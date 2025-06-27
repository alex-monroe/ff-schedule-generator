import sys
from pathlib import Path

# Ensure the generated gRPC modules are on the path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import grpc
import scheduler_pb2
import scheduler_pb2_grpc


def build_request(num_teams: int) -> scheduler_pb2.ScheduleRequest:
    request = scheduler_pb2.ScheduleRequest()
    # Alternate teams between two divisions so ordering does not already match
    # the solver's expected grouping.
    for i in range(num_teams // 2):
        request.league.append(scheduler_pb2.Team(name=f"Division 0 Team {i+1}", division_id=0))
        request.league.append(scheduler_pb2.Team(name=f"Division 1 Team {i+1}", division_id=1))
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
