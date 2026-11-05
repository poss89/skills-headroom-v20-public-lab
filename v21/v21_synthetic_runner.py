#!/usr/bin/env python3
"""V21: bounded, offline, synthetic Headroom 0.42.0 agent-densify fixture.
Never run outside the network-denied Docker sandbox of the V21 workflow.
No secrets, real transcripts, model calls, proxy, MCP, or persistent memory.
"""
import copy
import importlib.metadata
import json
import os
import resource
import sys
import time

EXPECTED_VERSION = "0.42.0"
TRIALS = 3

def fixtures():
    rows = [
        {
            "event_id": f"EVT-{i:04d}",
            "status": "ok" if i != 67 else "FATAL",
            "service": "synthetic-service",
            "region": "eu-test-1",
            "category": "sandbox-only",
            "retries": i % 3,
            "message": "FATAL_SENTINEL_AT_ROW_67" if i == 67 else "No action required",
        }
        for i in range(160)
    ]
    tabular = "event_id,status,service,region,category,message\n" + "\n".join(
        f"EVT-{i:04d},ok,synthetic-service,eu-test-1,sandbox-only,NO_REAL_DATA"
        for i in range(100)
    )
    diff = "--- a/test.txt\n+++ b/test.txt\n@@ -1,4 +1,4 @@\n" + (
        "-mode=inactive\n+mode=active\n unchanged=synthetic\n"
    ) * 16
    prose = (
        "This paragraph is intentionally fictional. An agent should preserve every "
        "fact even when the prose is not compressible. Marker: PROSE_SENTINEL_42. "
    ) * 15
    cases = {
        "json_table": json.dumps(rows, ensure_ascii=False, separators=(",", ":")),
        "csv_table": tabular,
        "diff": diff,
        "prose": prose,
        "malformed_text": "{not valid json,,,\n\t\u00ff\u03a9 END_SENTINEL",
        "empty": "",
    }
    return {name: [{"role": "tool", "content": value}] for name, value in cases.items()}

def peak_cgroup_bytes():
    for path in ("/sys/fs/cgroup/memory.peak",):
        try:
            return int(open(path, encoding="ascii").read().strip())
        except (OSError, ValueError):
            continue
    return None

def main():
    if os.environ.get("V21_SYNTHETIC_ONLY") != "1":
        raise RuntimeError("Explicit synthetic-only environment guard missing")
    if os.environ.get("HEADROOM_OFFLINE") != "1":
        raise RuntimeError("HEADROOM_OFFLINE flag missing")
    if importlib.metadata.version("headroom-ai") != EXPECTED_VERSION:
        raise RuntimeError("Wrong Headroom version")

    import_started = time.perf_counter()
    from headroom import densify
    # Internal source-level round-trip verifier, NOT an independent proof.
    from headroom.compress import _message_is_lossless
    import_seconds = time.perf_counter() - import_started

    metrics = []
    compressed_cases = 0
    cases = fixtures()
    for label, input_messages in cases.items():
        outputs = []
        observed = []
        for trial in range(TRIALS):
            working = copy.deepcopy(input_messages)
            preserved = copy.deepcopy(working)
            started = time.perf_counter()
            result = densify(
                working, model="gpt-4o", model_limit=128000,
                hooks=None, protect_recent=0,
            )
            elapsed_ms = (time.perf_counter() - started) * 1000
            if working != preserved:
                raise AssertionError(f"{label}: input mutated")
            if result.lossless is not True:
                raise AssertionError(f"{label}: lossless flag is not True")
            if len(result.messages) != len(input_messages):
                raise AssertionError(f"{label}: message count differs")
            for orig, out in zip(input_messages, result.messages):
                if out != orig and not _message_is_lossless(orig, out):
                    raise AssertionError(f"{label}: failed internal round-trip")
            b = int(result.tokens_before)
            a = int(result.tokens_after)
            s = int(result.tokens_saved)
            if b < 0 or a < 0 or s < 0:
                raise AssertionError(f"{label}: negative tokens")
            if b and a > b:
                raise AssertionError(f"{label}: token inflation")
            # A zero-count passthrough is NOT counted as a compression success.
            is_valid_measurement = b > 0 and a > 0 and s == (b - a)
            if s > 0 and is_valid_measurement:
                compressed_cases += 1 if trial == 0 else 0
            outputs.append(json.dumps(result.messages, sort_keys=True, ensure_ascii=False))
            observed.append({
                "trial": trial + 1,
                "elapsed_ms": round(elapsed_ms, 2),
                "tokens_before": b,
                "tokens_after": a,
                "tokens_saved": s,
                "reverted_messages": int(result.reverted_messages),
                "changed": result.messages != input_messages,
                "valid_token_measurement": is_valid_measurement,
            })
        if len(set(outputs)) != 1:
            raise AssertionError(f"{label}: nondeterministic output")
        metrics.append({"fixture": label, "trials": observed})

    print(json.dumps({
        "scope": "HEADROOM_0.42.0_AGENT_DENSIFY_SYNTHETIC_ONLY",
        "verification_limit": "Headroom internal round-trip check, not independent security proof",
        "import_seconds": round(import_seconds, 3),
        "peak_process_rss_kb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "peak_cgroup_bytes": peak_cgroup_bytes(),
        "compressed_fixture_count": compressed_cases,
        "fixtures": metrics,
    }, sort_keys=True))
    if compressed_cases == 0:
        print("PARTIAL: no verified positive token compression observed", file=sys.stderr)
        return 4
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"FAIL_SCOPED: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(2)
