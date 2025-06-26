.PHONY: install build run clean test

install:
	pip install -r requirements.txt

build:
	python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. scheduler.proto

run: build
	python3 server.py

clean:
	rm -f scheduler_pb2.py scheduler_pb2_grpc.py

test:
	PYTHONPATH=. python3 test_schedule_generator.py
