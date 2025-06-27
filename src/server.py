from concurrent import futures
import grpc
from grpc_reflection.v1alpha import reflection

import csv

import src.schedule_generator as schedule_generator
import src.scheduler_pb2 as scheduler_pb2
import src.scheduler_pb2_grpc as scheduler_pb2_grpc

class SchedulerServicer(scheduler_pb2_grpc.SchedulerServicer):
    """gRPC servicer that generates schedules."""

    def GenerateSchedule(self, request, context):
        """Generate a schedule based on the incoming request."""
        num_teams = len(request.league)

        # Keep the number of weeks pegged to 13 for now. Only the number of
        # teams varies based on the request.
        num_weeks = 13

        csv_schedule = schedule_generator.generate_schedule_csv(num_weeks, num_teams)

        # csv_schedule is returned as a CSV string with columns Week,Team1,Team2
        reader = csv.reader(csv_schedule.strip().splitlines())
        next(reader, None)  # skip header

        matchups_by_week = {}
        for row in reader:
            week = int(row[0])
            team1_index = int(row[1])
            team2_index = int(row[2])
            matchups_by_week.setdefault(week, []).append((team1_index, team2_index))

        response = scheduler_pb2.ScheduleResponse()
        for week in sorted(matchups_by_week.keys()):
            weekly = scheduler_pb2.WeeklyMatchups()
            for team1_idx, team2_idx in matchups_by_week[week]:
                matchup = scheduler_pb2.Matchup()
                matchup.team1.CopyFrom(request.league[team1_idx])
                matchup.team2.CopyFrom(request.league[team2_idx])
                weekly.matchups.append(matchup)
            response.matchups.append(weekly)

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
