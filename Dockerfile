FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only source code and protos
COPY src ./src

# Compile protobufs
COPY compile_protos.py ./
RUN python compile_protos.py

# Set PYTHONPATH so the server can find the generated modules
ENV PYTHONPATH=/app

EXPOSE 50051

CMD ["python", "src/server.py"]
