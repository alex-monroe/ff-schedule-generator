.PHONY: install build run clean test test-unit test-integration

install:
	pip install -r requirements.txt

build:
	python3 -m grpc_tools.protoc -Isrc/protos --python_out=src --grpc_python_out=src src/protos/scheduler.proto

run: build
	PYTHONPATH=. python3 src/server.py

clean:
	rm -f src/scheduler_pb2.py src/scheduler_pb2_grpc.py

test: test-unit test-integration

test-unit:
	PYTHONPATH=src python3 -m unittest tests/test_schedule_generator.py

test-integration:
	PYTHONPATH=src python3 -m unittest \
	tests/test_integration_schedule_generator.py \
	tests/test_integration_server.py
