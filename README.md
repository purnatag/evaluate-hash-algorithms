# Evaluation Pipeline for TLSH (and other hashing schemes)
---

This repository contains the file `eval.py`, used to evaluate the quality of compression exhibited by the hashing schemes `tlsh`, `ssdeep` and `sdhash` on system event signature logs.
The metrics for evaluation are --
- Computation of locality or change ratio which is %change in hash/%change in the input signature.
- Mean gaps between the changes in the hash value, and variance
- Mean and variance of the distribution of deltas on modified input signatures versus Mean and variance of deltas on hash values. Here ~deltas~ refers to % change per original signature length and % change per original hash length, respectively.
