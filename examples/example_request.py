import argparse
import json
import urllib.request
import urllib.error
from google.protobuf import json_format
from src import scheduler_pb2


def build_request(num_teams: int) -> scheduler_pb2.ScheduleRequest:
    request = scheduler_pb2.ScheduleRequest()
    # Alternate teams between two divisions so ordering does not already match
    # the solver's expected grouping.
    for i in range(num_teams // 2):
        request.league.append(scheduler_pb2.Team(name=f"Division 0 Team {i+1}", division_id=0))
        request.league.append(scheduler_pb2.Team(name=f"Division 1 Team {i+1}", division_id=1))
    return request


def request_and_print(url: str, num_teams: int) -> None:
    """Request a schedule for ``num_teams`` and print it."""

    url = url.rstrip("/") + "/generate-schedule"
    request = build_request(num_teams)
    req_dict = json_format.MessageToDict(
        request, preserving_proto_field_name=True
    )
    data = json.dumps(req_dict).encode()
    http_req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(http_req) as resp:
        resp_data = json.load(resp)

    response = json_format.ParseDict(resp_data, scheduler_pb2.ScheduleResponse())

    print(f"Schedule for {num_teams} teams")
    for week_idx, weekly in enumerate(response.matchups, start=1):
        print(f"Week {week_idx}")
        for matchup in weekly.matchups:
            print(f"  {matchup.team1.name} vs {matchup.team2.name}")
    print()


def main(url: str = "https://ff-scheduler-466320.uw.r.appspot.com", teams: str = "10,8,12") -> None:
    """Send example schedule requests to the HTTP server."""

    for teams in [int(t) for t in teams.split(",")]:
        try:
            request_and_print(url, teams)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode()
            print(f"Request for {teams} teams failed: {body}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Send an example ScheduleRequest over HTTP"
    )
    parser.add_argument(
        "url",
        nargs="?",
        default="https://ff-scheduler-466320.uw.r.appspot.com",
        help="Base URL of the schedule service",
    )
    parser.add_argument(
        "--teams",
        default="10,8,12",
        help="Comma separated list of team counts to request",
    )
    args = parser.parse_args()
    main(args.url, args.teams)
