import nox

@nox.session(reuse_venv=True)
def build(session):
    session.install("grpcio-tools")
    session.run(
        "python",
        "-m",
        "grpc_tools.protoc",
        "-Isrc/protos",
        "--python_out=src",
        "--grpc_python_out=src",
        "src/protos/scheduler.proto",
    )

@nox.session(reuse_venv=True)
def run(session):
    session.install("-r", "requirements.txt")
    session.run(
        "python",
        "-m",
        "grpc_tools.protoc",
        "-Isrc/protos",
        "--python_out=src",
        "--grpc_python_out=src",
        "src/protos/scheduler.proto",
    )
    session.run(
        "python",
        "src/server.py",
        env={"PYTHONPATH": "."},
    )

@nox.session(reuse_venv=True)
def test_unit(session):
    session.install("-r", "requirements.txt")
    session.run(
        "python",
        "-m",
        "unittest",
        "tests/test_schedule_generator.py",
        env={"PYTHONPATH": "src"},
    )

@nox.session(reuse_venv=True)
def test_integration(session):
    session.install("-r", "requirements.txt")
    session.run(
        "python",
        "-m",
        "unittest",
        "tests/test_integration_schedule_generator.py",
        "tests/test_integration_server.py",
        env={"PYTHONPATH": "src"},
    )

@nox.session(reuse_venv=True)
def tests(session):
    session.notify("test_unit")
    session.notify("test_integration")
