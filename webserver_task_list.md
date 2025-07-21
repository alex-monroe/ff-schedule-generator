# Web Server Refactor Task List

This checklist outlines the steps required to convert the existing gRPC server into an HTTP web server while continuing to use the protobuf definitions for request and response formats.

## Phase 1: Setup and Dependencies
- [ ] **Investigate HTTP Framework**
  - Evaluate frameworks such as **FastAPI** or **Flask** for implementing the new server.
- [ ] **Add Web Dependencies**
  - Update `requirements.txt` and `noxfile.py` with any required libraries (e.g., `fastapi`, `uvicorn`).

## Phase 2: Protobuf Integration
- [ ] **Compile Protos**
  - Continue using `compile_protos.py` to generate `*_pb2.py` files.
- [ ] **JSON Conversion Helpers**
  - Utilize `google.protobuf.json_format` to translate between JSON payloads and protobuf messages.

## Phase 3: HTTP Server Implementation
- [ ] **Create Server Module**
  - Replace `grpc.server` usage with an HTTP framework.
  - Implement an endpoint such as `POST /generate_schedule` that accepts a JSON body matching `ScheduleRequest`.
- [ ] **Return Protobuf Response**
  - Convert the generated `ScheduleResponse` message to JSON and return it with status code `200`.
- [ ] **Preserve Health Endpoints**
  - Keep `/`, `/liveness_check`, and `/readiness_check` routes returning the same responses.

## Phase 4: Tests and Tooling
- [ ] **Update Unit Tests**
  - Write tests for the new HTTP handlers using the existing protobuf messages for input/output validation.
- [ ] **Adjust Integration Tests**
  - Replace gRPC client calls with HTTP requests and verify JSON responses.
- [ ] **Update Nox Sessions**
  - Modify the `run` and test sessions to install web dependencies and start the HTTP server.

## Phase 5: Documentation and Deployment
- [ ] **Update Dockerfile**
  - Expose the appropriate HTTP port and adjust the command to run the new server.
- [ ] **Revise README**
  - Document how to start the web server and send example HTTP requests.
- [ ] **Describe Migration Notes**
  - Explain that protobuf models still define request and response schemas even though communication is now HTTP-based.

