# Windows-First Real-Time Voice Changer v1

## TL;DR
> **Summary**: Build a Windows-first desktop voice changer with a strict real-time audio engine, a PySide6 control surface, hybrid transformation in v1 (DSP presets + one ONNX AI path), and explicit fallback/telemetry so the app stays usable even when AI inference is unavailable.
> **Deliverables**:
> - Real-time microphone capture, transform, and playback pipeline
> - DSP preset path and one ONNX-based AI conversion path
> - PySide6 main window plus overlay-style hotkey activation
> - Existing virtual-audio tool compatibility validation on Windows
> - Automated latency/fallback/QA harness with evidence artifacts
> - Local git repo initialized in the current workspace, connected to `https://github.com/mschoi0411/voiceforge-ai.git`, with per-task push discipline
> **Effort**: XL
> **Parallel**: YES - 7 waves
> **Critical Path**: 1 -> 2 -> 3 -> 6 -> 7 -> 8 -> 10

## Context
### Original Request
Refine and strengthen the proposed architecture for a real-time AI voice changer, add missing decisions and recommended additions, and turn it into an implementation-ready development plan.

### Interview Summary
- Greenfield workspace: there is no existing source tree, manifest, test harness, or packaging configuration to preserve.
- v1 scope is hybrid: DSP presets for responsiveness plus one ONNX-based AI conversion path.
- v1 routing scope is local monitoring plus compatibility with existing virtual-audio tools; no bundled virtual microphone driver.
- Test strategy is `tests-after`.
- Performance baseline is CPU-capable operation with optional NVIDIA acceleration.
- Packaging is deferred until the core pipeline is stable and instrumented.

### Metis Review (gaps addressed)
- Added a canonical internal audio contract, backpressure policy, failure-state mapping, warm-up semantics, and observability requirements.
- Added explicit reference hardware tiers and measurable latency targets to avoid vague "low latency" acceptance.
- Constrained v1 scope to one runtime family (`ONNX Runtime`) and one AI model contract.
- Added named routing compatibility validation, local-only model management, and explicit "not in v1" guardrails.

## Work Objectives
### Core Objective
Deliver a Windows-first offline desktop application that processes live microphone input in real time, applies either DSP or one ONNX AI transformation path, and outputs stable transformed audio without blocking the UI or callback thread.

### Deliverables
- Python application scaffold with `src/`, `tests/`, `tools/`, `models/`, and configuration layout
- Local git repository initialized in the current workspace and connected to `origin` = `https://github.com/mschoi0411/voiceforge-ai.git`
- Initial `README.md` covering project purpose, architecture, setup, roadmap, and current implementation status
- Canonical audio format and runtime contracts
- Callback-safe capture/output path with bypass mode
- DSP preset engine with pitch/tone/character transforms
- ONNX runtime adapter with warm-up and CPU/GPU provider fallback
- Pipeline orchestrator with bounded queues, backpressure, and fallback state machine
- PySide6 main window and overlay toggle with Windows-first global hotkey support
- Windows routing compatibility validation for `VB-CABLE` and `Voicemeeter` style setups
- Telemetry, diagnostics, and automated harnesses that emit `.sisyphus/evidence/*`
- Packaging comparison spike between `PyInstaller` and `pyside6-deploy` with a deterministic selection rule
- Packaging readiness workstream after stability gate

### Definition of Done (verifiable conditions with commands)
- `python -m pytest tests/unit -q`
- `python -m pytest tests/integration -q`
- `python -m pytest tests/ui -q`
- `python tools/pipeline_harness.py --mode bypass --input tests/fixtures/voice_48k_mono.wav --expect-max-latency-ms 80 --json-out .sisyphus/evidence/final-bypass.json`
- `python tools/pipeline_harness.py --mode dsp_preset --preset robot --input tests/fixtures/voice_48k_mono.wav --expect-max-latency-ms 100 --json-out .sisyphus/evidence/final-dsp.json`
- `python tools/pipeline_harness.py --mode ai_onnx --model models/default/default.onnx --input tests/fixtures/voice_48k_mono.wav --expect-provider any --expect-state ready --json-out .sisyphus/evidence/final-ai.json`
- `python tools/routing_probe.py --targets "VB-CABLE,Voicemeeter" --json-out .sisyphus/evidence/final-routing.json`

