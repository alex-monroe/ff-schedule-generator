FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only source code and protos
COPY src ./src

# Compile protobufs
RUN python -m grpc_tools.protoc -Isrc/protos --python_out=src --grpc_python_out=src src/protos/scheduler.proto

# Set PYTHONPATH so the server can find the generated modules
ENV PYTHONPATH=/app

EXPOSE 50051

CMD ["python", "src/server.py"]
