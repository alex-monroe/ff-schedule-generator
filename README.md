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

The server will start on port `50051`