### Must Have
- Canonical internal audio format: mono `float32` PCM at `24000 Hz`, fixed `10 ms` frames (`240` samples), timestamped at ingress
- Queue policy: capture queue max `3` frames, process queue max `3` frames, output queue max `3` frames; on overflow, drop the oldest unprocessed frame and increment a dropped-frame counter
- Windows-first audio backend via `sounddevice`/PortAudio with WASAPI low-latency mode when available
- Supported release target: Windows 10/11 x64 for v1; macOS/Linux remain adapter-ready but unsupported for release parity
- Primary inference runtime: `ONNX Runtime` with provider order `CUDAExecutionProvider -> CPUExecutionProvider`
- AI streaming contract for v1: one stateful ONNX model family wrapped behind a fixed streaming adapter that consumes `4` canonical frames per inference (`40 ms`, `960` samples at `24 kHz`), emits `4` canonical frames per inference, uses `0 ms` positive lookahead, keeps continuity through explicit state tensors or fixed rolling history, and forbids orchestrator-level overlap-add
- AI manifest contract: each model package must declare tensor names, tensor shapes, dtype, required pre/post normalization, stateful vs stateless mode, warm-up input shape, and whether `state_in/state_out` tensors are mandatory; the bundled default path uses `audio_in:[1,1,960]` and `audio_out:[1,1,960]` as the primary streaming tensors
- Resampler ownership: canonicalize exactly once at ingress and reformat exactly once at egress when needed; no mid-pipeline sample-rate or channel conversion is allowed
- Latency accounting must be stage-based, not only end-to-end: capture ingress -> canonical frame ready, canonical frame ready -> transform ready, transform ready -> output submit, end-to-end monitor, warm-up, mode switch, and device recovery all require separate metrics
- CPU-only operation must remain functional; GPU acceleration is an optimization path
- Bounded queues only, with explicit overflow policy and visible counters
- Model load and warm-up entirely off the callback thread
- Warm-up semantics: preload the selected model on app launch or model selection; keep AI controls disabled until readiness is `ready`; target warm-up <= `12 s` on CPU tier and <= `5 s` on GPU tier
- Offline-only model usage: bundled local sample model plus user-imported local models only
- v1 model contract: one local ONNX model family only, mono `24 kHz` input/output wrapper, and packaged default model artifact ceiling of `200 MB`
- Failure mapping: model load failure -> DSP mode, provider failure -> CPU provider then DSP, device loss -> muted-safe state until recovery or user reselects device
- Sustained-lag fallback trigger: if AI transform-stage p95 exceeds `55 ms` for `2` consecutive `5 s` windows, or process-queue depth stays above `2` for more than `500 ms`, force downgrade to DSP and record an overload event
- Recovery policy: fallback is sticky for at least `10 s`; AI auto-retry is allowed only if the user-selected mode is still AI, provider preflight passes, queue depth stays <= `1` for the preceding `5 s`, and no callback over/underflow event occurs during that retry window
- Provider re-check cadence while degraded: rerun provider preflight every `30 s` and on manual model reselect; never retry faster than the configured cooldown
- Provider preflight: on app launch and model selection, record `get_available_providers()`, attempt session creation with configured provider order, run one warm-up inference, record actual provider(s) used, and downgrade AI availability immediately if session creation or warm-up fails
- Reconnect policy: device reconnect attempts begin after `1000 ms` debounce, retry at `2000 ms` intervals up to `3` attempts, then remain in `device_lost` until manual device selection
- Audio quality gates for release: processed audio must keep clipping ratio <= `0.1%`, absolute DC offset mean <= `0.01`, voiced-frame dropout ratio <= `1%`, and loudness delta versus bypass within `+/- 6 dB` except for presets explicitly tagged as `extreme`
- Global hotkey support for Windows in v1; non-Windows parity is deferred
- Automated evidence capture for happy path and failure path scenarios
- Every implementation commit is pushed to `origin` immediately after local verification passes

### Must NOT Have (guardrails, AI slop patterns, scope boundaries)
- No cloud inference, remote API dependency, or runtime model download requirement
- No bundled virtual-audio driver in v1
- No `Torch` production runtime in v1
- No multiple AI model families in v1
- No inference, logging, disk I/O, or resampling on the audio callback thread
- No heap-heavy allocation bursts, blocking locks, provider/session creation, device enumeration, exception formatting, JSON/metrics serialization, or direct Qt signal emission on the audio callback thread
- No cross-platform parity promise before Windows validation passes
- No marketplace, account system, sync, recording studio features, or Discord-specific integration in v1
- No packaging/release blocker before real-time stability and telemetry gates pass
- No unpushed local implementation commit after a task marked complete

## Verification Strategy
> ZERO HUMAN INTERVENTION - all verification is agent-executed.
- Test decision: `tests-after` using `pytest`, `pytest-qt`, and purpose-built harness scripts
- QA policy: every task includes happy-path and failure-path automated scenarios
- Evidence: `.sisyphus/evidence/task-{N}-{slug}.{ext}`
- Reference hardware tiers:
  - CPU tier: Windows 11, 6-core laptop-class CPU, 16 GB RAM, no discrete GPU
  - GPU tier: Windows 11, same CPU baseline plus NVIDIA RTX-class GPU with current drivers
- Latency targets:
  - Capture ingress -> canonical frame ready p95 <= `20 ms`
  - Canonical frame ready -> transform ready p95 <= `25 ms` in DSP mode and <= `55 ms` in AI mode
  - Transform ready -> output submit p95 <= `20 ms`
  - Bypass path p95 <= `80 ms`
  - DSP path p95 <= `100 ms`
  - AI path on GPU p95 <= `100 ms`
  - AI path on CPU must stay functional and fall back safely if p95 exceeds `100 ms`
  - Mode switch to DSP or bypass visible-state update <= `250 ms`
  - Device-loss banner/state update <= `500 ms`
  - Warm-up and recovery metrics are tracked independently from steady-state latency
- Quality and soak gates:
  - Release evidence must include clipping ratio, DC offset, loudness delta, voiced-frame dropout ratio, callback exception count, queue-depth drift, and memory-growth trend
  - Soak verification is mandatory before packaging sign-off: `30 min` bypass, `30 min` DSP, `15 min` AI on CPU tier, `15 min` AI on GPU tier if available

## Execution Strategy
### Parallel Execution Waves
> Target: 5-8 tasks per wave. This plan uses smaller waves because the real-time pipeline has hard technical dependencies that must be stabilized before later work can be trusted.

Wave 1: scaffold foundation (`1`)
Wave 2: contracts and config (`2`)
Wave 3: independent engine slices (`3`, `4`, `5`)
Wave 4: runtime orchestration (`6`)
Wave 5: UI control plane (`7`)
Wave 6: routing validation and telemetry (`8`, `9`)
Wave 7: packaging and release gate (`10`)

