from typing import List

import numpy as np
from numba import njit


@njit(cache=True)
def pairwise_alignment(
    s1: str,
    s2: str,
    gap_penalty: int = -1,
    match_score: int = 2,
    mismatch_penalty: int = -1,
) -> tuple[str, str]:
    m, n = len(s1), len(s2)
    dp = np.zeros((m + 1, n + 1), dtype=np.int64)
    for i in range(m + 1):
        dp[i][0] = i * gap_penalty
    for j in range(n + 1):
        dp[0][j] = j * gap_penalty
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            match = dp[i - 1][j - 1] + (
                match_score if s1[i - 1] == s2[j - 1] else mismatch_penalty
            )
            delete = dp[i - 1][j] + gap_penalty
            insert = dp[i][j - 1] + gap_penalty
            dp[i][j] = max(match, delete, insert)
    # Traceback
    aligned1: str = ""
    aligned2: str = ""
    i, j = m, n
    while i > 0 or j > 0:
        if (
            i > 0
            and j > 0
            and dp[i][j]
            == dp[i - 1][j - 1]
            + (match_score if s1[i - 1] == s2[j - 1] else mismatch_penalty)
        ):
            aligned1 = s1[i - 1] + aligned1
            aligned2 = s2[j - 1] + aligned2
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i - 1][j] + gap_penalty:
            aligned1 = s1[i - 1] + aligned1
            aligned2 = "-" + aligned2
            i -= 1
        else:
            aligned1 = "-" + aligned1
            aligned2 = s2[j - 1] + aligned2
            j -= 1
    return aligned1, aligned2


@njit(cache=True)
def propagate_gaps_to_all(aligned_seqs, aligned_consensus):
    idx = 0
    for c in aligned_consensus:
        if c == "-":
            for k in range(len(aligned_seqs)):
                aligned_seqs[k] = aligned_seqs[k][:idx] + "-" + aligned_seqs[k][idx:]
            idx += 1
        else:
            idx += 1
    return aligned_seqs


@njit(cache=True)
def msa(
    sequences: List[str],
    gap_penalty: int = -1,
    match_score: int = 2,
    mismatch_penalty: int = -1,
):
    # Classic progressive alignment for short strings
    aligned = [sequences[0]]
    for seq in sequences[1:]:
        # Align current alignment to new sequence
        # Build a consensus string from current alignment
        consensus = ""
        maxlen_consensus = 0
        for s in aligned:
            length = len(s)
            if length > maxlen_consensus:
                maxlen_consensus = length
        for i in range(maxlen_consensus):
            chars = [s[i] if i < len(s) else "-" for s in aligned]
            # Most common non-gap char or gap
            filtered = [c for c in chars if c != "-"]
            consensus += filtered[0] if filtered else "-"
        # Align consensus to new sequence
        a1, a2 = pairwise_alignment(
            consensus, seq, gap_penalty, match_score, mismatch_penalty
        )

        aligned = propagate_gaps_to_all(aligned, a1)
        aligned.append(a2)
        # Pad all to same length
        maxlen = 0
        for i in range(len(aligned)):
            length = len(aligned[i])
            if length > maxlen:
                maxlen = length
        for i in range(len(aligned)):
            aligned[i] += "-" * (maxlen - len(aligned[i]))
    return aligned
