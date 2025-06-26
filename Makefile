.PHONY: install build run clean test

install:
	pip install -r requirements.txt

build:
	python3 -m grpc_tools.protoc -Isrc/protos --python_out=src --grpc_python_out=src src/protos/scheduler.proto

run: build
	PYTHONPATH=. python3 src/server.py

clean:
	rm -f src/scheduler_pb2.py src/scheduler_pb2_grpc.py

test:
	PYTHONPATH=src python3 -m unittest tests/test_schedule_generator.py
