import os
import sys
import time
import unittest
import subprocess
from multiprocessing import Process

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
    server.serve()


class TestServerIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proc = Process(target=_run_server)
        cls.proc.start()
        # give the server some time to start
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        cls.proc.join()

    def test_generate_schedule_default_response(self):
        channel = grpc.insecure_channel('localhost:50051')
        stub = scheduler_pb2_grpc.SchedulerStub(channel)
        response = stub.GenerateSchedule(scheduler_pb2.ScheduleRequest())
        self.assertIsInstance(response, scheduler_pb2.ScheduleResponse)
        self.assertEqual(len(response.matchups), 0)
        channel.close()


if __name__ == '__main__':
    unittest.main()
