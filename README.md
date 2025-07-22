# Fantasy Football Schedule Generator

This project contains an HTTP server for generating fantasy football schedules.

## Installation

To install the necessary Python dependencies, run the following commands:

```bash
pip install -r requirements.txt
pip install nox
```

## Build

The API exchanges JSON payloads, but request and response schemas are defined
by protobuf. All definitions in `src/protos` must be compiled before the server
can run. A helper script `compile_protos.py` handles this for every `.proto`
file found in that directory.

```bash
nox -s build
```

This will create the generated `_pb2.py` files next to your source code. You can also run `python compile_protos.py` directly if you prefer not to use Nox.

## Running the Server

To run the HTTP server, use the following command:

```bash
nox -s run
```

The server listens on port `8080` and exposes health endpoints used by GCP App Engine:

* `/liveness_check`
* `/readiness_check`

Both endpoints return `200 OK` with the body `"ok"`.

Cross-Origin Resource Sharing (CORS) is enabled so browser-based clients can
request schedules from trusted domains. Requests originating from `*.vercel.app`
or any domain containing `google` or `gcp` are allowed.

## Example Request

After starting the server, you can send an HTTP request to it using Python. The
snippet below builds a `ScheduleRequest` with ten teams and prints the generated
schedule.

```python
import json
import urllib.request
from google.protobuf import json_format
import scheduler_pb2

request = scheduler_pb2.ScheduleRequest()
for i in range(10):
    team = scheduler_pb2.Team(name=f'Team {i+1}', division_id=0)
    request.league.append(team)

req_dict = json_format.MessageToDict(request, preserving_proto_field_name=True)
data = json.dumps(req_dict).encode()
http_req = urllib.request.Request(
    'https://ff-scheduler-466320.uw.r.appspot.com/generate-schedule',
    data=data,
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(http_req) as resp:
    response_data = json.load(resp)

print(response_data)
```

Ensure the protobuf files are built (`nox -s build`) so that `scheduler_pb2` is
available before running the snippet.

You can also run the example script in `examples/example_request.py` to see the
same request in action against the hosted API:

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
docker run -p 8080:8080 schedule-server
```

The image compiles the protobuf definitions during build and starts the HTTP server on port `8080`.
The `compile_protos.py` script is copied into the image so that any new `.proto` files will be included automatically.

## Deployment Smoke Test

A GitHub Actions workflow runs `examples/example_request_https.py` after each deployment and once a day to verify that the production server responds correctly. The script sends a simple schedule request and checks that the response contains 13 weeks with five matchups per week.
