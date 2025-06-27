from concurrent import futures
import csv

import grpc
from grpc_reflection.v1alpha import reflection

from src import schedule_generator
import src.scheduler_pb2 as scheduler_pb2
import src.scheduler_pb2_grpc as scheduler_pb2_grpc

class SchedulerServicer(scheduler_pb2_grpc.SchedulerServicer):
    def GenerateSchedule(self, request, context):
        num_teams = len(request.league)

        # If no teams were provided simply return an empty response
        if num_teams == 0:
            return scheduler_pb2.ScheduleResponse()

        csv_output = schedule_generator.generate_schedule_csv(13, num_teams)
        lines = csv_output.strip().splitlines()

        # Mapping from team index in the solver output to the Team message from
        # the request.  The schedule generator uses zero based indices.
        teams = list(request.league)

        weekly = {}
        try:
            reader = csv.DictReader(lines)
            for row in reader:
                week = int(row["Week"])
                t1 = teams[int(row["Team1"])]
                t2 = teams[int(row["Team2"])]

                weekly.setdefault(week, scheduler_pb2.WeeklyMatchups())
                weekly[week].matchups.append(
                    scheduler_pb2.Matchup(team1=t1, team2=t2)
                )
        except (csv.Error, KeyError, ValueError) as e:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Malformed CSV data: {e}")

        response = scheduler_pb2.ScheduleResponse()
        for week in sorted(weekly.keys()):
            response.matchups.append(weekly[week])

        return response

def serve():
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
    print("Server started on port 50051 with reflection enabled")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
