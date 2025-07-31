import hashlib
from typing import Callable, Dict, List, Optional, Tuple


def _hash_path(path: List[str]) -> str:
    """Create a compact hash of the path to reduce memory usage."""
    if not path:
        return ""
    # Use a shorter hash to save memory while maintaining uniqueness
    return hashlib.md5("".join(path).encode()).hexdigest()[:16]


def _clean_memo_by_position(
    memo: Dict[Tuple[int, str], Tuple[List[str], float]],
    current_position: int,
    keep_recent: int = 5,
) -> None:
    """Clean memo entries for positions too far behind current position."""
    positions_to_clear = set(
        pos for pos, _ in memo.keys() if pos < current_position - keep_recent
    )
    for pos in positions_to_clear:
        keys_to_remove = [key for key in memo.keys() if key[0] == pos]
        for key in keys_to_remove:
            del memo[key]


def _clean_memo_lru(
    memo: Dict[Tuple[int, str], Tuple[List[str], float]], target_size: int
) -> None:
    """Clean memo using a simple LRU-like strategy (remove entries from earlier positions)."""
    if len(memo) <= target_size:
        return

    # Sort keys by position (earlier positions will be removed first)
    sorted_keys = sorted(memo.keys(), key=lambda x: x[0])
    keys_to_remove = sorted_keys[: len(memo) - target_size]

    for key in keys_to_remove:
        del memo[key]


def recursive_search(
    position: int,
    current_path: List[str],
    current_weights: List[float],
    best_weight_so_far: List[float],  # Use list for mutability
    tokens: List[List[str]],
    token_weights: List[List[float]],
    get_path_weight: Callable[[List[str], List[float]], float],
    sorted_indices: List[List[int]],  # Pre-sorted token indices
    min_future_weights: List[float],  # Minimum possible weight from each position
    memo: Dict[Tuple[int, str], Tuple[List[str], float]],  # Optimized memoization cache
    memo_size_limit: int = 200_000,  # Hard limit on memo size
    depth_limit: Optional[int] = None,  # Optional depth limit for memoization
) -> Tuple[List[str], float]:
    """
    Recursively search for the optimal path starting from the given position.

    Args:
        position: Current position in the tokens list
        current_path: Path taken so far
        current_weights: Token weights corresponding to current_path
        best_weight_so_far: Mutable container for the best weight found so far
        tokens: List of token options at each position
        token_weights: Corresponding weights for each token option
        get_path_weight: Function to calculate path weight
        sorted_indices: Pre-sorted token indices by weight for each position
        min_future_weights: Minimum possible weight from each position onwards
        memo: Memoization cache

    Returns:
        Tuple of (best_path, best_weight) from this position onwards
    """
    # Create optimized memoization key using path hash
    path_hash = _hash_path(current_path)
    memo_key = (position, path_hash)

    # Check memoization cache
    if memo_key in memo:
        return memo[memo_key]

    # Memory management: limit memo size and clear old entries if needed
    if len(memo) >= memo_size_limit:
        # Try cleaning old positions first
        # _clean_memo_by_position(memo, position)

        # # If still too large, use more aggressive cleaning
        # if len(memo) >= memo_size_limit - 100_000:
        #     _clean_memo_lru(memo, memo_size_limit // 2)

        # # If still too large, return current best path to avoid memory overflow
        # if len(memo) >= memo_size_limit - 200_000:
        #     current_weight = (
        #         get_path_weight(current_path, current_weights) if current_path else 0.0
        #     )
        #     return (current_path.copy(), current_weight)

        current_weight = (
            get_path_weight(current_path, current_weights) if current_path else 0.0
        )
        return (current_path.copy(), current_weight)

    # Skip memoization for very deep recursions to save memory
    use_memo = depth_limit is None or len(current_path) < depth_limit

    # Calculate current subpath weight
    current_weight = (
        get_path_weight(current_path, current_weights) if current_path else 0.0
    )

    # Enhanced pruning: check if current + minimum future cost exceeds best
    if position < len(min_future_weights):
        estimated_total = current_weight + min_future_weights[position]
        if estimated_total >= best_weight_so_far[0]:
            result = ([], float("inf"))
            if use_memo:
                memo[memo_key] = result
            return result

    # Base case: reached the end
    if position >= len(tokens):
        # Check if all characters in the path are "-"
        if all(c == "-" for c in current_path):
            result = ([], float("inf"))
            if use_memo:
                memo[memo_key] = result
            return result
        # Calculate final path weight
        if current_weight < best_weight_so_far[0]:
            best_weight_so_far[0] = current_weight
        result = (current_path.copy(), current_weight)
        if use_memo:
            memo[memo_key] = result
        return result

    best_path = None
    best_weight = float("inf")

    # Try all tokens at current position, using pre-sorted indices
    for token_idx in sorted_indices[position]:
        token = tokens[position][token_idx]
        token_weight = token_weights[position][token_idx]
        new_path = current_path + [token]
        new_weights = current_weights + [token_weight]

        # Recursively explore from next position
        path_from_here, weight_from_here = recursive_search(
            position + 1,
            new_path,
            new_weights,
            best_weight_so_far,
            tokens,
            token_weights,
            get_path_weight,
            sorted_indices,
            min_future_weights,
            memo,
            memo_size_limit,
            depth_limit,
        )

        if weight_from_here < best_weight:
            best_weight = weight_from_here
            best_path = path_from_here

    result = (best_path if best_path is not None else [], best_weight)
    if use_memo:
        memo[memo_key] = result
    return result


