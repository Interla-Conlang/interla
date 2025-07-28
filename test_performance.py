#!/usr/bin/env python3
"""
Performance test for sampler.py optimization
"""

import time
from typing import List, Tuple

from gen_vocabulary import path_pronounciability_weight
from sampler import sample_tokens


def create_test_case(
    size: int,
) -> Tuple[List[List[str]], List[List[float]]]:
    """Create a test case with given size"""
    tokens = []
    token_weights = []

    # Create tokens with varying number of options (4-8 per position for wider graphs)
    for i in range(size):
        if i % 4 == 0:
            # Position with 8 options
            tokens.append(["a", "e", "i", "o", "u", "æ", "ə", "ɛ"])
            token_weights.append([0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4])
        elif i % 4 == 1:
            # Position with 6 options
            tokens.append(["t", "s", "n", "k", "p", "m"])
            token_weights.append([0.1, 0.15, 0.2, 0.25, 0.3, 0.35])
        elif i % 4 == 2:
            # Position with 5 options
            tokens.append(["r", "l", "w", "j", "h"])
            token_weights.append([0.15, 0.2, 0.25, 0.3, 0.35])
        else:
            # Position with 4 options
            tokens.append(["-", "ʔ", "ŋ", "θ"])
            token_weights.append([0.1, 0.2, 0.3, 0.4])

    return tokens, token_weights


def benchmark_current_implementation():
    """Benchmark the current implementation with various sizes"""
    print("Benchmarking current implementation...")

    test_sizes = [
        5,
        7,
        9,
        11,
        13,
        15,
        17,
        19,
    ]  # Test even larger sizes with wide graphs

    for size in test_sizes:
        tokens, token_weights = create_test_case(size)

        start_time = time.time()
        result = sample_tokens(tokens, token_weights, path_pronounciability_weight)
        end_time = time.time()

        print(f"Size {size}: {end_time - start_time:.4f}s -> '{result}'")

        # Stop if it takes too long
        if end_time - start_time > 5.0:
            print(f"Stopping at size {size} due to long execution time")
            break


if __name__ == "__main__":
    benchmark_current_implementation()
