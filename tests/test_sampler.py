from sampler import recursive_search


def dummy_get_path_weight(path, weights):
    # Simple sum of weights
    return sum(weights)


def test_recursive_search_basic():
    tokens = [
        ["a", "b"],
        ["c", "d"],
    ]
    token_weights = [
        [1.0, 2.0],
        [3.0, 1.0],
    ]
    best_weight_so_far = [float("inf")]
    best_path, best_weight = recursive_search(
        0, [], [], best_weight_so_far, tokens, token_weights, dummy_get_path_weight
    )
    # The optimal path is ['a', 'd'] with weight 1.0 + 1.0 = 2.0
    assert best_path == ["a", "d"]
    assert best_weight == 2.0


def test_recursive_search_pruning():
    tokens = [
        ["x", "y"],
        ["z"],
    ]
    token_weights = [
        [10.0, 1.0],
        [1.0],
    ]
    # Set best_weight_so_far to 2.0, so any path >= 2.0 is pruned
    best_weight_so_far = [2.0]
    best_path, best_weight = recursive_search(
        0, [], [], best_weight_so_far, tokens, token_weights, dummy_get_path_weight
    )
    # Only path ['y', 'z'] with weight 1.0 + 1.0 = 2.0 is not pruned, but since >= best_weight_so_far, should return [], inf
    assert best_path == []
    assert best_weight == float("inf")


def test_recursive_search_empty_tokens():
    tokens = []
    token_weights = []
    best_weight_so_far = [float("inf")]
    best_path, best_weight = recursive_search(
        0, [], [], best_weight_so_far, tokens, token_weights, dummy_get_path_weight
    )
    assert best_path == []
    assert best_weight == 0.0


def test_recursive_search_handles_dash():
    tokens = [
        ["a", "-"],
        ["b", "-"],
    ]
    token_weights = [
        [1.0, 0.5],
        [2.0, 0.1],
    ]
    best_weight_so_far = [float("inf")]
    best_path, best_weight = recursive_search(
        0, [], [], best_weight_so_far, tokens, token_weights, dummy_get_path_weight
    )
    # The optimal path is ['-', '-'] with weight 0.5 + 0.1 = 0.6
    assert best_path == ["-", "-"]
    assert best_weight == 0.6


def test_recursive_search_custom_weight_function():
    def custom_weight(path, weights):
        # Penalize if 'x' is in path
        return sum(weights) + (100 if "x" in path else 0)

    tokens = [
        ["a", "x"],
        ["b"],
    ]
    token_weights = [
        [1.0, 1.0],
        [2.0],
    ]
    best_weight_so_far = [float("inf")]
    best_path, best_weight = recursive_search(
        0, [], [], best_weight_so_far, tokens, token_weights, custom_weight
    )
    # Should avoid 'x', so path is ['a', 'b'] with weight 1.0 + 2.0 = 3.0
    assert best_path == ["a", "b"]
    assert best_weight == 3.0


def test_only_one_path():
    def custom_weight(path, weights):
        # Penalize if 'x' is in path
        return sum(weights) + (100 if "x" in path else 0)

    tokens = [
        ["a"],
        ["b"],
        ["c"],
    ]
    token_weights = [
        [1.0],
        [2.0],
        [3.0],
    ]
    best_weight_so_far = [float("inf")]
    best_path, best_weight = recursive_search(
        0, [], [], best_weight_so_far, tokens, token_weights, custom_weight
    )
    assert best_path == ["a", "b", "c"]


if __name__ == "__main__":
    test_recursive_search_basic()
    test_recursive_search_pruning()
    test_recursive_search_empty_tokens()
    test_recursive_search_handles_dash()
    test_recursive_search_custom_weight_function()
    test_only_one_path()
    print("All tests passed!")
