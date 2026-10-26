import pathlib, sys, time
mode = sys.argv[1]
print("OUT-READY", flush=True)
print("ERR-READY", file=sys.stderr, flush=True)
if len(sys.argv) > 2:
    pathlib.Path(sys.argv[2]).write_text("ready", encoding="utf-8")
if mode == "nonzero":
    sys.exit(7)
if mode == "sleep":
    time.sleep(10)