### Dependency Matrix (full, all tasks)
- `1` -> blocks `2`, `3`, `5`, `7`
- `2` -> blocks `3`, `4`, `5`, `6`, `7`
- `3` -> blocks `6`, `8`, `9`
- `4` -> blocks `6`, `9`
- `5` -> blocks `6`, `9`
- `6` -> blocks `7`, `8`, `9`
- `7` -> blocks `8`, `9`, `10`
- `8` -> blocks `10`
- `9` -> blocks `10`
- `10` -> release/stability gate end-state

### Agent Dispatch Summary (wave -> task count -> categories)
- Wave 1 -> 1 task -> `quick`
- Wave 2 -> 1 task -> `unspecified-high`
- Wave 3 -> 3 tasks -> `deep`, `unspecified-high`
- Wave 4 -> 1 task -> `deep`
- Wave 5 -> 1 task -> `visual-engineering`
- Wave 6 -> 2 tasks -> `unspecified-high`, `deep`
- Wave 7 -> 1 task -> `writing`

## TODOs
> Implementation + Test = ONE task. Never separate.
> EVERY task MUST have: Agent Profile + Parallelization + QA Scenarios.

- [ ] 1. Scaffold project layout and verification harness baseline

  **What to do**: Initialize git in the current `voice_change` workspace, set default branch to `main`, connect `origin` to `https://github.com/mschoi0411/voiceforge-ai.git`, create the initial Python project structure under `src/`, `tests/`, `tools/`, `models/`, and `.sisyphus/evidence/`, define dependency manifests, wire `pytest`, `pytest-qt`, fixture storage, add a minimal CLI entrypoint that can launch in a no-audio test mode, and create `README.md` with project overview, planned architecture, setup steps, roadmap, and current status.
  **Must NOT do**: Do not implement real audio transforms yet; do not add packaging, cloud integration, or multiple runtime options.

  **Recommended Agent Profile**:
  - Category: `quick` - Reason: mostly scaffold, manifests, and test harness setup
  - Skills: `[]` - no special skill required
  - Omitted: `['/playwright']` - browser automation is not relevant here

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: `2`, `3`, `5`, `7` | Blocked By: none

  **References**:
  - Baseline: `.sisyphus/plans/real-time-voice-changer-v1.md` - authoritative scope, guardrails, and deliverables for execution
  - External: `https://docs.pytest.org/` - test runner conventions
  - External: `https://pytest-qt.readthedocs.io/` - Qt test harness conventions
  - External: `https://doc.qt.io/qtforpython-6/` - PySide6 application bootstrap patterns

  **Acceptance Criteria** (agent-executable only):
  - [ ] `python -m pytest tests -q` runs and collects the scaffolded empty/smoke suites without import errors
  - [ ] `python -m src.main --help` exits successfully in non-audio mode
  - [ ] `git remote get-url origin` returns `https://github.com/mschoi0411/voiceforge-ai.git`
  - [ ] `git branch --show-current` returns `main`
  - [ ] `README.md` exists at repo root and documents purpose, stack, setup, architecture, and roadmap

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Scaffold smoke path
    Tool: Bash
    Steps: Run `python -m pytest tests/smoke -q`; run `python -m src.main --help`; run `git remote get-url origin`
    Expected: Test collection succeeds; CLI help renders without audio-device access; `origin` points to `https://github.com/mschoi0411/voiceforge-ai.git`
    Evidence: .sisyphus/evidence/task-1-scaffold.json

  Scenario: Missing optional dependency path
    Tool: Bash
    Steps: Run `python -m src.main --no-audio --require-optional missing_dep`
    Expected: Process exits non-zero with a clear dependency/setup message and no traceback spam
    Evidence: .sisyphus/evidence/task-1-scaffold-error.json
  ```

  **Commit**: YES | Message: `chore(scaffold): initialize repo, readme, and test harness` | Files: `.git/`, `README.md`, `src/`, `tests/`, `tools/`, `models/`, project manifest files

- [ ] 2. Define canonical audio contracts and runtime configuration

  **What to do**: Implement shared types/config for canonical internal audio frames (`float32`, mono, `24000 Hz`, `10 ms` frames), queue limits, latency thresholds, provider ordering, model metadata, fallback states, and the fixed v1 AI streaming contract; define ingress-only canonicalization and egress-only format conversion; add fixture generators and validation tests for resample/downmix rules, model tensor contract validation, and expanded audio-quality fixtures.
  **Must NOT do**: Do not bind directly to UI widgets or device APIs in this task.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` - Reason: core contracts affect every later module
  - Skills: `[]` - codebase-local type/config work
  - Omitted: `['/frontend-ui-ux']` - no UI design work here

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: `3`, `4`, `5`, `6`, `7` | Blocked By: `1`

  **References**:
  - Baseline: `.sisyphus/plans/real-time-voice-changer-v1.md` - canonical audio contract and modular requirements
  - External: `https://onnxruntime.ai/docs/` - provider/session configuration concepts
  - External: `https://numpy.org/doc/` - array dtype and shape expectations for PCM tensors
  - External: `https://onnxruntime.ai/docs/api/python/api_summary.html` - `InferenceSession`, provider precedence, `get_available_providers()`, and tensor metadata APIs

  **Acceptance Criteria** (agent-executable only):
  - [ ] `python -m pytest tests/unit/test_audio_contracts.py -q`
  - [ ] `python -m pytest tests/unit/test_settings_validation.py -q`
  - [ ] `python -m pytest tests/unit/test_model_manifest_contract.py -q`
  - [ ] `python -m pytest tests/unit/test_fixture_matrix.py -q`

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Canonical format happy path
    Tool: Bash
    Steps: Run `python -m pytest tests/unit/test_audio_contracts.py -q`
    Expected: Canonical frame schema, timestamps, queue caps, and provider order validate successfully
    Evidence: .sisyphus/evidence/task-2-contracts.json

  Scenario: Sample-rate mismatch normalization
    Tool: Bash
    Steps: Run `python -m pytest tests/unit/test_resample_policy.py -q`
    Expected: `44.1kHz` and stereo fixtures normalize to canonical mono `24kHz` without contract violations
    Evidence: .sisyphus/evidence/task-2-contracts-error.json

  Scenario: Model contract and fixture matrix validation
    Tool: Bash
    Steps: Run `python -m pytest tests/unit/test_model_manifest_contract.py -q`; run `python -m pytest tests/unit/test_fixture_matrix.py -q`
    Expected: Manifest rejects unsupported tensor names/shapes/lookahead/state modes; fixtures cover silence-heavy speech, near-clipping speech, noisy speech, plosive-heavy speech, fast speech, slow speech, male/female range examples, and stereo `44.1kHz` normalization paths
    Evidence: .sisyphus/evidence/task-2-contracts-matrix.json
  ```

  **Commit**: YES | Message: `feat(core): define audio contracts and runtime settings` | Files: `src/core/`, `src/config/`, `tests/unit/`, `tests/fixtures/`

- [ ] 3. Build callback-safe capture/output bypass slice

  **What to do**: Implement Windows-first input/output device adapters using `sounddevice`, WASAPI low-latency settings when available, lock-free or minimal-lock frame handoff, ingress canonicalization outside the callback thread, egress format conversion outside the callback thread, and a bypass mode that proves end-to-end capture-to-playback works before transformation is introduced.
  **Must NOT do**: Do not run inference, resampling policy changes, logging, disk writes, device enumeration, provider probes, large allocations, exception formatting, or telemetry serialization on the callback thread.

  **Recommended Agent Profile**:
  - Category: `deep` - Reason: this is the first real-time critical slice with strict latency constraints
  - Skills: `[]` - direct implementation focus
  - Omitted: `['/git-master']` - no git-specific work required

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: `6`, `8`, `9` | Blocked By: `1`, `2`

  **References**:
  - Baseline: `.sisyphus/plans/real-time-voice-changer-v1.md` - capture/output requirements and latency target
  - External: `https://python-sounddevice.readthedocs.io/` - stream callback and device enumeration API
  - External: `https://numpy.org/doc/` - frame buffer handling
  - External: `https://python-sounddevice.readthedocs.io/en/latest/api/misc.html` - callback under/overflow behavior and guidance to avoid blocking callback work

  **Acceptance Criteria** (agent-executable only):
  - [ ] `python -m pytest tests/integration/test_bypass_pipeline.py -q`
  - [ ] `python tools/pipeline_harness.py --mode bypass --input tests/fixtures/voice_48k_mono.wav --expect-max-latency-ms 80 --json-out .sisyphus/evidence/task-3-bypass.json`

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Bypass happy path
    Tool: Bash
    Steps: Run `python tools/pipeline_harness.py --mode bypass --input tests/fixtures/voice_48k_mono.wav --expect-max-latency-ms 80 --json-out .sisyphus/evidence/task-3-bypass.json`
    Expected: Callback exceptions stay at `0`, queue depth stays within cap, reported p95 latency is <= `80 ms`, and no mid-pipeline resample event is recorded
    Evidence: .sisyphus/evidence/task-3-bypass.json

  Scenario: Device disconnect recovery
    Tool: Bash
    Steps: Run `python -m pytest tests/integration/test_device_hot_unplug.py -q`
    Expected: Pipeline enters safe-muted state, reports device-loss event, and recovers or surfaces a controlled error banner state
    Evidence: .sisyphus/evidence/task-3-bypass-error.json
  ```

  **Commit**: YES | Message: `feat(audio): add callback-safe bypass pipeline` | Files: `src/audio/`, `src/core/`, `tools/pipeline_harness.py`, `tests/integration/`

- [ ] 4. Implement DSP preset engine and post-processing chain

  **What to do**: Add low-latency DSP transforms for pitch/tone/character presets, plus normalization, gain, EQ-lite, clipping prevention, and basic output-quality metrics; expose preset metadata separately from UI so the engine can run headless in tests.
  **Must NOT do**: Do not make DSP state depend on Qt objects; do not silently change the canonical frame size or sample rate.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` - Reason: medium-complexity signal-processing work with strict contract adherence
  - Skills: `[]` - no extra skill required
  - Omitted: `['/frontend-ui-ux']` - keep preset logic out of UI concerns

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: `6`, `9` | Blocked By: `2`

  **References**:
  - Baseline: `.sisyphus/plans/real-time-voice-changer-v1.md` - required DSP preset scope and latency guardrails
  - External: `https://numpy.org/doc/` - vectorized DSP buffer operations
  - External: `https://docs.pytest.org/` - fixture-driven regression testing

  **Acceptance Criteria** (agent-executable only):
  - [ ] `python -m pytest tests/unit/test_dsp_effects.py -q`
  - [ ] `python -m pytest tests/unit/test_dsp_quality_metrics.py -q`
  - [ ] `python tools/pipeline_harness.py --mode dsp_preset --preset deep_voice --input tests/fixtures/voice_48k_mono.wav --expect-max-latency-ms 100 --json-out .sisyphus/evidence/task-4-dsp.json`

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: DSP preset happy path
    Tool: Bash
    Steps: Run `python tools/pipeline_harness.py --mode dsp_preset --preset deep_voice --input tests/fixtures/voice_48k_mono.wav --expect-max-latency-ms 100 --json-out .sisyphus/evidence/task-4-dsp.json`
    Expected: Output audio remains within canonical format, clipping counter is `0`, and p95 latency is <= `100 ms`
    Evidence: .sisyphus/evidence/task-4-dsp.json

  Scenario: Extreme slider bounds
    Tool: Bash
    Steps: Run `python -m pytest tests/unit/test_dsp_parameter_bounds.py -q`
    Expected: Invalid pitch/tone values clamp or reject deterministically without NaNs or crashes
    Evidence: .sisyphus/evidence/task-4-dsp-error.json

  Scenario: DSP quality sanity checks
    Tool: Bash
    Steps: Run `python -m pytest tests/unit/test_dsp_quality_metrics.py -q`
    Expected: DSP output stays within clipping, DC offset, and loudness-delta thresholds defined for non-extreme presets
    Evidence: .sisyphus/evidence/task-4-dsp-quality.json
  ```

  **Commit**: YES | Message: `feat(engine): add dsp presets and post-processing` | Files: `src/engine/`, `src/core/`, `tests/unit/`, `tools/pipeline_harness.py`

- [ ] 5. Add ONNX inference adapter, model registry, and warm-up lifecycle

  **What to do**: Implement the single v1 AI path around `ONNX Runtime`; define a local model manifest, provider selection order, provider preflight, exact tensor contract, background warm-up, readiness state, actual-provider recording, unsupported-op warning path, and CPU/GPU fallback without changing the engine contract.
  **Must NOT do**: Do not add `Torch` runtime support; do not cold-load the model on hotkey press or audio callback entry; do not enable AI mode before provider preflight and warm-up succeed.

  **Recommended Agent Profile**:
  - Category: `deep` - Reason: runtime/provider behavior and warm-up semantics are high-risk architecture points
  - Skills: `[]` - focused systems work
  - Omitted: `['/playwright']` - not a browser task

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: `6`, `9` | Blocked By: `1`, `2`

  **References**:
  - Baseline: `.sisyphus/plans/real-time-voice-changer-v1.md` - AI runtime choice and fallback requirements
  - External: `https://onnxruntime.ai/docs/` - providers, sessions, and optimization settings
  - External: `https://numpy.org/doc/` - tensor/frame conversion expectations
  - External: `https://onnxruntime.ai/docs/api/python/api_summary.html` - provider precedence, `get_available_providers()`, `get_inputs()`, `get_outputs()`, `enable_profiling`, and `run_async()` semantics

  **Acceptance Criteria** (agent-executable only):
  - [ ] `python -m pytest tests/unit/test_model_registry.py -q`
  - [ ] `python -m pytest tests/integration/test_onnx_warmup.py -q`
  - [ ] `python -m pytest tests/integration/test_provider_preflight.py -q`

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: ONNX warm-up happy path
    Tool: Bash
    Steps: Run `python -m pytest tests/integration/test_onnx_warmup.py -q`
    Expected: Selected model initializes in the background, reports provider used, and flips readiness from `warming` to `ready` before AI enablement
    Evidence: .sisyphus/evidence/task-5-onnx.json

  Scenario: Provider/model failure fallback
    Tool: Bash
    Steps: Run `python -m pytest tests/integration/test_model_provider_fallback.py -q`
    Expected: Missing or failing provider degrades to CPU or DSP/bypass according to policy, with explicit error state and no callback crash
    Evidence: .sisyphus/evidence/task-5-onnx-error.json

  Scenario: Provider preflight and actual-provider record
    Tool: Bash
    Steps: Run `python -m pytest tests/integration/test_provider_preflight.py -q`
    Expected: Startup preflight records available providers, session creation result, actual provider used, and warns deterministically when configured providers or required ops are unavailable
    Evidence: .sisyphus/evidence/task-5-onnx-preflight.json
  ```

  **Commit**: YES | Message: `feat(ai): add onnx adapter and warmup lifecycle` | Files: `src/engine/`, `src/models/`, `src/config/`, `tests/unit/`, `tests/integration/`

- [ ] 6. Build pipeline orchestrator, bounded queues, and fallback state machine

  **What to do**: Implement the runtime controller that switches among bypass, DSP, and AI modes; enforce queue caps and drop/coalesce policy; centralize state transitions for `warming`, `ready`, `degraded_dsp`, `device_lost`, `recovering`, and `error`; and implement deterministic recovery hysteresis for warm-up completion, overload relief, provider retry, and device recovery.
  **Must NOT do**: Do not let UI code own pipeline truth; do not allow unbounded buffering or ambiguous failure states; do not auto-flap between AI and DSP without cooldown and preflight checks.

  **Recommended Agent Profile**:
  - Category: `deep` - Reason: core orchestration and safety policy task
  - Skills: `[]` - architecture-sensitive systems work
  - Omitted: `['/frontend-ui-ux']` - UI should consume state, not define it

  **Parallelization**: Can Parallel: NO | Wave 4 | Blocks: `7`, `8`, `9` | Blocked By: `3`, `4`, `5`

  **References**:
  - Baseline: `.sisyphus/plans/real-time-voice-changer-v1.md` - fallback system and runtime policy requirements
  - External: `https://onnxruntime.ai/docs/` - runtime/provider failure modes
  - External: `https://docs.pytest.org/` - state-machine regression coverage patterns

  **Acceptance Criteria** (agent-executable only):
  - [ ] `python -m pytest tests/integration/test_pipeline_state_machine.py -q`
  - [ ] `python -m pytest tests/integration/test_overload_backpressure.py -q`
  - [ ] `python -m pytest tests/integration/test_mode_switch_regression.py -q`

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Mode switching happy path
    Tool: Bash
    Steps: Run `python -m pytest tests/integration/test_pipeline_state_machine.py -q`
    Expected: Bypass -> DSP -> AI transitions occur only when readiness conditions pass, and queue-depth metrics remain within configured caps
    Evidence: .sisyphus/evidence/task-6-orchestrator.json

  Scenario: Inference overload path
    Tool: Bash
    Steps: Run `python -m pytest tests/integration/test_overload_backpressure.py -q`
    Expected: When inference lags, the controller drops/coalesces according to policy, raises an overload event, and falls back safely without growing queue depth past the cap
    Evidence: .sisyphus/evidence/task-6-orchestrator-error.json

  Scenario: Recovery and rapid-switch regression
    Tool: Bash
    Steps: Run `python -m pytest tests/integration/test_mode_switch_regression.py -q`
    Expected: Rapid `bypass -> DSP -> AI -> DSP -> bypass` transitions, AI-enable spam during warm-up, and device changes during warm-up do not produce mode flapping or stale worker state
    Evidence: .sisyphus/evidence/task-6-orchestrator-recovery.json
  ```

  **Commit**: YES | Message: `feat(runtime): add pipeline orchestrator and fallback state machine` | Files: `src/runtime/`, `src/core/`, `tests/integration/`, `tools/pipeline_harness.py`

- [ ] 7. Create PySide6 control surface, overlay behavior, and Windows hotkey flow

  **What to do**: Build the main window and lightweight overlay/hotbar; wire enable/disable toggle, preset selector, pitch/tone sliders, device selectors, model readiness indicator, and a Windows-first global hotkey that shows/hides the overlay without owning engine state; define a single runtime-to-UI state map for `warming`, `ready`, `degraded_dsp`, `device_lost`, `recovering`, and `error`.
  **Must NOT do**: Do not perform audio work on the UI thread; do not enable AI controls before warm-up completes; do not let overlay visibility implicitly change pipeline mode.

  **Recommended Agent Profile**:
  - Category: `visual-engineering` - Reason: UI implementation must remain deliberate while respecting engine constraints
  - Skills: `[]` - direct desktop UI work
  - Omitted: `['/playwright']` - browser UI tooling is not relevant; use `pytest-qt`

  **Parallelization**: Can Parallel: YES | Wave 5 | Blocks: `9`, `10` | Blocked By: `1`, `2`, `6`

  **References**:
  - Baseline: `.sisyphus/plans/real-time-voice-changer-v1.md` - overlay UI, controls, and hotkey requirements
  - External: `https://doc.qt.io/qtforpython-6/` - Qt widget/thread patterns
  - External: `https://pytest-qt.readthedocs.io/` - UI automation patterns for PySide6

  **Acceptance Criteria** (agent-executable only):
  - [ ] `python -m pytest tests/ui/test_main_window.py -q`
  - [ ] `python -m pytest tests/ui/test_overlay_hotkey.py -q`
  - [ ] `python -m pytest tests/ui/test_ui_state_consistency.py -q`

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: UI happy path
    Tool: Bash
    Steps: Run `python -m pytest tests/ui/test_main_window.py -q`
    Expected: Preset, device, and enable controls render; AI toggle remains disabled until readiness state is `ready`
    Evidence: .sisyphus/evidence/task-7-ui.json

  Scenario: Provider failure reflected in UI
    Tool: Bash
    Steps: Run `python -m pytest tests/ui/test_provider_failure_banner.py -q`
    Expected: Provider failure surfaces a visible error state, AI controls disable, and DSP/bypass controls remain available
    Evidence: .sisyphus/evidence/task-7-ui-error.json

  Scenario: Runtime-to-UI state consistency
    Tool: Bash
    Steps: Run `python -m pytest tests/ui/test_ui_state_consistency.py -q`
    Expected: UI reads all readiness/mode/overload/device-loss states from the runtime source of truth, explains why fallback occurred, and only disables controls according to the declared state map
    Evidence: .sisyphus/evidence/task-7-ui-state.json
  ```

  **Commit**: YES | Message: `feat(ui): add control surface and overlay hotkey flow` | Files: `src/ui/`, `tests/ui/`, `src/runtime/`

- [ ] 8. Validate Windows routing compatibility and isolate backend adapters

  **What to do**: Add device-enumeration and routing probes for Windows; validate interoperability with named third-party tools (`VB-CABLE`, `Voicemeeter`) and formalize a backend adapter interface so macOS/Linux implementations can be added later without changing engine contracts.
  **Must NOT do**: Do not ship or bundle a virtual-audio driver; do not claim macOS/Linux parity yet.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` - Reason: OS/device boundary work with external compatibility risk
  - Skills: `[]` - systems integration focus
  - Omitted: `['/frontend-ui-ux']` - task is backend/routing validation, not UI polish

  **Parallelization**: Can Parallel: YES | Wave 6 | Blocks: `10` | Blocked By: `3`, `6`, `7`

  **References**:
  - Baseline: `.sisyphus/plans/real-time-voice-changer-v1.md` - Windows-first routing and device selector requirements
  - External: `https://python-sounddevice.readthedocs.io/` - device enumeration and stream configuration
  - External: `https://vb-audio.com/Cable/` - named compatibility target for Windows validation

  **Acceptance Criteria** (agent-executable only):
  - [ ] `python -m pytest tests/integration/test_device_enumeration.py -q`
  - [ ] `python tools/routing_probe.py --targets "VB-CABLE,Voicemeeter" --json-out .sisyphus/evidence/task-8-routing.json`

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Routing compatibility happy path
    Tool: Bash
    Steps: Run `python tools/routing_probe.py --targets "VB-CABLE,Voicemeeter" --json-out .sisyphus/evidence/task-8-routing.json`
    Expected: Probe enumerates target devices when installed, reports compatible channel/sample-rate settings, and surfaces clear unsupported cases
    Evidence: .sisyphus/evidence/task-8-routing.json

  Scenario: Missing virtual-audio tools
    Tool: Bash
    Steps: Run `python -m pytest tests/integration/test_missing_virtual_device_guidance.py -q`
    Expected: App reports compatibility guidance instead of failure when named tools are absent
    Evidence: .sisyphus/evidence/task-8-routing-error.json
  ```

  **Commit**: YES | Message: `feat(audio): validate routing compatibility and backend adapters` | Files: `src/audio/`, `src/runtime/`, `tools/routing_probe.py`, `tests/integration/`

- [ ] 9. Add telemetry, diagnostics panel, and performance evidence harness

  **What to do**: Instrument callback timing, queue depth, dropped frames, resample count, warm-up time, provider used, actual provider used, state transitions, stage-by-stage latency, and audio-quality metrics; expose a user-facing diagnostics summary plus a developer-facing diagnostics export; extend harnesses to emit machine-readable evidence used for release gating; add long-run soak harnesses.
  **Must NOT do**: Do not emit verbose logs from the callback thread; do not make telemetry optional for release verification; do not mix end-user summary fields with developer-only debugging detail in one undifferentiated panel.

  **Recommended Agent Profile**:
  - Category: `deep` - Reason: performance visibility is required to judge correctness of the real-time system
  - Skills: `[]` - platform-internal work
  - Omitted: `['/git-master']` - not a history operation

  **Parallelization**: Can Parallel: YES | Wave 6 | Blocks: `10` | Blocked By: `3`, `4`, `5`, `6`, `7`

  **References**:
  - Baseline: `.sisyphus/plans/real-time-voice-changer-v1.md` - latency targets, observability, and evidence expectations
  - External: `https://docs.pytest.org/` - structured test assertions
  - External: `https://pytest-qt.readthedocs.io/` - diagnostics panel verification

  **Acceptance Criteria** (agent-executable only):
  - [ ] `python -m pytest tests/integration/test_metrics_export.py -q`
  - [ ] `python -m pytest tests/ui/test_diagnostics_panel.py -q`
  - [ ] `python -m pytest tests/ui/test_diagnostics_audience_split.py -q`
  - [ ] `python -m pytest tests/integration/test_soak_runner.py -q`
  - [ ] `python tools/pipeline_harness.py --mode ai_onnx --model models/default/default.onnx --input tests/fixtures/voice_48k_mono.wav --expect-provider any --expect-state ready --json-out .sisyphus/evidence/task-9-telemetry.json`

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Telemetry happy path
    Tool: Bash
    Steps: Run `python tools/pipeline_harness.py --mode ai_onnx --model models/default/default.onnx --input tests/fixtures/voice_48k_mono.wav --expect-provider any --expect-state ready --json-out .sisyphus/evidence/task-9-telemetry.json`
    Expected: JSON evidence includes callback timing, queue depth, dropped frames, warm-up time, provider used, actual provider used, stage-by-stage latency, loudness delta, clipping ratio, and final state
    Evidence: .sisyphus/evidence/task-9-telemetry.json

  Scenario: Overload diagnostics path
    Tool: Bash
    Steps: Run `python -m pytest tests/integration/test_overload_metrics_visibility.py -q`
    Expected: Overload/fallback events appear in exported metrics and UI diagnostics without crashing the pipeline
    Evidence: .sisyphus/evidence/task-9-telemetry-error.json

  Scenario: Soak and drift verification
    Tool: Bash
    Steps: Run `python -m pytest tests/integration/test_soak_runner.py -q`
    Expected: Soak harness covers `30 min` bypass, `30 min` DSP, `15 min` AI CPU, and `15 min` AI GPU when available; memory growth, queue-depth drift, dropped-frame trend, callback exceptions, and stale-worker count stay within release thresholds
    Evidence: .sisyphus/evidence/task-9-soak.json
  ```

  **Commit**: YES | Message: `feat(obs): add telemetry diagnostics and evidence export` | Files: `src/utils/`, `src/ui/`, `tools/`, `tests/integration/`, `tests/ui/`

- [ ] 10. Finish packaging readiness and release gate after stability passes

  **What to do**: Add Windows packaging configuration, offline model asset layout, settings persistence defaults, and a release checklist that only activates after tasks `1-9` pass; compare `PyInstaller` smoke packaging against a `pyside6-deploy` feasibility spike; choose the final packaging path with a deterministic rule based on launch stability, asset inclusion, startup time, and bundle size; and separate read-only install assets from writable app data/config/cache/evidence directories using Qt standard paths.
  **Must NOT do**: Do not start packaging before telemetry/routing evidence is green; do not bundle a virtual-audio driver; do not store writable evidence, user-imported models, or mutable settings in the install directory.

  **Recommended Agent Profile**:
  - Category: `writing` - Reason: combines packaging config, release documentation, and final smoke verification
  - Skills: `[]` - no specialty skill required
  - Omitted: `['/frontend-ui-ux']` - visual redesign is not the goal here

  **Parallelization**: Can Parallel: NO | Wave 7 | Blocks: none | Blocked By: `7`, `8`, `9`

  **References**:
  - Baseline: `.sisyphus/plans/real-time-voice-changer-v1.md` - packaging guardrails and Windows-first execution requirement
  - External: `https://pyinstaller.org/en/stable/` - Windows packaging reference
  - External: `https://doc.qt.io/qtforpython-6/` - deployment caveats for PySide6 apps
  - External: `https://doc.qt.io/qtforpython-6/deployment/index.html` - official Qt for Python deployment options and recommendation for `pyside6-deploy`
  - External: `https://doc.qt.io/qt-6/qstandardpaths.html` - writable app-data/config/cache path rules for packaged apps

  **Acceptance Criteria** (agent-executable only):
  - [ ] `python -m pytest tests/smoke/test_packaged_launch.py -q`
  - [ ] `pyinstaller --noconfirm app.spec`
  - [ ] `pyside6-deploy src/main.py`
  - [ ] `python -m pytest tests/smoke/test_standard_paths_layout.py -q`

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Packaged app smoke path
    Tool: Bash
    Steps: Run `pyinstaller --noconfirm app.spec`; run `pyside6-deploy src/main.py`; run the selected packaged binary in `--no-audio --diagnostics` mode
    Expected: At least one packaging path passes launch smoke; the chosen path is the one that passes all smoke checks with writable paths resolved via Qt standard locations and with no network access required
    Evidence: .sisyphus/evidence/task-10-packaging.json

  Scenario: Missing model asset path
    Tool: Bash
    Steps: Run `python -m pytest tests/smoke/test_missing_model_asset.py -q`
    Expected: Packaged/runtime startup reports clear local asset guidance and falls back to DSP/bypass instead of crashing
    Evidence: .sisyphus/evidence/task-10-packaging-error.json

  Scenario: Writable path separation
    Tool: Bash
    Steps: Run `python -m pytest tests/smoke/test_standard_paths_layout.py -q`
    Expected: Default model in install assets is read-only, while imported models, settings, cache, and evidence resolve to writable Qt standard paths outside the install directory
    Evidence: .sisyphus/evidence/task-10-standard-paths.json
  ```

  **Commit**: YES | Message: `chore(release): add packaging and release gate` | Files: `app.spec`, packaging assets, `tests/smoke/`, release docs/config

## Final Verification Wave (MANDATORY - after ALL implementation tasks)
> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.
> **Do NOT auto-proceed after verification. Wait for user's explicit approval before marking work complete.**
> **Never mark F1-F4 as checked before getting user's okay.** Rejection or user feedback -> fix -> re-run -> present again -> wait for okay.
- [ ] F1. Plan Compliance Audit - oracle
- [ ] F2. Code Quality Review - unspecified-high
- [ ] F3. Real Manual QA - unspecified-high (+ playwright if UI)
- [ ] F4. Scope Fidelity Check - deep

  **Final QA Scenarios**:
  ```text
  Scenario: F1 compliance audit
    Tool: Bash
    Steps: Run the designated oracle review agent against completed work and compare outputs against `.sisyphus/plans/real-time-voice-changer-v1.md`
    Expected: Oracle reports no deviations on scope, task ordering, runtime choice, fallback policy, or verification requirements
    Evidence: .sisyphus/evidence/f1-plan-compliance.md

  Scenario: F2 code quality review
    Tool: Bash
    Steps: Run the designated code-quality review agent across changed files and capture findings
    Expected: No unresolved high-severity maintainability, safety, or architecture issues remain
    Evidence: .sisyphus/evidence/f2-code-quality.md

  Scenario: F3 manual QA replay
    Tool: Bash
    Steps: Re-run packaged smoke tests plus pipeline harnesses for bypass, DSP, AI, routing, and UI suites; aggregate results into one report
    Expected: All scripted QA passes and evidence artifacts exist for each major mode and failure path
    Evidence: .sisyphus/evidence/f3-manual-qa.md

  Scenario: F4 scope fidelity audit
    Tool: Bash
    Steps: Run the designated deep review agent to compare delivered files and features against the plan's IN/OUT scope rules
    Expected: No out-of-scope features were added and no required v1 features are missing
    Evidence: .sisyphus/evidence/f4-scope-fidelity.md
  ```

## Commit Strategy
- Follow the atomic ladder defined in the TODO section; do not squash unrelated real-time engine and UI work together.
- Require a runnable command or passing test/harness for every commit.
- Push every completed implementation commit immediately to `origin main`; do not batch multiple task completions into one delayed push.
- Create `README.md` in Task 1 and keep it updated when scope, setup, or delivery status materially changes.
- Defer packaging commit(s) until telemetry and routing validation already pass.

## Success Criteria
- Live microphone input can be transformed and played back without callback-thread stalls.
- DSP mode is stable on CPU reference hardware within the defined latency target.
- AI mode works offline with ONNX Runtime, warms in the background, and degrades safely to DSP/bypass on failure.
- UI accurately reflects pipeline state, device/model readiness, and failure conditions.
- Windows routing compatibility is validated against named third-party virtual-audio setups.
- Automated evidence artifacts exist for unit, integration, UI, routing, latency, warm-up, fallback, quality, soak, and packaging paths.