def sample_tokens(
    tokens: List[List[str]],
    token_weights: List[List[float]],
    get_path_weight: Callable[[List[str], List[float]], float],
    memo_size_limit: int = 1_000_000,  # Hard limit on memo size
    depth_limit: Optional[int] = None,  # Optional depth limit for memoization
) -> str:
    """
    Solver that tries all possible combinations recursively with memory optimization.

    This function explores all possible paths by:
    1. Trying all tokens at the first position
    2. For each first token, trying all tokens at the second position (if edge weight is not +inf)
    3. Continuing recursively until the end
    4. Returns the path with minimum total weight

    Memory optimization features:
    - memo_size_limit: Hard limit on memoization cache size (default 1M entries)
    - depth_limit: Only memoize up to this depth to save memory (default: no limit)
    """
    assert len(tokens) == len(token_weights), (
        f"Tokens and token_weights must have the same length: {len(tokens)} vs {len(token_weights)}"
    )
    if not tokens or not tokens[0]:
        return ""

    # Pre-sort token indices by weight for each position
    sorted_indices = []
    for position in range(len(tokens)):
        indices_sorted = sorted(
            range(len(tokens[position])), key=lambda idx: token_weights[position][idx]
        )
        sorted_indices.append(indices_sorted)

    # Calculate minimum possible future weights for pruning
    min_future_weights = [0.0] * (len(tokens) + 1)
    for position in range(len(tokens) - 1, -1, -1):
        min_token_weight = min(token_weights[position])
        min_future_weights[position] = (
            min_token_weight + min_future_weights[position + 1]
        )

    # Use a mutable container for best_weight_so_far
    best_weight_so_far = [float("inf")]

    # Initialize optimized memoization cache
    memo: Dict[Tuple[int, str], Tuple[List[str], float]] = {}

    # Start recursive search from position 0
    optimal_path, optimal_weight = recursive_search(
        0,
        [],
        [],
        best_weight_so_far,
        tokens,
        token_weights,
        get_path_weight,
        sorted_indices,
        min_future_weights,
        memo,
        memo_size_limit,
        depth_limit,
    )
    assert optimal_path, "No valid path found"
    assert len(optimal_path) == len(tokens), (
        f"Expected optimal path length {len(tokens)}, got {len(optimal_path)}"
    )
    assert optimal_weight < float("inf"), "No valid path found"
    return "".join([c for c in optimal_path if c != "-"])
