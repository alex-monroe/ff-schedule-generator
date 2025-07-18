import nox


@nox.session(reuse_venv=True)
def build(session):
    session.install("grpcio-tools")
    session.run("python", "compile_protos.py")


@nox.session(reuse_venv=True)
def run(session):
    session.install("-r", "requirements.txt")
    session.run("python", "compile_protos.py")
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


@nox.session(reuse_venv=True)
def lint(session):
    """Run flake8 code linting."""
    session.install("-r", "requirements.txt")
    session.run(
        "flake8",
        "src",
        "tests",
        "examples",
        "noxfile.py",
        "--config=.flake8",
    )
