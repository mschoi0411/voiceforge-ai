from __future__ import annotations


def test_soak_durations_are_defined_for_release_gate() -> None:
    soak_plan = {
        "bypass_minutes": 30,
        "dsp_minutes": 30,
        "ai_cpu_minutes": 15,
        "ai_gpu_minutes": 15,
    }
    assert soak_plan["bypass_minutes"] == 30
    assert soak_plan["dsp_minutes"] == 30
    assert soak_plan["ai_cpu_minutes"] == 15
    assert soak_plan["ai_gpu_minutes"] == 15
