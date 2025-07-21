"""
Some tests around the notion of barycenter for strings.
"""
from collections import Counter

def string_barycenter(words):
    max_len = max(len(w) for w in words)
    bary = ""
    for i in range(max_len):
        chars = [w[i] for w in words if i < len(w)]
        most_common = Counter(chars).most_common(1)[0][0]
        bary += most_common
    return bary

print(string_barycenter(["hello", "hallo", "hola"]))
# TODO: would require aligning the strings first (because for example the "a" in hola should be aligned with the "o" in "hello" and "hallo", not the "l")