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

This will create the generated `_pb2.py` files next to your source code. You can
also run `python compile_protos.py` directly if you prefer not to use Nox. The
script exposes a `main()` function, so it can be imported and called from other
Python code as `compile_protos.main()`.

## Running the Server

For production-style runs the application is served by Gunicorn. Start it
directly with:

```bash
gunicorn src.server:app -b 0.0.0.0:8080
```

The `serve()` helper in `src/server.py` still uses Flask's built-in
development server for quick local testing and is invoked by:

```bash
nox -s run
```

Both methods listen on port `8080` and expose health endpoints:

* `/liveness_check`
* `/readiness_check`

Both endpoints return `200 OK` with the body `"ok"`.

Cross-Origin Resource Sharing (CORS) is enabled so browser-based clients can
request schedules from trusted domains. Requests originating from `*.vercel.app`
(including any paths under those subdomains) are allowed.

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
    'http://127.0.0.1:8080/generate-schedule',
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
same request in action against the server:

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

The image compiles the protobuf definitions during build and serves the app via
Gunicorn on port `8080`. The `compile_protos.py` script is copied into the image
so that any new `.proto` files will be included automatically.

