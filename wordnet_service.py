# from nltk.corpus import wordnet as wn
# from collections import deque
# import nltk

# nltk.download("wordnet", quiet=True)


# def get_synonyms(word: str, pos: str | None = None) -> list[str]:
#     """Return a deduplicated list of synonyms for a word across all synsets."""
#     synsets = wn.synsets(word, pos=pos) if pos else wn.synsets(word)
#     synonyms: set[str] = set()
#     for synset in synsets:
#         for lemma in synset.lemmas():
#             name = lemma.name().replace("_", " ")
#             if name.lower() != word.lower():
#                 synonyms.add(name)
#     return sorted(synonyms)


# def shortest_path(start: str, end: str, max_depth: int = 6) -> list[str] | None:
#     """BFS over synonym graph. Returns the word chain or None if unreachable."""
#     if start == end:
#         return [start]

#     queue: deque[list[str]] = deque([[start]])
#     visited: set[str] = {start}

#     while queue:
#         path = queue.popleft()
#         if len(path) > max_depth:
#             return None
#         for synonym in get_synonyms(path[-1]):
#             if synonym in visited:
#                 continue
#             new_path = path + [synonym]
#             if synonym.lower() == end.lower():
#                 return new_path
#             visited.add(synonym)
#             queue.append(new_path)

#     return None
