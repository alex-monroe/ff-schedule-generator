from concurrent import futures
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import grpc
from grpc_reflection.v1alpha import reflection

import src.scheduler_pb2 as scheduler_pb2
import src.scheduler_pb2_grpc as scheduler_pb2_grpc
from src import schedule_generator


logger = logging.getLogger(__name__)


class HealthHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for health and readiness checks."""

    def do_GET(self) -> None:  # noqa: D401 -- required method signature
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
        elif self.path in (
            "/liveness_check",
            "/readiness_check",
            "/_ah/liveness_check",
            "/_ah/readiness_check",
        ):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok")
        else:
            self.send_response(404)
            self.end_headers()


class SchedulerServicer(scheduler_pb2_grpc.SchedulerServicer):
    def GenerateSchedule(self, request, context):
        logger.info("GenerateSchedule request received with %d teams", len(request.league))

        response = scheduler_pb2.ScheduleResponse()

        # Determine how many unique divisions are present in the request. The
        # service currently only supports schedules for a single division or for
        # two divisions. Any other number of divisions is rejected.
        division_ids = {team.division_id for team in request.league}
        division_ids.update(div.id for div in request.divisions)
        if len(division_ids) not in (1, 2):
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Only 1 or 2 divisions are currently supported",
            )

        # Reorder teams so that all teams from the same division are contiguous
        # in the list passed to the solver. The solver expects the first half of
        # teams to belong to one division and the rest to another.
        teams_sorted = sorted(list(request.league), key=lambda t: t.division_id)

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
                # Map the solver indices back to the correct teams using the
                # sorted order used when invoking the solver.
                matchup.team1.CopyFrom(teams_sorted[team1_idx])
                matchup.team2.CopyFrom(teams_sorted[team2_idx])

        logger.info("Returning schedule response with %d weeks", len(response.matchups))

        return response


def serve():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
    )

    # Start HTTP health server on port 8080 in a separate thread
    httpd = HTTPServer(("0.0.0.0", 8080), HealthHandler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    logger.info("Health server started on port 8080")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    scheduler_pb2_grpc.add_SchedulerServicer_to_server(SchedulerServicer(), server)

    # Enable reflection
    SERVICE_NAMES = (
        scheduler_pb2.DESCRIPTOR.services_by_name["Scheduler"].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    server.add_insecure_port("0.0.0.0:50051")
    server.start()
    logger.info("Server started on port 50051 with reflection enabled")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
