# VoiceForge AI

Windows-first, offline, real-time voice changer application.

## Project Goal

Capture microphone audio, transform voice in real-time (DSP + ONNX AI path), and play back with low latency while keeping the UI responsive.

## Planned Architecture

- `src/audio`: capture/output adapters and buffering
- `src/core`: canonical audio contracts and runtime-safe shared types
- `src/engine`: DSP effects and ONNX model adapter
- `src/runtime`: orchestration and fallback state machine
- `src/ui`: PySide6 UI and overlay behavior
- `tests`: unit/integration/ui/smoke tests
- `tools`: harness scripts for latency, routing, and diagnostics

## Current Status

Initial scaffold is in place.

- Python project metadata configured (`pyproject.toml`)
- CLI entrypoint available (`python -m src.main`)
- smoke tests configured with `pytest`
- repository setup and remote push discipline are active

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

## Run

```bash
python -m src.main --help
python -m src.main --no-audio
```

## Roadmap

1. Core contracts and AI streaming model contract
2. Callback-safe bypass audio pipeline
3. DSP preset engine
4. ONNX provider preflight and warm-up lifecycle
5. Runtime state machine and fallback/recovery hysteresis
6. PySide6 UI with state-consistent controls
7. Telemetry, soak tests, and packaging strategy
