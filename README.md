# shell_ai

`shell_ai` is a lightweight local shell agent. You give it a natural-language request, it asks Gemini for the best shell command, shows its reasoning, and then lets you choose whether to execute the command on your machine.

The project is intentionally small:

- `ai.py`: the full CLI
- `.env`: local configuration
- `pyproject.toml`: Python dependencies

## Why Gemini Free Tier Works Here

This project uses the Gemini Developer API through `pydantic-ai` and currently targets `gemini-2.5-flash`.

As of March 30, 2026, Google lists `gemini-2.5-flash` with a free tier on the Gemini API pricing page, so this setup can work with a Google AI Studio / Gemini API key without paid billing, subject to Google's current regional availability, quotas, and account limits.

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

Run it from the project directory:

```bash
uv run ai "find the 20 largest files in this directory"
```

Another example:

```bash
uv run ai show me which process is using port 3000
```

If you want `ai` available directly in your shell, install this project as a tool:

```bash
uv tool install --from . ai
```

If `uv` warns that the tool bin directory is not on `PATH`, either run:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

To make that permanent in bash:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

or let `uv` update your shell config:

```bash
uv tool update-shell
```

If you already installed it once and want to pick up local code changes, reinstall with:

```bash
uv tool install --from . ai --force --refresh
```

After that, these both work:

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

For a shell-wide setup, export the key in your shell profile:

```bash
export GEMINI_API_KEY=your_gemini_api_key_here
```

Or store it in a persistent config file:

```bash
mkdir -p ~/.config/shell_ai
printf 'GEMINI_API_KEY=your_gemini_api_key_here\n' > ~/.config/shell_ai/.env
```

The flow is:

1. The agent prints its reasoning.
2. The agent prints one final shell command.
3. You confirm with `Y` or cancel with `n`.

## Configuration

Environment variables:

- `GEMINI_API_KEY`: required
- `TARGET_OS`: optional; defaults to the current OS detected by Python

Notes:

- On macOS, the default target OS is normalized to `MacOS`.
- If `GEMINI_API_KEY` is missing, the script exits immediately with an error.

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
