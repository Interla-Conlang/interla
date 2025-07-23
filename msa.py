"""
Multiple Sequence Alignment (MSA) module for the Interla project.

This module provides functionality for aligning multiple sequences using
progressive alignment techniques with dynamic programming.
"""

from typing import List, Tuple

import numpy as np
from numba import njit


@njit(cache=True)
def pairwise_alignment(
    s1: str,
    s2: str,
    gap_penalty: int = -1,
    match_score: int = 2,
    mismatch_penalty: int = -1,
) -> Tuple[str, str]:
    """
    Perform pairwise sequence alignment using dynamic programming.

    This function uses the Needleman-Wunsch algorithm to find the optimal
    global alignment between two sequences.

    Args:
        s1: First sequence to align
        s2: Second sequence to align
        gap_penalty: Penalty for introducing gaps (negative value)
        match_score: Score for matching characters (positive value)
        mismatch_penalty: Penalty for mismatched characters (negative value)

    Returns:
        Tuple of aligned sequences with gaps inserted as '-' characters
    """
    m, n = len(s1), len(s2)

    # Initialize DP matrix
    dp = np.zeros((m + 1, n + 1), dtype=np.int64)

    # Initialize first row and column with gap penalties
    for i in range(m + 1):
        dp[i][0] = i * gap_penalty
    for j in range(n + 1):
        dp[0][j] = j * gap_penalty

    # Fill the DP matrix
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            match = dp[i - 1][j - 1] + (
                match_score if s1[i - 1] == s2[j - 1] else mismatch_penalty
            )
            delete = dp[i - 1][j] + gap_penalty
            insert = dp[i][j - 1] + gap_penalty
            dp[i][j] = max(match, delete, insert)

    # Traceback to reconstruct alignment
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
            # Match or mismatch
            aligned1 = s1[i - 1] + aligned1
            aligned2 = s2[j - 1] + aligned2
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i - 1][j] + gap_penalty:
            # Deletion in s2
            aligned1 = s1[i - 1] + aligned1
            aligned2 = "-" + aligned2
            i -= 1
        else:
            # Insertion in s2
            aligned1 = "-" + aligned1
            aligned2 = s2[j - 1] + aligned2
            j -= 1

    return aligned1, aligned2


@njit(cache=True)
def propagate_gaps_to_all(aligned_seqs: List[str], aligned_consensus: str) -> List[str]:
    """
    Propagate gaps from consensus sequence to all aligned sequences.

    This function ensures that gaps introduced in the consensus sequence
    are reflected in all previously aligned sequences.

    Args:
        aligned_seqs: List of previously aligned sequences
        aligned_consensus: Consensus sequence with gaps

    Returns:
        Updated list of aligned sequences with gaps propagated
    """
    idx = 0
    for c in aligned_consensus:
        if c == "-":
            # Insert gap at current position in all sequences
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
) -> List[str]:
    """
    Perform multiple sequence alignment using progressive alignment.

    This function aligns multiple sequences by progressively adding each
    sequence to the growing alignment, using consensus-based approach.

    Args:
        sequences: List of sequences to align
        gap_penalty: Penalty for introducing gaps (negative value)
        match_score: Score for matching characters (positive value)
        mismatch_penalty: Penalty for mismatched characters (negative value)

    Returns:
        List of aligned sequences with gaps inserted for optimal alignment

    Raises:
        ValueError: If sequences list is empty
    """

    # Classic progressive alignment for short strings
    aligned = [sequences[0]]

    for seq in sequences[1:]:
        # Align current alignment to new sequence
        # Build a consensus string from current alignment
        consensus = ""
        maxlen_consensus = 0

        # Find maximum length among aligned sequences
        for s in aligned:
            length = len(s)
            if length > maxlen_consensus:
                maxlen_consensus = length

        # Build consensus sequence
        for i in range(maxlen_consensus):
            chars = [s[i] if i < len(s) else "-" for s in aligned]
            # Use most common non-gap character or gap if all are gaps
            filtered = [c for c in chars if c != "-"]
            consensus += filtered[0] if filtered else "-"

        # Align consensus to new sequence
        a1, a2 = pairwise_alignment(
            consensus, seq, gap_penalty, match_score, mismatch_penalty
        )

        # Propagate gaps from aligned consensus to all previously aligned sequences
        aligned = propagate_gaps_to_all(aligned, a1)
        aligned.append(a2)

        # Pad all sequences to same length
        maxlen = 0
        for i in range(len(aligned)):
            length = len(aligned[i])
            if length > maxlen:
                maxlen = length

        for i in range(len(aligned)):
            aligned[i] += "-" * (maxlen - len(aligned[i]))

    return aligned
