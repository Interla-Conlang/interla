from typing import Callable, List, Tuple


def sample_tokens(
    tokens: List[Tuple[str, ...]],
    token_weights: List[Tuple[float, ...]],
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
    if not tokens or not tokens[0]:
        return ""

    def recursive_search(
        position: int,
        current_path: List[str],
        current_weights: List[float],
        best_weight_so_far: List[float],  # Use list for mutability in closure
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
        # Calculate current subpath weight
        current_weight = (
            get_path_weight(current_path, current_weights) if current_path else 0.0
        )

        # Prune if current subpath is already worse than best found so far
        if current_weight >= best_weight_so_far[0]:
            return [], float("inf")

        # Base case: reached the end
        if position >= len(tokens):
            # Calculate final path weight
            if current_weight < best_weight_so_far[0]:
                best_weight_so_far[0] = current_weight
            return current_path.copy(), current_weight

        best_path = None
        best_weight = float("inf")

        # Try all tokens at current position, sorted by their weights
        token_indices_sorted = sorted(
            range(len(tokens[position])), key=lambda idx: token_weights[position][idx]
        )
        for token_idx in token_indices_sorted:
            token = tokens[position][token_idx]
            token_weight = token_weights[position][token_idx]
            new_path = current_path + [token]
            new_weights = current_weights + [token_weight]

            # Recursively explore from next position
            path_from_here, weight_from_here = recursive_search(
                position + 1, new_path, new_weights, best_weight_so_far
            )

            if weight_from_here < best_weight:
                best_weight = weight_from_here
                best_path = path_from_here

        return best_path if best_path is not None else [], best_weight

    # Use a mutable container for best_weight_so_far
    best_weight_so_far = [float("inf")]

    # Start recursive search from position 0
    optimal_path, _ = recursive_search(0, [], [], best_weight_so_far)
    return "".join([c for c in optimal_path if c != "-"])
