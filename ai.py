from __future__ import annotations

import os
import platform
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent

import pydantic.warnings as pydantic_warnings
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from dotenv import dotenv_values, find_dotenv


UnsupportedFieldAttributeWarning = getattr(pydantic_warnings, "UnsupportedFieldAttributeWarning", UserWarning)
warnings.filterwarnings(
    "ignore",
    message=r".*functionDeclarations.*",
    category=UnsupportedFieldAttributeWarning,
)

ENV_FILE_KEYS = ("GEMINI_API_KEY", "TARGET_OS")


def load_env_file(path: Path) -> None:
    values = dotenv_values(path)
    for key in ENV_FILE_KEYS:
        value = values.get(key)
        if value is not None and key not in os.environ:
            os.environ[key] = value


def load_env() -> None:
    explicit_env = os.environ.get("AI_ENV_FILE")
    if explicit_env:
        explicit_path = Path(explicit_env).expanduser()
        if not explicit_path.is_file():
            raise RuntimeError(f"AI_ENV_FILE points to a missing file: {explicit_path}")
        load_env_file(explicit_path)
        return

    candidate_paths: list[Path] = []

    cwd_env = find_dotenv(usecwd=True)
    if cwd_env:
        candidate_paths.append(Path(cwd_env))

    source_env = Path(__file__).resolve().with_name(".env")
    candidate_paths.append(source_env)

    config_home = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")).expanduser()
    candidate_paths.append(config_home / "shell_ai" / ".env")
    candidate_paths.append(config_home / "ai" / ".env")
    candidate_paths.append(Path.home() / ".shell_ai.env")

    seen: set[Path] = set()
    for path in candidate_paths:
        resolved = path.resolve(strict=False)
        if resolved in seen:
            continue
        seen.add(resolved)
        if path.is_file():
            load_env_file(path)


DEFAULT_TARGET_OS = {"Darwin": "MacOS"}.get(platform.system(), platform.system())


def get_target_os() -> str:
    return os.environ.get("TARGET_OS", DEFAULT_TARGET_OS).strip() or DEFAULT_TARGET_OS


def build_system_prompt(target_os: str) -> str:
    return dedent(
        f"""\
    You are a professional developer specializing in shell commands.
    Your task is to generate the correct shell commands based on the 
    user's request.
    
    The OS is {target_os}.

    IMPORTANT: ALWAYS USE THE SAME LANGUAGE AS THE USER PROMPT IN 
    YOUR RESPONSE.

    Process:

    1. Think Aloud: Use the `think` function to explain your reasoning. 
    Justify why you chose a particular command, considering efficiency,
    safety, and best practices.

    2. Provide the Final Command: Use the `answer` function to present
    the final shell command concisely.
"""
    )


@dataclass
class Answer:
    success: bool
    cmd: str | None
    failure: str | None


def think(s: str) -> None:
    """Communicate your thought process to the user.

    Args:
        s (str): A description of your reasoning or decision-making process.
    """
    print(f"(AI Thinking): {s}\n")


def answer(success: bool, cmd: str | None, failure: str | None) -> Answer:
    """Provide the final shell command or explain why it couldn't be generated.

    Args:
        success (bool): Indicates whether a shell command was successfully generated.
        cmd (str | None): The generated shell command if `success` is True.
            It must be a single-line command. If `success` is False, this should be None.
        failure (str | None): If `success` is False, provide a reason why the command
            could not be generated. If `success` is True, this should be None.

    Returns:
        Answer: A structured response that will be processed for the user.
    """
    return Answer(success, cmd, failure)


def build_agent(gemini_key: str, target_os: str) -> Agent:
    cli_agent = Agent(
        model=GeminiModel("gemini-2.5-flash", api_key=gemini_key),
        system_prompt=build_system_prompt(target_os),
        result_type=Answer,
    )
    cli_agent.tool_plain(think)
    cli_agent.tool_plain(answer)
    return cli_agent


def print_config_error(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    print("", file=sys.stderr)
    print("Set GEMINI_API_KEY in one of these places:", file=sys.stderr)
    print("- your shell environment", file=sys.stderr)
    print("- a .env file in the directory where you run ai", file=sys.stderr)
    print("- ~/.config/shell_ai/.env", file=sys.stderr)
    print("- a file pointed to by AI_ENV_FILE", file=sys.stderr)


def main() -> None:
    try:
        load_env()
    except RuntimeError as exc:
        print_config_error(str(exc))
        sys.exit(1)

    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        print_config_error("Missing GEMINI_API_KEY.")
        sys.exit(1)

    user_prompt = " ".join(sys.argv[1:]).strip()
    if len(user_prompt) == 0:
        print("No prompts")
        sys.exit(1)

    agent = build_agent(gemini_key, get_target_os())
    resp = agent.run_sync(user_prompt)
    answer = resp.data
    if answer.success and answer.cmd is not None:
        print(f"(AI Answer): {answer.cmd}")
        #y_or_n = input("Execute? Y/N: ")
        #if y_or_n in ["y", "Y"]:
        #    os.system(answer.cmd)
        choice = input("Execute? [Y/n]: ").strip().lower()
        if choice == "":
            choice = "y"
        if choice == "y":
            os.system(answer.cmd)
        else:
            print("Skipped")
    else:
        print(f"(AI Answer): {answer.failure}")
        print("Generate failed")


if __name__ == "__main__":
    main()
