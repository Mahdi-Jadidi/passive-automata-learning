# Review 09 M4 sparse RAW pipeline reproduction

Run on Ubuntu 24.04 with CPython 3.13.5. Check out the producer, verifier and
interface commits listed in the pipeline configuration in separate directories.
The runner validates each staged blob and the original RAW SHA-256.

```bash
python -B benchmarks/v2/review09_pipeline.py --case medium_choice --memory-mib 512 \
  --journal-origin retained --producer source-core --verifier source-proof \
  --interface source-interface --output pipeline-retained
python -B benchmarks/v2/review09_pipeline.py --case medium_choice --memory-mib 512 \
  --journal-origin fresh --producer source-core --verifier source-proof \
  --interface source-interface --output pipeline-fresh
```

The matrix substitutes the four original large fixture names and 512 or 1536 MiB.
Each job runs one/all, normal/-O and fresh search/checkpoint-resume. Each route
shares a single 30 s deadline. Child processes receive the remaining wall budget
and cooperative stages receive at most 25 s. The checkpoint uses a one-entry cap.
The producer runs with --sparse, the independent replayer with --sparse-exact,
and replay binds frontier v2 and the requested mode. Stage arguments and
effective wall caps are recorded in the JSON. The immutable producer uses its
default 64 MiB compatibility index cap. The RAW closure uses 10 million work
units and the producer and verifier limits are in the pipeline configuration. The retained arm independently reconstructs the
scope and checks byte equality before handing the archived scope to the producer.
Review08 stored medium and huge directly. The HDFS bytes were recovered from the
one-normal-fresh directories of the two 512 MiB artifacts in Actions run
45832542233 and checked against the published hashes and lengths.
The fresh arm generates its own journal in each route, then derives its scope
independently. Any incomplete outcome stays censored.

```bash
repo=Mahdi-Jadidi/passive-automata-learning
run=46014832411
gh run download "$run" -R "$repo" -p 'review09-pipeline-*' -D review09-download
gh run view "$run" -R "$repo" --json databaseId,status,conclusion,headSha,url,jobs \
  --jq '{databaseId,status,conclusion,headSha,url,jobs:[.jobs[]|{databaseId,name,conclusion,url}]}' \
  > review09-ci.json
python -B benchmarks/v2/review09_export.py review09-download review09-ci.json \
  benchmarks/v2/results/review09
```
