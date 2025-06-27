import unittest
from pathlib import Path
import subprocess

# Compile the protobuf definitions for the tests
proto_dir = Path(__file__).resolve().parents[1] / 'src' / 'protos'
proto_file = proto_dir / 'scheduler.proto'
subprocess.run([
    'python3', '-m', 'grpc_tools.protoc',
    f'-I{proto_dir}',
    f'--python_out={proto_dir.parent}',
    f'--grpc_python_out={proto_dir.parent}',
    str(proto_file)
], check=True)

import server
import scheduler_pb2 as pb2

class TestSchedulerServerIntegration(unittest.TestCase):
    def setUp(self):
        self.servicer = server.SchedulerServicer()

    def _build_request(self, num_teams):
        request = pb2.ScheduleRequest()
        for i in range(num_teams):
            team = pb2.Team(name=f'Team {i}', division_id=0)
            request.league.append(team)
        return request

    def test_generate_schedule_uses_request_team_count(self):
        num_teams = 10
        request = self._build_request(num_teams)
        response = self.servicer.GenerateSchedule(request, None)

        self.assertEqual(len(response.matchups), 13)
        for weekly in response.matchups:
            self.assertEqual(len(weekly.matchups), num_teams // 2)

if __name__ == '__main__':
    unittest.main()
