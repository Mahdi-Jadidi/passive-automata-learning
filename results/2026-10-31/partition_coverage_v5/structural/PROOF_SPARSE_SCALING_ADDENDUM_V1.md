# Sparse scaling addendum v1

This is a separate corpus addendum. It does not mutate the auditor's frozen core corpus. Runtime remains sparse_certificate_v2.py, SHA256 1ff16263322f2009d68cd2b4ecc3b6587fa9ef80695fa9489fb199c9e13d6705.

Start from two base words acbde, ebadc. Replace each original symbol x by an ordered nonempty clone list C_x, using the identical contiguous clone order at every occurrence. Add t=k-3 fresh singleton anchors: prefix them in forward order to the first word, suffix them in reverse order to the second. Let m be the total clone plus anchor count. For q>=1 and a fixed event repeat R>=1, produce both words with every individual symbol event repeated R*r times, for r=1,...,q. There are 2q positives, of lengths mR,...,mqR (each twice).

For any pair of clones of the same original symbol, relative order is fixed across both bases; for clones of distinct originals, relative order is fixed or inverted exactly as in the original pair. Anchors invert relative order with every clone and with each other. Across r values all pair count vectors differ. Therefore a fixed-order pair has exactly q distinct projections; an inverted-order pair has exactly 2q>q. The derived opposition graph is the clone blow-up of the 7-edge base graph joined to a t-clique. Each C_x is independent; all anchor vertices join every other group. This is an ACTUAL sample projection statement, not a synthetic graph injection.

The graph has a k-clique formed by one representative each from C_b,C_c,C_e and all anchors. It forces every C_a vertex via C_b,C_e and anchors, every C_d via C_c,C_e and anchors; remaining C_b,C_c,C_e clones are forced by the other two anchor colors and singleton anchors. Every vertex is forced. The full projection blocks are C_a union C_c, C_b union C_d, C_e, and each singleton anchor. Their fixed internal order is the same in both base words, so each has exactly q full words across distinct R*r counts. A negative empty word is rejected because all block words are nonempty.

The only missing cross-color rectangle relative to the corresponding complete multipartite graph is C_a x C_d. Thus the derived graph is strictly less dense whenever clone lists are nonempty. This lift is still fairly dense as k increases because the new anchors are universal; do not call it asymptotically sparse in edge count. The proven relaxation is removal of the complete multipartite requirement.

Capture 20261031T064256.626868Z_ca453dc10c ran only branch correctness sanity; no official timing or method comparison. It snapshots provider, generator and protocol before generating/logging each input and solving it. All eight cells passed own assertions. Full raw stdout (17,758,549 bytes) preserves inputs and full provider results. The materialized fixture was extracted after execution and accurately labels that provenance; it is a new input-only addendum for independent capture.

|m|k|R|q tested|maximum positive length|opposition edges|complete multipartite edges|
|--:|--:|--:|:--|--:|--:|--:|
|256|16|1|1,2,3,4|256,512,768,1024|19751|22103|
|16|6|512|1,2,3,4|8192,16384,24576,32768|88|94|

The m256/k16 blocks have sizes 98,97,48, then thirteen singleton anchors. Clone sizes are 49,49,49,48,48. The missing rectangle has 49*48=2352 edges. The m16/k6 clone sizes are 3,3,3,2,2, with three anchors; output block sizes6,5,2,1,1,1. Missing rectangle is3*2=6. These maxima are attained in separate cells; no claim that m256/k16 simultaneously attained length32768.

Files and hashes:

* sparse_scaling_v1.py: f0a8c5b74da621540f74b2011627ba37bc5bc74ae0b33bbbca7d27f4c2fcca72
* sparse_scaling_protocol_v1.json: b2f5e9ed07a070768d47b30198d37460e6a399c3e4763554ac9613d1abf7e0a2
* sparse_scaling_fixtures_v1.json: d6b8398e9a8c85d8f3c2f65cb87a9518ea7ffefade56a9e42c0d46ae6e8c084c

Independent acceptance remains auditor responsibility. The complete graph cannot be replaced by only pair checks in either method; full cap and negative validation remain essential.
