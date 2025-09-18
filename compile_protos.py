from pathlib import Path
from grpc_tools import protoc


def main() -> None:
    """Compile all protobuf definitions in ``src/protos``."""

    PROTO_DIR = Path("src/protos")
    OUT_DIR = Path("src")

    proto_files = [str(p) for p in PROTO_DIR.glob("*.proto")]

    if not proto_files:
        raise SystemExit("No .proto files found")

    protoc_args = [
        "grpc_tools.protoc",
        f"-I{PROTO_DIR}",
        f"--python_out={OUT_DIR}",
        f"--grpc_python_out={OUT_DIR}",
    ] + proto_files

    protoc.main(protoc_args)


if __name__ == "__main__":
    main()
