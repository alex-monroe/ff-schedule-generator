.PHONY: install build run clean test test-unit test-integration
SHELL := /bin/zsh

install:
	pip install -r requirements.txt

build:
	python3 -m grpc_tools.protoc -Isrc/protos --python_out=src --grpc_python_out=src src/protos/scheduler.proto

run: build
	PYTHONPATH=. python3 src/server.py

clean:
	rm -f src/scheduler_pb2.py src/scheduler_pb2_grpc.py
	find . -name __pycache__ -type d -exec rm -rf {} +


test: test-unit test-integration

test-unit:
	PYTHONPATH=src python3 -m unittest tests/test_schedule_generator.py

test-integration:
	PYTHONPATH=src python3 -m unittest tests/test_integration_schedule_generator.py
	PYTHONPATH=src python3 -m unittest tests/test_integration_server.py
