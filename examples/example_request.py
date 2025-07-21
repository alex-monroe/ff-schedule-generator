import argparse
import json
import urllib.request
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


def main(host: str = "localhost") -> None:
    """Send an example schedule request to the HTTP server."""

    url = f"http://{host}:8080/generate-schedule"
    request = build_request(10)
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
        help="IP or hostname of the running HTTP server (default: localhost)",
    )
    args = parser.parse_args()
    main(args.host)
