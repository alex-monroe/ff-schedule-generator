# Fantasy Football Schedule Generator

This project contains a gRPC server for generating fantasy football schedules.

## Installation

To install the necessary Python dependencies, run the following command:

```bash
pip install -r requirements.txt
```

Or, if you have `make` installed:

```bash
make install
```

## Build

The server uses gRPC for communication, with the service interface defined in `scheduler.proto`. Before running the server, you need to compile the protobuf file to generate the Python gRPC code.

```bash
make build
```

This will create `scheduler_pb2.py` and `scheduler_pb2_grpc.py` in the project root.

## Running the Server

To run the gRPC server, use the following command:

```bash
make run
```

The server will start on port `50051`.

## Example Request

After starting the server, you can send a gRPC request to it using Python. The snippet below builds a `ScheduleRequest` with ten teams and prints the generated schedule.

```python
import grpc
import scheduler_pb2
import scheduler_pb2_grpc

channel = grpc.insecure_channel('localhost:50051')
stub = scheduler_pb2_grpc.SchedulerStub(channel)

request = scheduler_pb2.ScheduleRequest()
for i in range(10):
    team = scheduler_pb2.Team(name=f'Team {i+1}', division_id=0)
    request.league.append(team)

response = stub.GenerateSchedule(request)
print(response)
```

Ensure the protobuf files are built (`make build`) so that `scheduler_pb2` and `scheduler_pb2_grpc` are available before running the snippet.

You can also run the example script in `examples/example_request.py` to see the
same request in action:

```bash
make build
python examples/example_request.py
```
