import os
import sys
import time
import unittest
import subprocess
from multiprocessing import Process
import logging

import grpc

# Compile protobuf definitions before importing the server
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
subprocess.check_call([
    sys.executable,
    '-m', 'grpc_tools.protoc',
    '-Isrc/protos',
    '--python_out=src',
    '--grpc_python_out=src',
    'src/protos/scheduler.proto'
], cwd=ROOT_DIR)

import scheduler_pb2
import scheduler_pb2_grpc
import server


def _run_server():
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
    )
    logging.info("Starting server in subprocess for integration test")
    server.serve()


class TestServerIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
        )
        logging.info("Launching gRPC server process for integration test")
        cls.proc = Process(target=_run_server)
        cls.proc.start()
        # give the server some time to start
        time.sleep(1)
        logging.info("Server process started")

    @classmethod
    def tearDownClass(cls):
        logging.info("Terminating gRPC server process")
        cls.proc.terminate()
        cls.proc.join()
        logging.info("Server process terminated")

    def test_generate_schedule_default_response(self):
        logging.info("Sending GenerateSchedule request to server")
        channel = grpc.insecure_channel('localhost:50051')
        stub = scheduler_pb2_grpc.SchedulerStub(channel)
        response = stub.GenerateSchedule(scheduler_pb2.ScheduleRequest())
        logging.info("Received response with %d matchups", len(response.matchups))
        self.assertIsInstance(response, scheduler_pb2.ScheduleResponse)
        self.assertEqual(len(response.matchups), 0)
        channel.close()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
    )
    unittest.main()
