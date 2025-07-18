import argparse
import grpc
from src import scheduler_pb2
from src import scheduler_pb2_grpc


def build_request(num_teams: int) -> scheduler_pb2.ScheduleRequest:
    request = scheduler_pb2.ScheduleRequest()
    # Alternate teams between two divisions so ordering does not already match
    # the solver's expected grouping.
    for i in range(num_teams // 2):
        request.league.append(scheduler_pb2.Team(name=f"Division 0 Team {i+1}", division_id=0))
        request.league.append(scheduler_pb2.Team(name=f"Division 1 Team {i+1}", division_id=1))
    return request


def main(host: str = "localhost") -> None:
    """Send an example schedule request to the server."""

    channel = grpc.insecure_channel(f"{host}:50051")
    stub = scheduler_pb2_grpc.SchedulerStub(channel)

    request = build_request(10)
    response = stub.GenerateSchedule(request)

    for week_idx, weekly in enumerate(response.matchups, start=1):
        print(f"Week {week_idx}")
        for matchup in weekly.matchups:
            print(f"  {matchup.team1.name} vs {matchup.team2.name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send an example ScheduleRequest")
    parser.add_argument(
        "host",
        nargs="?",
        default="localhost",
        help="IP or hostname of the running gRPC server (default: localhost)",
    )
    args = parser.parse_args()
    main(args.host)
