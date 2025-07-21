import os
import sys
import time
import unittest
import subprocess
import logging
import importlib
import shutil
import urllib.request

import grpc

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
        "50051:50051",
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
        _build_image()
        global scheduler_pb2, scheduler_pb2_grpc
        scheduler_pb2 = importlib.import_module("scheduler_pb2")
        scheduler_pb2_grpc = importlib.import_module("scheduler_pb2_grpc")
        logging.info("Launching gRPC server container for integration test")
        cls.proc = _run_container()
        # give the server some time to start
        time.sleep(1)
        logging.info("Server container started")

    @classmethod
    def tearDownClass(cls):
        logging.info("Stopping gRPC server container")
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
        channel = grpc.insecure_channel("localhost:50051")
        stub = scheduler_pb2_grpc.SchedulerStub(channel)

        request = scheduler_pb2.ScheduleRequest()
        # Create 10 teams split across two divisions but interleaved in the
        # request to ensure the server reorders them correctly.
        for i in range(5):
            request.league.append(scheduler_pb2.Team(name=f"Div1 Team {i+1}", division_id=1))
            request.league.append(scheduler_pb2.Team(name=f"Div0 Team {i+1}", division_id=0))

        response = stub.GenerateSchedule(request)
        logging.info("Received response with %d weeks", len(response.matchups))

        self.assertIsInstance(response, scheduler_pb2.ScheduleResponse)
        self.assertEqual(len(response.matchups), 13)
        for weekly in response.matchups:
            self.assertEqual(len(weekly.matchups), 5)

        channel.close()

    def test_health_endpoints(self):
        """Verify health and readiness endpoints return 200."""
        for path in ("liveness_check", "readiness_check"):
            url = f"http://localhost:8080/{path}"
            with urllib.request.urlopen(url) as resp:
                body = resp.read().decode()
                self.assertEqual(resp.getcode(), 200)
                self.assertEqual(body, "ok")

    def test_generate_schedule_invalid_divisions(self):
        """Requests with more than two divisions should return an error."""
        logging.info("Sending invalid GenerateSchedule request to server")
        channel = grpc.insecure_channel("localhost:50051")
        stub = scheduler_pb2_grpc.SchedulerStub(channel)

        request = scheduler_pb2.ScheduleRequest()
        # Create teams across three divisions to trigger the validation.
        for i in range(4):
            request.league.append(scheduler_pb2.Team(name=f"Div0 Team {i+1}", division_id=0))
        for i in range(3):
            request.league.append(scheduler_pb2.Team(name=f"Div1 Team {i+1}", division_id=1))
        for i in range(3):
            request.league.append(scheduler_pb2.Team(name=f"Div2 Team {i+1}", division_id=2))

        with self.assertRaises(grpc.RpcError) as cm:
            stub.GenerateSchedule(request)
        self.assertEqual(cm.exception.code(), grpc.StatusCode.INVALID_ARGUMENT)

        channel.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
    )
    unittest.main()
