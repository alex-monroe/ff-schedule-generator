from concurrent import futures
import logging
import csv
import io

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

        num_teams = len(request.league)
        if num_teams == 0:
            logger.info("No teams provided, returning empty schedule")
            return scheduler_pb2.ScheduleResponse()

        # Generate the schedule CSV using the existing generator
        csv_output = schedule_generator.generate_schedule_csv(13, num_teams)

        # Parse the CSV into the gRPC response
        weeks: list[scheduler_pb2.WeeklyMatchups] = []
        reader = csv.reader(io.StringIO(csv_output))
        next(reader, None)  # skip header
        for row in reader:
            week_idx = int(row[0])
            team1_idx = int(row[1])
            team2_idx = int(row[2])

            while len(weeks) <= week_idx:
                weeks.append(scheduler_pb2.WeeklyMatchups())

            matchup = scheduler_pb2.Matchup(
                team1=request.league[team1_idx],
                team2=request.league[team2_idx],
            )
            weeks[week_idx].matchups.append(matchup)

        response = scheduler_pb2.ScheduleResponse(matchups=weeks)
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
