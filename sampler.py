from typing import Callable, Dict, List, Tuple


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
    memo: Dict[
        Tuple[int, Tuple[str, ...]], Tuple[List[str], float]
    ],  # Memoization cache
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
    # Create memoization key based on position and current path
    path_key = tuple(current_path)
    memo_key = (position, path_key)

    # Check memoization cache
    if memo_key in memo:
        return memo[memo_key]

    # Calculate current subpath weight
    current_weight = (
        get_path_weight(current_path, current_weights) if current_path else 0.0
    )

    # Enhanced pruning: check if current + minimum future cost exceeds best
    if position < len(min_future_weights):
        estimated_total = current_weight + min_future_weights[position]
        if estimated_total >= best_weight_so_far[0]:
            result = ([], float("inf"))
            memo[memo_key] = result
            return result

    # Base case: reached the end
    if position >= len(tokens):
        # Check if all characters in the path are "-"
        if all(c == "-" for c in current_path):
            result = ([], float("inf"))
            memo[memo_key] = result
            return result
        # Calculate final path weight
        if current_weight < best_weight_so_far[0]:
            best_weight_so_far[0] = current_weight
        result = (current_path.copy(), current_weight)
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
        )

        if weight_from_here < best_weight:
            best_weight = weight_from_here
            best_path = path_from_here

    result = (best_path if best_path is not None else [], best_weight)
    memo[memo_key] = result
    return result


def sample_tokens(
    tokens: List[List[str]],
    token_weights: List[List[float]],
    get_path_weight: Callable[[List[str], List[float]], float],
) -> str:
    """
    Solver that tries all possible combinations recursively.

    This function explores all possible paths by:
    1. Trying all tokens at the first position
    2. For each first token, trying all tokens at the second position (if edge weight is not +inf)
    3. Continuing recursively until the end
    4. Returns the path with minimum total weight
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

    # Initialize memoization cache
    memo = {}

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
    )
    # assert optimal_path, "No valid path found"
    # assert len(optimal_path) == len(tokens), (
    #     f"Expected optimal path length {len(tokens)}, got {len(optimal_path)}"
    # )
    # assert optimal_weight < float("inf"), "No valid path found"
    return "".join([c for c in optimal_path if c != "-"])
