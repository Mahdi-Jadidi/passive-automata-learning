# P2.1 — independent SharedGateway re-audit (issue #10)

This supersedes the **separate-ledger** interface findings in [P21_ROUNDTRIP.md](P21_ROUNDTRIP.md) for the newer pinned SharedGateway. Core remains pinned at 539af04bb0b097de5704c28f2b82f23cea5ef783; new interface b27850a667a55927fd3ad127dccce3956d8ead22. No external learner calls, no operational acceptance, no merge. A clean git checkout remains blocked by DNS; actual source bytes reconstructed from GitHub and checked against published blob identities.

## Executed evidence

Rebuilt the actual interface exporter in normal and optimized Python with the pinned core and interface. Both files matched the published contents exactly (SHA-256):
- roundtrip_bundle.json (16592 bytes): 1ec8d4c2d13910c0803339e1d21737716855b929511b1c56b299672b48d7ba35
- roundtrip_journal.json (7514 bytes): 425c3f4da1908592e64c9b0f94ed039ba7ebb18bf3ca5815a10f843d892aa392

Independent replay in tests/reference/shared_artifact_replay.py reads actual journal, registrations, artifacts and quarantine; rederives raw structural conclusions and wire semantics, including full DFA validation, and compares converted records to the journal. It does not import producer or adapter code. Driver audit_shared_gateway.py imports actual public producer/gateway APIs for behavioral checks only.

Reproduction from proof branch tests/reference, with CORE_DIR pointing to implementation/partition_feedback_final of pinned core and INTERFACE_DIR to research/interface/p2 of pinned interface. Run the actual pinned export_roundtrip.py with the pinned core on PYTHONPATH, passing the desired output directory as documented by the interface. Then:
```sh
python audit_shared_gateway.py "$CORE_DIR" "$INTERFACE_DIR" "$EXPORT_DIR"
python -O audit_shared_gateway.py "$CORE_DIR" "$INTERFACE_DIR" "$EXPORT_DIR"
```
Normal and optimized audit output matched byte-for-byte; actual output:
```text
blob core.py 997304c3adce9d3148d454b079639575f419ba0e
blob schema.py 65a7522a8442a184c14f7a0fa74fc307ce60229f
blob sparse_analysis.py f773cc1c6b1a852193ba2afb75aa2fce4941a5c2
blob component_closure.py 97844bc266556cc04cd54a75c0d57dc00d6709ea
blob evidence_store.py 42e38c8ee590267b292ebc0d678e9d4f3a56849b
blob adapter.py c38e441c7327a44adad8a0fe1125d45c93e8ef69
blob strict_ledger.py a66975de137e3ec556b8c7aacd108cf975c46344
blob shared_gateway.py 33ef122814c409cc7c0d201b0cb4c3127b078862
blob export_roundtrip.py ddd211111322ff1bae9c7e2a0c0f4eaef40c9d75
blob test_adapter.py bfa7dee3373da7d267c373e238b95d271a8a2669
published_case=0 records=12 optimum=1 registrations=5 artifacts=4 observations={'UNKNOWN': 1, 'PROJECTION_NO': 1, 'ACCEPT': 1, 'BOUNDED_NO': 1} pending_attempts=2 operational=INCOMPLETE
published_case=1 records=4 optimum=2 registrations=0 artifacts=0 observations={} pending_attempts=0 operational=INCOMPLETE
actual_published_export_mutations_rejected=16
latest_gateway_global_reuse=REJECTED origin_rebind=REJECTED duplicate_receipt=UNKNOWN_ONLY raw_atomic_rollback=PASS invalid_response_rollback=4 unknown_retry=PASS concurrent_deliveries=16 committed=1
latest_gateway_false_exhaustion=CORE_ACCEPTED_INDEPENDENT_REJECTED sidecar_authentication=NOT_ESTABLISHED operational_status=INCOMPLETE
```

The two structural optima are unrestricted costs, not operational optima. Pending attempts are a ledger property, not a search-frontier proof. The simulated ACCEPT and external-shaped test callback confer no operational authority. The 16 mutations are actual-export modifications, not claims of 16 independent bug classes.

## Disposition

The previous separate-ledger divergences are **closed on the tested in-memory SharedGateway path**: global attempt ID reuse and registration-origin rebinding reject without state change; repeated receipt yields UNKNOWN-only, without second semantic observation; timeout/retry and raw/invalid-response rollback preserve existing records. Sixteen concurrent deliveries commit exactly one observation. This is not a durable transaction/recovery proof.

**P2.1 gate remains open.** Actual core accepts a forged EXHAUSTED flag on a zero-budget PARTIAL epoch; independent replay rejects it. Exhaustion is producer metadata, not an independently established proof; no downstream pruning/closure based solely on that metadata. Bare core records still do not bind trusted origin. Shared export registrations/artifact sidecars are internally checked, not authenticated; an adversarial coordinated replacement cannot be ruled out from self-consistency alone. Durable persistence/atomic crash recovery, owner-approved live transport and authenticated receipts, capacity-policy approval, candidate-level pending frontier and actual proof consumer integration remain outstanding. Clean checkout CI also not established. Do not begin P3 on this evidence alone.

Commits: 3ffdbc299a9e57ea1363726ea8a56e7bb858bc37 independent SharedGateway replay (blob e024c37642ad4dc3c125a444e768f84d6fced548); 9b1bfdbac6993cc7fabbd44c0f7c43e06ba48685 actual gateway test driver (blob 5819d549241f3be69524252abde20b3d5b159abb). Both committed blob identities match locally executed source.
