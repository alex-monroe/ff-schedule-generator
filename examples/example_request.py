import sys
from pathlib import Path

# Ensure the generated gRPC modules are on the path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import grpc
import scheduler_pb2
import scheduler_pb2_grpc


def build_request(num_teams: int) -> scheduler_pb2.ScheduleRequest:
    request = scheduler_pb2.ScheduleRequest()
    for i in range(num_teams):
        team = scheduler_pb2.Team(name=f"Team {i+1}", division_id=0)
        request.league.append(team)
    return request


def main() -> None:
    channel = grpc.insecure_channel("localhost:50051")
    stub = scheduler_pb2_grpc.SchedulerStub(channel)

    request = build_request(10)
    response = stub.GenerateSchedule(request)

    for week_idx, weekly in enumerate(response.matchups, start=1):
        print(f"Week {week_idx}")
        for matchup in weekly.matchups:
            print(f"  {matchup.team1.name} vs {matchup.team2.name}")


if __name__ == "__main__":
    main()

