import argparse
import json
import sys
import time
import urllib.error
import urllib.request

from google.protobuf import json_format

from src import scheduler_pb2


class ScheduleValidationError(RuntimeError):
    """Raised when the schedule response fails validation."""

    def __init__(self, message: str, response: dict) -> None:
        super().__init__(message)
        self.response = response


def build_request(num_teams: int) -> scheduler_pb2.ScheduleRequest:
    request = scheduler_pb2.ScheduleRequest()
    for i in range(num_teams // 2):
        request.league.append(
            scheduler_pb2.Team(name=f"Division 0 Team {i+1}", division_id=0)
        )
        request.league.append(
            scheduler_pb2.Team(name=f"Division 1 Team {i+1}", division_id=1)
        )
    request.options.in_division_play_twice = True
    request.options.out_of_division_play_once = True
    request.options.num_weeks = 13
    return request


def request_schedule(url: str, num_teams: int) -> tuple[dict, float]:
    """Request a schedule and validate the response."""

    url = url.rstrip("/") + "/generate-schedule"

    request = build_request(num_teams)
    req_dict = json_format.MessageToDict(
        request, preserving_proto_field_name=True
    )
    data = json.dumps(req_dict).encode()
    http_req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )

    start = time.perf_counter()
    with urllib.request.urlopen(http_req) as resp:
        body = resp.read()
    duration = time.perf_counter() - start

    try:
        resp_data = json.loads(body)
    except json.JSONDecodeError as exc:  # pragma: no cover - validation
        raise ScheduleValidationError(
            "Response was not valid JSON",
            {"raw": body.decode()},
        ) from exc

    response = json_format.ParseDict(resp_data, scheduler_pb2.ScheduleResponse())

    if len(response.matchups) != 13:
        raise ScheduleValidationError(
            f"Expected 13 weeks of matchups, got {len(response.matchups)}",
            resp_data,
        )
    for weekly in response.matchups:
        if len(weekly.matchups) != num_teams // 2:
            raise ScheduleValidationError(
                "Each week should contain the expected number of matchups, "
                f"got {len(weekly.matchups)}",
                resp_data,
            )

    return resp_data, duration


def main(url: str, num_teams: int) -> None:
    try:
        resp_data, duration = request_schedule(url, num_teams)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode()
        print(f"Request failed: {body}", file=sys.stderr)
        sys.exit(1)
    except ScheduleValidationError as exc:  # pragma: no cover - sanity check
        print(f"Request failed: {exc}", file=sys.stderr)
        print(json.dumps(exc.response), file=sys.stderr)
        sys.exit(1)

    print(f"Schedule received in {duration:.2f}s")
    print(json.dumps(resp_data))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Send a schedule request for smoke testing",
    )
    parser.add_argument(
        "url",
        nargs="?",
        default="http://127.0.0.1:8080",
        help="Base URL of the schedule service",
    )
    parser.add_argument(
        "--teams",
        type=int,
        default=10,
        help="Number of teams to request a schedule for",
    )
    args = parser.parse_args()
    main(args.url, args.teams)
