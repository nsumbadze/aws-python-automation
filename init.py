from pathlib import Path
import platform
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
ENV_PATH = ROOT / ".env"
ENV_EXAMPLE_PATH = ROOT / ".env.example"


def prompt(message: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default is not None else ""
    value = input(f"{message}{suffix}: ").strip()
    if value:
        return value
    return default or ""


def confirm(message: str, default: bool = True) -> bool:
    default_label = "Y/n" if default else "y/N"
    value = input(f"{message} [{default_label}]: ").strip().lower()
    if not value:
        return default
    return value in {"y", "yes"}


def run_command(command: list[str]) -> None:
    process = subprocess.run(command, cwd=ROOT)
    if process.returncode != 0:
        raise SystemExit(process.returncode)


def ensure_poetry() -> None:
    if shutil.which("poetry"):
        return

    if not confirm("Poetry is not installed. Install it now?", True):
        raise SystemExit("Poetry is required to continue.")

    run_command([sys.executable, "-m", "pip", "install", "poetry"])


def write_env_file() -> None:
    if ENV_PATH.exists() and not confirm(".env already exists. Overwrite it?", False):
        return

    access_key = prompt("AWS access key ID")
    secret_key = prompt("AWS secret access key")
    session_token = prompt("AWS session token", "")
    region_name = prompt("AWS region", "us-east-1")

    env_content = (
        f"aws_access_key_id={access_key}\n"
        f"aws_secret_access_key={secret_key}\n"
        f"aws_session_token={session_token}\n"
        f"aws_region_name={region_name}\n"
    )
    ENV_PATH.write_text(env_content, encoding="utf-8")


def ensure_env_example() -> None:
    if not ENV_EXAMPLE_PATH.exists():
        ENV_EXAMPLE_PATH.write_text(
            "aws_access_key_id=YOUR_ACCESS_KEY_ID\n"
            "aws_secret_access_key=YOUR_SECRET_ACCESS_KEY\n"
            "aws_session_token=\n"
            "aws_region_name=us-east-1\n",
            encoding="utf-8",
        )


def install_dependencies() -> None:
    run_command(["poetry", "install"])

    system_name = platform.system()

    if system_name == "Windows":
        run_command(["poetry", "run", "pip", "install", "python-magic-bin"])
    elif system_name == "Linux":
        print("Linux detected.")
        print("If python-magic fails later, install libmagic with your package manager.")
        print("Examples: `sudo apt install libmagic1` or `sudo apt install libmagic-dev`")
    elif system_name == "Darwin":
        print("macOS detected.")
        print("If python-magic fails later, install libmagic with Homebrew: `brew install libmagic`")


def main() -> None:
    print("AWS Python Automation init")
    ensure_env_example()
    ensure_poetry()
    write_env_file()

    if confirm("Install project dependencies now?", True):
        install_dependencies()

    print("Initialization finished.")
    print("Next step: run `poetry run python -m s3.upload_files_by_extension.main -h`")


if __name__ == "__main__":
    main()
