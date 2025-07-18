# Fantasy Football Schedule Generator

This project contains a gRPC server for generating fantasy football schedules.

## Installation

To install the necessary Python dependencies, run the following commands:

```bash
pip install -r requirements.txt
pip install nox
```

## Build

The server uses gRPC for communication. All protobuf definitions in `src/protos` must be compiled before the server can run. A helper script `compile_protos.py` handles this for every `.proto` file found in that directory.

```bash
nox -s build
```

This will create the generated `_pb2.py` files next to your source code. You can also run `python compile_protos.py` directly if you prefer not to use Nox.

## Running the Server

To run the gRPC server, use the following command:

```bash
nox -s run
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

Ensure the protobuf files are built (`nox -s build`) so that `scheduler_pb2` and `scheduler_pb2_grpc` are available before running the snippet.

You can also run the example script in `examples/example_request.py` to see the
same request in action:

```bash
nox -s build
PYTHONPATH=.:src python examples/example_request.py
```

## Docker

A `Dockerfile` is provided for building the server into a container image. A
`.dockerignore` file excludes development artifacts so the image stays small.
Build the image and run it locally with:

```bash
docker build -t schedule-server .
docker run -p 50051:50051 schedule-server
```

The image compiles the protobuf definitions during build and starts the gRPC server on port `50051`.
The `compile_protos.py` script is copied into the image so that any new `.proto` files will be included automatically.
