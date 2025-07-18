import argparse
import urllib.parse
import grpc
from src import scheduler_pb2
from src import scheduler_pb2_grpc


def build_request(num_teams: int) -> scheduler_pb2.ScheduleRequest:
    request = scheduler_pb2.ScheduleRequest()
    for i in range(num_teams // 2):
        request.league.append(
            scheduler_pb2.Team(name=f"Division 0 Team {i+1}", division_id=0)
        )
        request.league.append(
            scheduler_pb2.Team(name=f"Division 1 Team {i+1}", division_id=1)
        )
    return request


def main(url: str) -> None:
    """Send an example schedule request to a deployed server via HTTPS."""
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc or parsed.path
    target = f"{host}:443"
    channel = grpc.secure_channel(target, grpc.ssl_channel_credentials())
    stub = scheduler_pb2_grpc.SchedulerStub(channel)

    request = build_request(10)
    response = stub.GenerateSchedule(request)

    for week_idx, weekly in enumerate(response.matchups, start=1):
        print(f"Week {week_idx}")
        for matchup in weekly.matchups:
            print(f"  {matchup.team1.name} vs {matchup.team2.name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send an example ScheduleRequest over HTTPS")
    parser.add_argument(
        "url",
        nargs="?",
        default="https://ff-scheduler-466320.uw.r.appspot.com",
        help="Full HTTPS URL of the deployed API",
    )
    args = parser.parse_args()
    main(args.url)
