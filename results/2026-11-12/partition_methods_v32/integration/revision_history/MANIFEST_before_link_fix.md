# SHA-256 manifest — integration release candidate

Recorded 2026-11-12. Paths are relative to `partition_methods_v32/`. Hashes bind bytes, not correctness. Circular dossier reviews have passed for the listed source hashes. Independent review of the integrated documents is pending; if any listed file changes, recompute its hash and re-evaluate the applicable review before release. The manifest does not hash itself.

| File | SHA-256 |
|---|---|
| `package_a/METHODS_1_2_3_6.md` | `874565D4C99268AB0183AB4BC2415B54AF2F5CE4FA688BA45BE56DF17E912657` |
| `package_b/REVIEW_A.md` | `411A6B0A275485CBC728EB8EA4CA621413C5309C3B6F9E81E37C39145D4D3311` |
| `package_b/DOSSIERS_4_5_9_10.md` | `52A394CF3B93E43250DA45F805EDD93D939B45212A2D8F954843DA959330B8C6` |
| `package_c/REVIEW_B.md` | `FEFDDBDDD4B4DA0C65BFC6694E82A1CBA4675220DCD946AAA2AB0C2C65A29C32` |
| `package_c/METHODS_7_8_11_14.md` | `FE822EB7EE46A68371CE61D6F33276F6AAC7E9C233F378F2C8D7B24658DD3FE6` |
| `package_a/REVIEW_C.md` | `FF2AC7ADF91C397BD8A7CF4D914CD24D8B3DBEB290924C9F28324F04C5FA8953` |
| `integration/REPORT_EN.md` | `2C0D5F2F3967B1E44CCCC9FB43C481668F031B9D44EE86985518C5B376E87630` |
| `integration/COMPARISON.md` | `6F5CB531AB1370F0B96B0A9C5CAF63C3895461E5A552357D766798B5CCAF575A` |
| `integration/WALKTHROUGH_FA.md` | `9668C146AFB82A214107CE39116836C72E593334E33422F2CA5CE9ECE08D480B` |

A was reviewed by B, B by C, and C by A; each final review specifies its reviewed hash and qualifications. These are coordinated AI reviews, not human peer review, formal verification, or a complete literature audit. Dossiers contain no new implementation or benchmarks. In particular, decision-equivalent auxiliary graph construction does not establish parsimonious counting or a single-instance objective-preserving graph reduction; the latter is OPEN here. Active learning and statistical assumptions may change the problem and have no unqualified physical-identification guarantee.
