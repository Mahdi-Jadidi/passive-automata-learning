# C008 literature source notes — v1

Research access date for every source below: **2026-11-02** (Asia/Tehran). Notes are paraphrases and distinguish what a source proves from how it relates to C008.

## 1. Compositional automata learning by alphabet refinement

**Léo Henry, Thomas Neele, Mohammad Reza Mousavi, Matteo Sammartino.** “A Detailed Account of Compositional Automata Learning through Alphabet Refinement.” arXiv:2504.16624v3, revised 2026-04-01. Primary version page: [arXiv v3](https://arxiv.org/abs/2504.16624v3); [full text](https://arxiv.org/html/2504.16624v3); DOI: [10.48550/arXiv.2504.16624](https://doi.org/10.48550/arXiv.2504.16624).

**Attributed notes.** The paper models a system as a deterministic LTS whose finite trace language is prefix-closed. A distribution is a family of component alphabets that covers the global alphabet; alphabets may overlap, and a symbol in more than one alphabet is synchronizing. The paper uses global membership/equivalence-query interaction and derives local observations from finite global observations. Proposition 5 characterizes when a distribution models the finite observation function; Theorem 18 shows that the paper's refinement process reaches *some* observation-modeling distribution after finitely many refinements. Its “canonical distribution” removes redundant contained alphabets while retaining the same connecting power (Proposition 19).

**Relevance and limit.** This is the closest source for *active* compositional learning with unknown alphabet distribution. Its query model and overlapping synchronization alphabets differ from C007/C008's finite passive ± sample and disjoint ownership partition. Its termination/correctness result is about learning the global LTS language with a sound distribution, not a theorem that the returned distribution equals physical ownership. The paper's canonical-distribution operation is not the prime disjoint factorization defined in the C008 critique.

## 2. Gold: limit identification and finite stopping

**E. Mark Gold.** “Language Identification in the Limit.” *Information and Control* 10(5), 447–474 (1967). DOI: [10.1016/S0019-9958(67)91165-5](https://doi.org/10.1016/S0019-9958(67)91165-5). The original article was consulted through this [author-hosted scan](https://homepages.math.uic.edu/~lreyzin/papers/gold67.pdf).

**Attributed notes.** Gold distinguishes a positive-only “text” from an “informant” that presents labeled membership information for every string. His result table says the class of regular languages is identifiable in the limit from an informant. It also states that the positive-text model is weaker: classes containing all finite languages and an infinite language fail its limit-identification criterion (Theorems I.8–I.9 for specified text/naming models). The paper separately distinguishes convergence in the limit from finite identifiability: the learner is not told at a finite time that its current answer is correct.

**Relevance and limit.** The informant model is a useful contrast for a stream that eventually labels every word. It does not give a finite-sample ownership guarantee, and its positive-text impossibility theorem must not be applied as though it covered finite samples with both positive and negative labels. Neither model identifies hardware component IDs from an extensional language.

## 3. Passive inference and characteristic samples

**Mrudula Balachander, Emmanuel Filiot, Raffaella Gentilini.** “Passive Learning of Regular Data Languages in Polynomial Time and Data.” In *CONCUR 2024*, LIPIcs 311, Article 10, pp. 10:1–10:21 (2024). [Primary Dagstuhl record](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CONCUR.2024.10); [open paper PDF](https://drops.dagstuhl.de/storage/00lipics/lipics-vol311-concur2024/LIPIcs.CONCUR.2024.10/LIPIcs.CONCUR.2024.10.pdf); DOI: [10.4230/LIPIcs.CONCUR.2024.10](https://doi.org/10.4230/LIPIcs.CONCUR.2024.10).

**Attributed notes.** The paper defines a finite positive/negative sample and consistency as accepting every positive and rejecting every negative. It recalls DFA RPNI and states the characteristic-sample guarantee: a consistent hypothesis is returned for finite samples, while a characteristic sample for the target suffices for recovery of its minimal automaton. Its own contribution gives a polynomial passive learner and polynomial-size characteristic samples for a deterministic register-automaton model over an infinite data domain.

**Relevance and limit.** This supports a disciplined two-stage view: after a correct ownership partition is known, local languages can be passively inferred under a characteristic-sample/model-size condition. It does not solve ownership discovery, nor does “consistent with the current sample” mean “the hidden language/factors have been identified.” The paper's main theorem concerns regular data languages, not C008's finite-alphabet product decomposition.

## 4. Shuffle factorization: a nearby but narrower uniqueness result

**Jean Berstel, Luc Boasson.** “Shuffle factorization is unique.” *Theoretical Computer Science* 273(1–2), 47–67 (2002). DOI: [10.1016/S0304-3975(00)00433-3](https://doi.org/10.1016/S0304-3975(00)00433-3). [Author-hosted paper PDF](https://www-igm.univ-mlv.fr/~berstel/Articles/2002ShuffleFactorizationUnique.pdf).

**Attributed notes.** The paper proves effective uniqueness (after normalization) when a *finite set of words* is represented as a shuffle of a multiset of individual words, with a special degeneracy around repeated copies of one symbol discussed in the article.

**Relevance and limit.** The operation is related because disjoint-alphabet component products are interleavings constrained by local projections. But its theorem is about factorizing finite word sets into word factors, not about arbitrary regular component languages, passive identification of a hidden alphabet partition, or physical ownership. It cannot be cited as a direct uniqueness theorem for C008.

## Search boundary

This is a bounded primary-source review, not a claim of exhaustive coverage. No secondary-source theorem was used to establish the impossibility example or the prime-factor uniqueness theorem in `INDEPENDENT_CRITIQUE_V1.md`; both are proved there directly from the product semantics.
