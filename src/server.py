import logging

from flask import Flask, jsonify, request
from flask_cors import CORS
from google.protobuf import json_format

import src.scheduler_pb2 as scheduler_pb2
from src import schedule_generator

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
    force=True,
)
logger = logging.getLogger(__name__)
app = Flask(__name__)
# Allow cross-origin requests only from trusted domains.
TRUSTED_ORIGINS = [
    # Allow all subdomains of vercel.app and any paths beneath them.
    r".*\.vercel\.app.*"
]
CORS(app, origins=TRUSTED_ORIGINS)


def build_schedule_response(
    req: scheduler_pb2.ScheduleRequest,
) -> scheduler_pb2.ScheduleResponse:
    logger.info(
        (
            "GenerateSchedule request received with %d teams across %d divisions "
            "(in_division_play_twice=%s, out_of_division_play_once=%s, num_weeks=%d)"
        ),
        len(req.league),
        len({t.division_id for t in req.league} | {d.id for d in req.divisions}),
        req.options.in_division_play_twice,
        req.options.out_of_division_play_once,
        req.options.num_weeks if req.options.num_weeks else 13,
    )

    response = scheduler_pb2.ScheduleResponse()

    division_ids = {team.division_id for team in req.league}
    division_ids.update(div.id for div in req.divisions)
    if len(division_ids) not in (1, 2):
        raise ValueError("Only 1 or 2 divisions are currently supported")

    teams_sorted = sorted(list(req.league), key=lambda t: t.division_id)
    num_teams = len(teams_sorted)
    if num_teams == 0:
        logger.info("No teams provided in request")
        return response

    num_weeks = req.options.num_weeks or 13

    schedule_data = schedule_generator.generate_schedule(
        num_weeks,
        num_teams,
        req.options.in_division_play_twice,
        req.options.out_of_division_play_once,
    )

    if isinstance(schedule_data, str):
        logger.error("Schedule generation failed: %s", schedule_data)
        raise ValueError(schedule_data)

    schedule = {}
    for week_str, team1_idx, team2_idx in schedule_data[1:]:
        week = int(week_str)
        schedule.setdefault(week, []).append((int(team1_idx), int(team2_idx)))

    for week in range(max(schedule.keys()) + 1):
        weekly = response.matchups.add()
        for team1_idx, team2_idx in schedule.get(week, []):
            matchup = weekly.matchups.add()
            matchup.team1.CopyFrom(teams_sorted[team1_idx])
            matchup.team2.CopyFrom(teams_sorted[team2_idx])

    logger.info("Returning schedule response with %d weeks", len(response.matchups))
    return response


@app.get("/")
def root() -> tuple[str, int]:
    return "OK", 200


@app.get("/liveness_check")
@app.get("/readiness_check")
def health_check() -> tuple[str, int]:
    return "ok", 200


@app.post("/generate-schedule")
def generate_schedule_http():
    req_json = request.get_json(force=True)
    logger.debug("/generate-schedule body: %s", req_json)
    req_pb = json_format.ParseDict(req_json, scheduler_pb2.ScheduleRequest())
    try:
        resp_pb = build_schedule_response(req_pb)
        resp_dict = json_format.MessageToDict(
            resp_pb, preserving_proto_field_name=True
        )
        logger.debug("Returning response with %d weeks", len(resp_pb.matchups))
        return jsonify(resp_dict), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


def serve() -> None:
    """Run the built-in development server."""
    app.run(host="0.0.0.0", port=8080)


if __name__ == "__main__":
    serve()
