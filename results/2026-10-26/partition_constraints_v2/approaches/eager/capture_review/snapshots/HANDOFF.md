# Durable capture candidate B-CAPTURE-R1

Status: candidate implemented, seven isolated initial checks passed; independent
auditor review/adoption pending. Only this capture_support/ folder was written.
No provider, common runtime, audit source or Git state was modified by this task.

## Adoption interface

capture_candidate.py retains capture(label, command, *, cwd=None,
timeout_seconds=30.0, source_paths=None), the existing returned fields, environment
allowlist and CLI options. When adopted by the auditor as audit/capture.py,
its __file__-derived AUDIT_DIR automatically relocates attempts/source_blobs to
audit/. It must not be promoted as provider/runtime source. Original capture bytes
are preserved under original/ with the original SHA256 in ORIGINAL_MANIFEST.json.

stdout.bin/stderr.bin exist before launch and are the actual direct-child output
destinations, not buffered parent PIPEs. Finalization fsyncs those file handles.
Output not yet flushed from the child application's own buffers is unrecoverable.
Snapshots retain source_paths byte-for-byte in content-addressed blobs; input
files must also be explicitly supplied through source_paths. Snapshot hash errors
are distinct from scientific solver results. Sources are not automatically
discovered from imports; callers remain responsible for complete dependencies.

KeyboardInterrupt during controlled capture execution is classified interrupted.
The direct child is terminated if still alive, then waited/reaped; terminate
escalates to kill after a one-second wait. Repeated cooperative interrupts during
cleanup retry rather than abandon that child. Only the Popen object created by
this call is controlled; no foreground user process or unrelated PID is touched.
Grandchildren/process trees are not managed. An unexpected cleanup failure is
reported as capture_error with primary_execution_status and cleanup_error.

Raw execution statuses remain success, program_error, timed_out,
environment_error and capture_error, with interrupted added. scientific_status
remains not_assessed even for raw success: a returned solver incomplete JSON is
not converted into scientific success here. Actual terminated-child exit_code is
retained on timeout/interrupt, unlike the original null exit_code in those cases.
Callers must classify by execution_status, not reinterpret terminated exit code
as a normal solver error. CLI interrupted exits 130; other status mappings remain.

subprocess_seconds measures from the Popen launch attempt through direct-child
termination/reaping, excluding source snapshots, environment/manifest generation,
output hashing and file finalization. It includes process startup and cleanup;
failed spawn attempts can have positive elapsed time. duration_seconds retains
the broader instrumentation clock through output hashing/result assembly, before
writing result.json itself. Neither field should be mislabeled pure solver CPU
time. The timeout controls wait after creation; Python process creation is not
preempted by this mechanism.

Abrupt capture-process termination, power loss, failed storage, interruption in
initial setup/final metadata writing, or a signal during a Popen constructor
before its object is returned may prevent complete final metadata. Started
attempts need supervisor reconciliation; this candidate does not promise every
abrupt kill finalizes a result. Already flushed output files can remain useful.

## Immutable initial checks

Outer captured CLI run:
attempts/20261026T125946.616606Z_fc6a0e33dd/

manifest.json records exact command, environment, code/source hashes and blobs.
stdout.bin contains complete structured results for all seven cases and their
unique attempt directories; stderr.bin is empty and result.json reports exit 0.
The scenarios were success, exit 7, timeout after flushed stdout/stderr,
nonexistent executable, simulated interrupt after the child's flushed readiness
marker, snapshot-delay clock separation, and prelaunch simulated interruption.
Every result and stream hash was checked after being saved. Every launched child
had child_reaped=true. The simulated interrupt patched Popen.wait once inside an
isolated selftest process; it sent no OS signal and interrupted no foreground app.

The clock-separation case inserted a 0.25-second snapshot delay; the difference
between duration_seconds and subprocess_seconds included that delay. This is a
clock-boundary check, not a benchmark or speed claim. Successful/nonzero exit
codes, raw status distinctions, byte counts/content hashes, immutable source blob
hashes, unique IDs and retained partial output were checked. No failed candidate
run was discarded or replaced. No independent empirical certification is claimed.
