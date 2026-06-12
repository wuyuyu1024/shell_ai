# shell_ai

`shell_ai` is a lightweight local shell agent. You give it a natural-language request, it asks Gemini for the best shell command, shows its reasoning, and then lets you choose whether to execute the command on your machine.

The project is intentionally small:

- `ai.py`: the full CLI
- `.env`: local configuration
- `pyproject.toml`: Python dependencies

## Features

- Turns plain-language requests into shell commands
- Uses the same language as the user prompt
- Prints a short "thinking" trace before the final command
- Asks for confirmation before executing anything
- Lets you override the target operating system with `TARGET_OS`

## Requirements

- Python `3.13`
- [`uv`](https://docs.astral.sh/uv/)
- A `GEMINI_API_KEY`

## Setup

1. Create your env file:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and set your Gemini API key:

   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   TARGET_OS=MacOS
   ```

3. Install dependencies:

   ```bash
   uv sync --frozen
   ```

## Usage

### Run From The Repo

```bash
uv run ai "find the 20 largest files in this directory"
```

Another example:

```bash
uv run ai show me which process is using port 3000
```

### Install the `ai` Command

Use this if you want to type `ai ...` from any directory instead of running
`uv run ai ...` from this repo.

1. From this repo, install the command:

```bash
uv tool install --from . ai
```

This installs the project as a uv tool and creates an `ai` executable in uv's
tool bin directory.

2. Let uv update your shell configuration:

```bash
uv tool update-shell
```

Restart your terminal after running it.

3. Check that your shell can find the installed command:

```bash
command -v ai
```

This should print the path to the installed `ai` executable.

#### Configure `GEMINI_API_KEY`

For a global install, choose one of these setups.

Option 1: store only this tool's config in `~/.config/shell_ai/.env`:

```bash
mkdir -p ~/.config/shell_ai
printf 'GEMINI_API_KEY=your_gemini_api_key_here\n' > ~/.config/shell_ai/.env
```

Option 2: keep the real `.env` only in this repo and link to it:

```bash
mkdir -p ~/.config/shell_ai
ln -s "$(pwd)/.env" ~/.config/shell_ai/.env
readlink ~/.config/shell_ai/.env
```

The `readlink` command should print the full path to this repo's `.env` file.
After that, `ai ...` can read the repo `.env` from any directory.

The CLI only reads `GEMINI_API_KEY` and `TARGET_OS` from `.env` files. Other
values in the file are ignored by `ai`.

#### Manual `PATH` setup

Most users can stop after `uv tool update-shell`. Use this section only if
`command -v ai` prints nothing.

First, ask uv where it installs tool commands:

```bash
uv tool dir --bin
```

Then add that directory to your `PATH`. Only use the block for your shell.

Bash or zsh:

Add this line to your shell startup file, such as `~/.zshrc` or `~/.bashrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Fish:

```fish
fish_add_path -U ~/.local/bin
```

If `uv tool dir --bin` prints a different directory, use that path instead of
`~/.local/bin`.

If you already installed it once and want to refresh the command after local
code changes:

```bash
uv tool install --from . ai --force --refresh
```

After `PATH` and `GEMINI_API_KEY` are configured, these examples work:

```bash
ai show my graphic card
ai "how much memory is used?"
```

When installed as a tool, `ai` can read `GEMINI_API_KEY` from:

- your shell environment
- a `.env` file in the current directory
- `~/.config/shell_ai/.env`
- `~/.config/ai/.env`
- `~/.shell_ai.env`
- a file pointed to by `AI_ENV_FILE`

The flow is:

1. The agent prints its reasoning.
2. The agent prints one final shell command.
3. You confirm with `Y` or cancel with `n`.

## Configuration

Environment variables:

- `GEMINI_API_KEY`: required
- `TARGET_OS`: optional; defaults to the current OS detected by Python
- `AI_ENV_FILE`: optional; points to a specific `.env` file to load

Notes:

- On macOS, the default target OS is normalized to `MacOS`.
- If `GEMINI_API_KEY` is missing, the script exits immediately with an error.

## Gemini Free Tier Note

This project uses the Gemini Developer API through `pydantic-ai` and currently targets `gemini-2.5-flash`.

As of March 30, 2026, Google lists `gemini-2.5-flash` with a free tier on the Gemini API pricing page, so this setup can work with a Google AI Studio / Gemini API key without paid billing, subject to Google's current regional availability, quotas, and account limits.

## Safety

This tool runs the generated command with `os.system(...)` after confirmation. That means:

- always read the command before accepting execution
- do not use it for destructive tasks unless you understand the command
- treat the output as AI-generated shell code, not guaranteed-safe automation

## Current Limitations

- It returns a single-line command, not a multi-step script.
- There is no sandboxing, retry logic, or command validation layer.

## Development

The code lives entirely in [`ai.py`](./ai.py). If you want to adjust behavior, the main places to change are:

- `SYSTEM_PROMPT` for agent instructions
- `GeminiModel("gemini-2.5-flash", ...)` for model selection
- `main()` for CLI behavior and execution policy

## References

- Gemini API pricing: https://ai.google.dev/gemini-api/docs/pricing
- Gemini API billing: https://ai.google.dev/gemini-api/docs/billing
- Gemini API rate limits: https://ai.google.dev/gemini-api/docs/rate-limits
