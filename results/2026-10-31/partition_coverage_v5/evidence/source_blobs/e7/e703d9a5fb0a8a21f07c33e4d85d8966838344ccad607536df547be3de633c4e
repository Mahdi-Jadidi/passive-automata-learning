# Frozen corpus v2 provenance note

The v2 corpus was generated in a separate `frozen_corpus_v2/` directory by
`generate_corpus_v2.py` with seed 20261031. Its captured generation attempt is
`20261101T053153.859440Z_9701cf17df`. That capture snapshots the generator and
`corpus_protocol_v1.json` before execution. The v2 generator deduplicates each
random word pool before assigning exact labels, preventing one word from
being labeled both positive and negative. This is a correction to the v1
generator implementation; it does not alter the frozen v1 corpus or its
captured gate result. The manifest and freeze record retain their v1 schema
filenames as emitted by the versioned generator.

The gate protocol v2 names the exact v2 manifest hash and source hashes.
No provider had been run against corpus v2 when this note and that protocol
were prepared.
