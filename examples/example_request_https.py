import argparse
import json
import sys
import urllib.request
import urllib.error

from google.protobuf import json_format

from src import scheduler_pb2


def build_request(num_teams: int) -> scheduler_pb2.ScheduleRequest:
    request = scheduler_pb2.ScheduleRequest()
    for i in range(num_teams // 2):
        request.league.append(
            scheduler_pb2.Team(name=f"Division 0 Team {i+1}", division_id=0)
        )
        request.league.append(
            scheduler_pb2.Team(name=f"Division 1 Team {i+1}", division_id=1)
        )
    request.in_division_play_twice = True
    request.out_of_division_play_once = True
    return request


def request_and_check(url: str, num_teams: int) -> None:
    """Request a schedule and perform basic sanity checks."""

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
        if resp.getcode() != 200:
            raise AssertionError(f"Unexpected status code {resp.getcode()}")
        resp_data = json.load(resp)

    response = json_format.ParseDict(resp_data, scheduler_pb2.ScheduleResponse())

    if len(response.matchups) != 13:
        raise AssertionError(
            f"Expected 13 weeks of matchups, got {len(response.matchups)}"
        )
    for weekly in response.matchups:
        if len(weekly.matchups) != num_teams // 2:
            raise AssertionError(
                "Each week should contain the expected number of matchups, "
                f"got {len(weekly.matchups)}"
            )

    print(f"Server returned schedule for {num_teams} teams")


def main(url: str = "https://ff-scheduler-466320.uw.r.appspot.com", teams: str = "10") -> None:
    """Send requests to the deployed server and verify the responses."""

    for num in [int(t) for t in teams.split(",")]:
        try:
            request_and_check(url, num)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode()
            print(f"Request for {num} teams failed: {body}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Send an example ScheduleRequest to the HTTPS service"
    )
    parser.add_argument(
        "url",
        nargs="?",
        default="https://ff-scheduler-466320.uw.r.appspot.com",
        help="Base URL of the schedule service",
    )
    parser.add_argument(
        "--teams",
        default="10",
        help="Comma separated list of team counts to request",
    )
    args = parser.parse_args()
    try:
        main(args.url, args.teams)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Test failed: {exc}", file=sys.stderr)
        sys.exit(1)
