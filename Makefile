.PHONY: install build run clean

install:
	pip install -r requirements.txt

build:
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. scheduler.proto

run: build
	python server.py

clean:
	rm -f scheduler_pb2.py scheduler_pb2_grpc.py
