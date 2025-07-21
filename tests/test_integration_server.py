import os
import sys
import time
import unittest
import subprocess
import logging
import importlib
import shutil
import urllib.request
import urllib.error

import json
from google.protobuf import json_format

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCKER_IMAGE = "schedule-server:test"
CONTAINER_NAME = "schedule-server-test"


def _compile_protos() -> None:
    """Compile protobuf definitions for the tests."""
    subprocess.check_call([
        sys.executable,
        "compile_protos.py",
    ], cwd=ROOT_DIR)


def _build_image() -> None:
    """Build the Docker image for the server used in tests if needed."""
    try:
        subprocess.check_call(
            ["docker", "image", "inspect", DOCKER_IMAGE],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=ROOT_DIR,
        )
        logging.info("Docker image %s already present", DOCKER_IMAGE)
        return
    except subprocess.CalledProcessError:
        pass

    logging.info("Building Docker image %s", DOCKER_IMAGE)
    subprocess.check_call([
        "docker",
        "build",
        "-t",
        DOCKER_IMAGE,
        ".",
    ], cwd=ROOT_DIR)


def _run_container() -> subprocess.Popen:
    """Run the server container and return the subprocess handle."""
    return subprocess.Popen([
        "docker",
        "run",
        "--name",
        CONTAINER_NAME,
        "-p",
        "8080:8080",
        "--rm",
        DOCKER_IMAGE,
    ], cwd=ROOT_DIR)


class TestServerIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        )
        if shutil.which("docker") is None:
            raise unittest.SkipTest("docker command not available")

        _compile_protos()
        # Add the generated protobuf code to the path
        sys.path.append(os.path.join(ROOT_DIR, "src"))
        _build_image()
        global scheduler_pb2
        scheduler_pb2 = importlib.import_module("scheduler_pb2")
        logging.info("Launching HTTP server container for integration test")
        cls.proc = _run_container()
        # give the server some time to start
        time.sleep(1)
        logging.info("Server container started")

    @classmethod
    def tearDownClass(cls):
        logging.info("Stopping server container")
        subprocess.run(
            ["docker", "stop", CONTAINER_NAME],
            cwd=ROOT_DIR,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            cls.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            cls.proc.kill()
            cls.proc.wait()
        logging.info("Server container terminated")

    def test_generate_schedule_returns_matchups(self):
        logging.info("Sending GenerateSchedule request to server")
        request = scheduler_pb2.ScheduleRequest()
        # Create 10 teams split across two divisions but interleaved in the
        # request to ensure the server reorders them correctly.
        for i in range(5):
            request.league.append(scheduler_pb2.Team(name=f"Div1 Team {i+1}", division_id=1))
            request.league.append(scheduler_pb2.Team(name=f"Div0 Team {i+1}", division_id=0))
        url = "http://127.0.0.1:8080/generate-schedule"
        req_dict = json_format.MessageToDict(
            request, preserving_proto_field_name=True
        )
        data = json.dumps(req_dict).encode()
        http_req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(http_req) as resp:
            self.assertEqual(resp.getcode(), 200)
            resp_data = json.load(resp)

        response = json_format.ParseDict(resp_data, scheduler_pb2.ScheduleResponse())
        logging.info("Received response with %d weeks", len(response.matchups))

        self.assertIsInstance(response, scheduler_pb2.ScheduleResponse)
        self.assertEqual(len(response.matchups), 13)
        for weekly in response.matchups:
            self.assertEqual(len(weekly.matchups), 5)

    def test_health_endpoints(self):
        """Verify health and readiness endpoints return 200."""
        for path in ("liveness_check", "readiness_check"):
            url = f"http://127.0.0.1:8080/{path}"
            with urllib.request.urlopen(url) as resp:
                body = resp.read().decode()
                self.assertEqual(resp.getcode(), 200)
                self.assertEqual(body, "ok")

    def test_root_path_returns_ok(self):
        """Verify the root path returns a 200 OK."""
        url = "http://127.0.0.1:8080/"
        with urllib.request.urlopen(url) as resp:
            body = resp.read().decode()
            self.assertEqual(resp.getcode(), 200)
            self.assertEqual(body, "OK")

    def test_generate_schedule_invalid_divisions(self):
        """Requests with more than two divisions should return an error."""
        logging.info("Sending invalid GenerateSchedule request to server")
        request = scheduler_pb2.ScheduleRequest()
        # Create teams across three divisions to trigger the validation.
        for i in range(4):
            request.league.append(scheduler_pb2.Team(name=f"Div0 Team {i+1}", division_id=0))
        for i in range(3):
            request.league.append(scheduler_pb2.Team(name=f"Div1 Team {i+1}", division_id=1))
        for i in range(3):
            request.league.append(scheduler_pb2.Team(name=f"Div2 Team {i+1}", division_id=2))
        url = "http://127.0.0.1:8080/generate-schedule"
        req_dict = json_format.MessageToDict(
            request, preserving_proto_field_name=True
        )
        data = json.dumps(req_dict).encode()
        http_req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(http_req)

        self.assertEqual(cm.exception.code, 400)
        body = json.loads(cm.exception.read().decode())
        self.assertIn("error", body)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
    )
    unittest.main()
