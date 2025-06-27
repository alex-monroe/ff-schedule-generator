from concurrent import futures
import logging
import grpc
from grpc_reflection.v1alpha import reflection

import src.scheduler_pb2 as scheduler_pb2
import src.scheduler_pb2_grpc as scheduler_pb2_grpc
from src import schedule_generator


logger = logging.getLogger(__name__)

class SchedulerServicer(scheduler_pb2_grpc.SchedulerServicer):
    def GenerateSchedule(self, request, context):
        logger.info(
            "GenerateSchedule request received with %d teams", len(request.league)
        )

        response = scheduler_pb2.ScheduleResponse()

        num_teams = len(request.league)
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
                matchup.team1.CopyFrom(request.league[team1_idx])
                matchup.team2.CopyFrom(request.league[team2_idx])

        logger.info(
            "Returning schedule response with %d weeks", len(response.matchups)
        )

        return response

def serve():
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
    )

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    scheduler_pb2_grpc.add_SchedulerServicer_to_server(SchedulerServicer(), server)

    # Enable reflection
    SERVICE_NAMES = (
        scheduler_pb2.DESCRIPTOR.services_by_name['Scheduler'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info("Server started on port 50051 with reflection enabled")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
