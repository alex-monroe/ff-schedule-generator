import logging

from flask import Flask, jsonify, request, send_from_directory
from google.protobuf import json_format

import src.scheduler_pb2 as scheduler_pb2
from src import schedule_generator

logger = logging.getLogger(__name__)
app = Flask(__name__, static_folder="static")


def build_schedule_response(
    req: scheduler_pb2.ScheduleRequest,
) -> scheduler_pb2.ScheduleResponse:
    logger.info("GenerateSchedule request received with %d teams", len(req.league))

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

    schedule_data = schedule_generator.generate_schedule(13, num_teams)

    if isinstance(schedule_data, str):
        logger.error("Schedule generation failed: %s", schedule_data)
        return response

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


@app.route("/")
def root():
    return app.send_static_file("index.html")


@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory("static", path)


@app.get("/liveness_check")
@app.get("/_ah/liveness_check")
@app.get("/readiness_check")
@app.get("/_ah/readiness_check")
def health_check() -> tuple[str, int]:
    return "ok", 200


@app.post("/generate-schedule")
def generate_schedule_http():
    req_json = request.get_json(force=True)
    req_pb = json_format.ParseDict(req_json, scheduler_pb2.ScheduleRequest())
    try:
        resp_pb = build_schedule_response(req_pb)
        resp_dict = json_format.MessageToDict(
            resp_pb, preserving_proto_field_name=True
        )
        return jsonify(resp_dict), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


def serve() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
    )
    app.run(host="0.0.0.0", port=8080)


if __name__ == "__main__":
    serve()
