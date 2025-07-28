from typing import Callable, List, Tuple


def sample_tokens(
    tokens: List[Tuple[str, ...]],
    token_weights: List[Tuple[float, ...]],
    get_path_weight: Callable[[List[str], List[float]], float],
) -> str:
    """
    Dummy solver for benchmarking that tries all possible combinations recursively.

    This function explores all possible paths by:
    1. Trying all tokens at the first position
    2. For each first token, trying all tokens at the second position (if edge weight is not +inf)
    3. Continuing recursively until the end
    4. Returns the path with minimum total weight
    """
    if not tokens or not tokens[0]:
        return ""

    def recursive_search(
        position: int, current_path: List[str], current_weights: List[float]
    ) -> Tuple[List[str], float]:
        """
        Recursively search for the optimal path starting from the given position.

        Args:
            position: Current position in the tokens list
            current_path: Path taken so far
            current_weights: Token weights corresponding to current_path

        Returns:
            Tuple of (best_path, best_weight) from this position onwards
        """
        # Base case: reached the end
        if position >= len(tokens):
            # Calculate final path weight
            final_weight = (
                get_path_weight(current_path, current_weights) if current_path else 0.0
            )
            return current_path.copy(), final_weight

        best_path = None
        best_weight = float("inf")

        # Try all tokens at current position
        for token_idx, token in enumerate(tokens[position]):
            # Create new path with this token
            new_path = current_path + [token]

            # Get the token weight and create new weights list
            token_weight = token_weights[position][token_idx]
            new_weights = current_weights + [token_weight]

            # Calculate total weight for this path so far
            path_weight = get_path_weight(new_path, new_weights)

            # Skip if path weight is infinite (invalid path)
            if path_weight == float("inf"):
                continue

            # Recursively explore from next position
            path_from_here, weight_from_here = recursive_search(
                position + 1, new_path, new_weights
            )

            # Update best path if this is better
            if weight_from_here < best_weight:
                best_weight = weight_from_here
                best_path = path_from_here

        return best_path if best_path is not None else [], best_weight

    # Start recursive search from position 0
    optimal_path, _ = recursive_search(0, [], [])

    # Return concatenated result
    return "".join([c for c in optimal_path if c != "-"])  # Exclude "-" tokens
