import random

from driver import driver
from wordfreq import zipf_frequency

# --- Frequency thresholds ---
# Puzzle start/end words must be clearly everyday vocabulary (Zipf >= 4.0).
# Clickable neighbors in game mode only need to be recognisable (Zipf >= 3.0),
# so "hound", "poodle", "canine" make it through while "Canis familiaris" does not.
PUZZLE_WORD_MIN_ZIPF = 5.0
NEIGHBOR_MIN_ZIPF = 3.0
CN_NEIGHBOR_MIN_ZIPF = 4.0  # stricter than WordNet neighbors; CN terms skew obscure


def is_common(word: str, min_zipf: float = NEIGHBOR_MIN_ZIPF) -> bool:
    return zipf_frequency(word.lower(), "en") >= min_zipf


# --- Full relation sets (Explorer tab) ---
SYNSET_RELS = "|".join(
    f"ns3__{r}"
    for r in [
        "also", "attribute", "causes", "is_caused_by",
        "domain_region", "has_domain_region", "domain_topic", "has_domain_topic",
        "entails", "is_entailed_by", "exemplifies", "is_exemplified_by",
        "holo_member", "holo_part", "holo_substance",
        "mero_member", "mero_part", "mero_substance",
        "hypernym", "hyponym", "instance_hypernym", "instance_hyponym",
        "similar",
    ]
)
SENSE_RELS = "|".join(
    f"ns3__{r}" for r in ["antonym", "derivation", "participle", "pertainym", "other"]
)

# --- Restricted relation sets (Word Chain game) ---
# Only the intuitive "next word" hops that players recognise without a
# linguistics background.  Hypernym/hyponym give up-down hierarchy,
# similar/also give sideways adjective links; antonym and derivation give
# cross-POS hops.
GAME_SYNSET_RELS = "|".join(
    f"ns3__{r}" for r in [
        "hypernym", "hyponym", "similar", "also",
        "mero_part", "mero_member", "mero_substance",
        "holo_part", "holo_member", "holo_substance",
    ]
)
GAME_SENSE_RELS = "|".join(
    f"ns3__{r}" for r in ["antonym", "derivation"]
)

# --- ConceptNet relations included in conceptual game mode ---
CN_GAME_RELS = {
    "UsedFor", "CapableOf", "AtLocation", "MadeOf",
    "HasProperty", "Causes", "PartOf", "SimilarTo", "IsA", "Synonym",
}

CN_NEIGHBORS_QUERY = """
UNWIND $words AS w
MATCH (a:ConceptNetNode {term: w})-[r:CN_REL]-(b:ConceptNetNode)
WHERE r.type IN $rels AND NOT b.term CONTAINS '_'
RETURN w AS word, b.term AS neighbor, r.type AS rel, r.weight AS weight
"""

# NOTE: This DB was imported with n10s handleMultival=ARRAY, so every RDF
# literal/IRI-valued property is stored as a Neo4j list rather than a scalar.
# Matching uses {prop: [param]} (array equality) so the range index is used,
# and head() unwraps single-element lists for output values.

NEIGHBORS_QUERY = f"""
UNWIND $words AS w
MATCH (form:Resource {{ns2__writtenRep: [w]}})
USING INDEX form:Resource(ns2__writtenRep)
MATCH (word:Resource)-[:ns2__canonicalForm]->(form)
MATCH (word)-[:ns2__sense]->(sense)-[:ns2__isLexicalizedSenseOf]->(synset)
CALL (sense, synset) {{
  MATCH (nbr_sense)-[:ns2__isLexicalizedSenseOf]->(synset)
  WHERE nbr_sense <> sense
  RETURN nbr_sense, 'synonym' AS rel
  UNION ALL
  MATCH (synset)-[r:{SYNSET_RELS}]->(other_synset)
  MATCH (nbr_sense)-[:ns2__isLexicalizedSenseOf]->(other_synset)
  RETURN nbr_sense, replace(TYPE(r), 'ns3__', '') AS rel
  UNION ALL
  MATCH (sense)-[r:{SENSE_RELS}]->(nbr_sense)
  RETURN nbr_sense, replace(TYPE(r), 'ns3__', '') AS rel
}}
MATCH (nbr_sense)<-[:ns2__sense]-(nbr_word)-[:ns2__canonicalForm]->(nbr_form)
WITH w, head(nbr_form.ns2__writtenRep) AS neighbor, COLLECT(DISTINCT rel) AS rels
WHERE neighbor IS NOT NULL AND neighbor <> w
RETURN w AS word, COLLECT({{word: neighbor, relations: rels}}) AS neighbors
"""

GAME_NEIGHBORS_QUERY = f"""
UNWIND $words AS w
MATCH (form:Resource {{ns2__writtenRep: [w]}})
USING INDEX form:Resource(ns2__writtenRep)
MATCH (word:Resource)-[:ns2__canonicalForm]->(form)
MATCH (word)-[:ns2__sense]->(sense)-[:ns2__isLexicalizedSenseOf]->(synset)
CALL (sense, synset) {{
  MATCH (nbr_sense)-[:ns2__isLexicalizedSenseOf]->(synset)
  WHERE nbr_sense <> sense
  RETURN nbr_sense, 'synonym' AS rel
  UNION ALL
  MATCH (synset)-[r:{GAME_SYNSET_RELS}]->(other_synset)
  MATCH (nbr_sense)-[:ns2__isLexicalizedSenseOf]->(other_synset)
  RETURN nbr_sense, replace(TYPE(r), 'ns3__', '') AS rel
  UNION ALL
  MATCH (sense)-[r:{GAME_SENSE_RELS}]->(nbr_sense)
  RETURN nbr_sense, replace(TYPE(r), 'ns3__', '') AS rel
}}
MATCH (nbr_sense)<-[:ns2__sense]-(nbr_word)-[:ns2__canonicalForm]->(nbr_form)
WITH w, head(nbr_form.ns2__writtenRep) AS neighbor, COLLECT(DISTINCT rel) AS rels
WHERE neighbor IS NOT NULL AND neighbor <> w
RETURN w AS word, COLLECT({{word: neighbor, relations: rels}}) AS neighbors
"""

SENSES_QUERY = """
MATCH (form:Resource {ns2__writtenRep: [$word]})
USING INDEX form:Resource(ns2__writtenRep)
MATCH (word:Resource)-[:ns2__canonicalForm]->(form)
MATCH (word)-[:ns2__sense]->(sense)-[:ns2__isLexicalizedSenseOf]->(synset)
OPTIONAL MATCH (synset)-[:ns3__definition]->(def)
OPTIONAL MATCH (synset)-[:ns3__example]->(ex)
RETURN DISTINCT synset.uri AS synset_uri,
       head(def.rdf__value) AS definition,
       COLLECT(DISTINCT head(ex.rdf__value)) AS examples
"""

SYNSET_NEIGHBORS_QUERY = f"""
MATCH (form:Resource {{ns2__writtenRep: [$word]}})
USING INDEX form:Resource(ns2__writtenRep)
MATCH (wordnode:Resource)-[:ns2__canonicalForm]->(form)
MATCH (wordnode)-[:ns2__sense]->(sense)-[:ns2__isLexicalizedSenseOf]->(synset)
OPTIONAL MATCH (synset)-[:ns3__definition]->(def_node)
OPTIONAL MATCH (synset)-[:ns3__example]->(ex_node)
WITH sense, synset,
     head(def_node.rdf__value) AS definition,
     COLLECT(DISTINCT head(ex_node.rdf__value)) AS examples
CALL (sense, synset) {{
  MATCH (nbr_sense)-[:ns2__isLexicalizedSenseOf]->(synset)
  WHERE nbr_sense <> sense
  RETURN nbr_sense, 'synonym' AS rel
  UNION ALL
  MATCH (synset)-[r:{SYNSET_RELS}]->(other_synset)
  MATCH (nbr_sense)-[:ns2__isLexicalizedSenseOf]->(other_synset)
  RETURN nbr_sense, replace(TYPE(r), 'ns3__', '') AS rel
  UNION ALL
  MATCH (sense)-[r:{SENSE_RELS}]->(nbr_sense)
  RETURN nbr_sense, replace(TYPE(r), 'ns3__', '') AS rel
}}
MATCH (nbr_sense)<-[:ns2__sense]-(nbr_word)-[:ns2__canonicalForm]->(nbr_form)
WITH synset, definition, examples,
     head(nbr_form.ns2__writtenRep) AS neighbor,
     COLLECT(DISTINCT rel) AS rels
WHERE neighbor IS NOT NULL AND neighbor <> $word
WITH synset.uri AS synset_uri, definition, examples,
     COLLECT({{neighbor: neighbor, rels: rels}}) AS pairs
RETURN synset_uri, definition, examples, pairs
ORDER BY synset_uri
"""

GAME_SYNSET_NEIGHBORS_QUERY = f"""
MATCH (form:Resource {{ns2__writtenRep: [$word]}})
USING INDEX form:Resource(ns2__writtenRep)
MATCH (wordnode:Resource)-[:ns2__canonicalForm]->(form)
MATCH (wordnode)-[:ns2__sense]->(sense)-[:ns2__isLexicalizedSenseOf]->(synset)
OPTIONAL MATCH (synset)-[:ns3__definition]->(def_node)
OPTIONAL MATCH (synset)-[:ns3__example]->(ex_node)
WITH sense, synset,
     head(def_node.rdf__value) AS definition,
     COLLECT(DISTINCT head(ex_node.rdf__value)) AS examples
CALL (sense, synset) {{
  MATCH (nbr_sense)-[:ns2__isLexicalizedSenseOf]->(synset)
  WHERE nbr_sense <> sense
  RETURN nbr_sense, 'synonym' AS rel
  UNION ALL
  MATCH (synset)-[r:{GAME_SYNSET_RELS}]->(other_synset)
  MATCH (nbr_sense)-[:ns2__isLexicalizedSenseOf]->(other_synset)
  RETURN nbr_sense, replace(TYPE(r), 'ns3__', '') AS rel
  UNION ALL
  MATCH (sense)-[r:{GAME_SENSE_RELS}]->(nbr_sense)
  RETURN nbr_sense, replace(TYPE(r), 'ns3__', '') AS rel
}}
MATCH (nbr_sense)<-[:ns2__sense]-(nbr_word)-[:ns2__canonicalForm]->(nbr_form)
WITH synset, definition, examples,
     head(nbr_form.ns2__writtenRep) AS neighbor,
     COLLECT(DISTINCT rel) AS rels
WHERE neighbor IS NOT NULL AND neighbor <> $word
WITH synset.uri AS synset_uri, definition, examples,
     COLLECT({{neighbor: neighbor, rels: rels}}) AS pairs
RETURN synset_uri, definition, examples, pairs
ORDER BY synset_uri
"""

POS_LABELS = {
    "n": "n.", "v": "v.", "a": "adj.", "s": "adj.", "r": "adv.",
}

RANDOM_WORDS_QUERY = """
MATCH (:Resource)-[:ns2__canonicalForm]->(form)
WITH DISTINCT head(form.ns2__writtenRep) AS w
WHERE w IS NOT NULL AND NOT w CONTAINS ' '
RETURN w ORDER BY rand() LIMIT $n
"""


def ensure_index() -> None:
    """Index written forms so word lookups don't scan every Resource node."""
    with driver.session() as session:
        session.run(
            "CREATE INDEX resource_written_rep IF NOT EXISTS "
            "FOR (n:Resource) ON (n.ns2__writtenRep)"
        )


def _parse_neighbors_result(
    result, *, min_zipf: float | None = None
) -> dict[str, dict[str, list[str]]]:
    out: dict[str, dict[str, list[str]]] = {}
    for rec in result:
        word = rec["word"]
        neighbors: dict[str, list[str]] = {}
        for n in rec["neighbors"]:
            nbr = n["word"]
            if not nbr or nbr.lower() == word.lower():
                continue
            if min_zipf is not None and not is_common(nbr, min_zipf):
                continue
            neighbors[nbr] = sorted(n["relations"])
        out[word] = neighbors
    return out


def get_neighbors_batch(words: list[str]) -> dict[str, dict[str, list[str]]]:
    """All WordNet relations, no frequency filter. Used by Explorer and chain validation."""
    if not words:
        return {}
    with driver.session() as session:
        result = session.run(NEIGHBORS_QUERY, words=words)
        return _parse_neighbors_result(result)


def get_game_neighbors_batch(
    words: list[str], *, conceptual: bool = False
) -> dict[str, dict[str, list[str]]]:
    """Restricted relations + Zipf frequency filter. Used by game BFS and neighbor display."""
    if not words:
        return {}
    with driver.session() as session:
        result = session.run(GAME_NEIGHBORS_QUERY, words=words)
        wn = _parse_neighbors_result(result, min_zipf=NEIGHBOR_MIN_ZIPF)

    if not conceptual:
        return wn

    cn = _get_cn_neighbors_batch(words)
    for word, cn_neighbors in cn.items():
        merged = wn.setdefault(word, {})
        for nbr, rels in cn_neighbors.items():
            if nbr in merged:
                merged[nbr] = sorted(set(merged[nbr]) | set(rels))
            else:
                merged[nbr] = rels
    return wn


def _get_cn_neighbors_batch(
    words: list[str],
) -> dict[str, dict[str, list[str]]]:
    """ConceptNet neighbors for each word, single-word terms only, Zipf-filtered."""
    if not words:
        return {}
    with driver.session() as session:
        result = session.run(
            CN_NEIGHBORS_QUERY, words=words, rels=list(CN_GAME_RELS)
        )
        out: dict[str, dict[str, list[str]]] = {}
        for rec in result:
            word = rec["word"]
            nbr = rec["neighbor"]
            rel = rec["rel"]
            if not nbr or not is_common(nbr, CN_NEIGHBOR_MIN_ZIPF):
                continue
            out.setdefault(word, {}).setdefault(nbr, [])
            if rel not in out[word][nbr]:
                out[word][nbr].append(rel)
        return out


def _parse_synset_result(
    result, word: str, *, min_zipf: float | None = None
) -> list[dict]:
    pos_order = {label: i for i, label in enumerate(dict.fromkeys(POS_LABELS.values()))}
    synsets = []
    for rec in result:
        pos_key = (rec["synset_uri"] or "").rsplit("-", 1)[-1]
        relations: dict[str, list[str]] = {}
        for pair in rec["pairs"]:
            nbr = pair["neighbor"]
            if not nbr:
                continue
            if min_zipf is not None and not is_common(nbr, min_zipf):
                continue
            for rel in pair["rels"]:
                relations.setdefault(rel, []).append(nbr)
        if not relations:
            continue
        for rel in relations:
            relations[rel] = sorted(relations[rel])
        synsets.append({
            "definition": rec["definition"] or "",
            "examples": [e for e in (rec["examples"] or []) if e],
            "pos": POS_LABELS.get(pos_key, ""),
            "relations": relations,
        })
    synsets.sort(key=lambda s: pos_order.get(s["pos"], len(pos_order)))
    return synsets


def get_synset_neighbors(word: str) -> list[dict]:
    """All relations, no frequency filter. Used by Explorer."""
    with driver.session() as session:
        result = session.run(SYNSET_NEIGHBORS_QUERY, word=word)
        return _parse_synset_result(result, word)


def get_game_synset_neighbors(word: str, *, conceptual: bool = False) -> list[dict]:
    """Restricted relations + Zipf filter. Used by Word Chain neighbor display."""
    with driver.session() as session:
        result = session.run(GAME_SYNSET_NEIGHBORS_QUERY, word=word)
        synsets = _parse_synset_result(result, word, min_zipf=NEIGHBOR_MIN_ZIPF)

    if not conceptual:
        return synsets

    cn_neighbors = _get_cn_neighbors_batch([word]).get(word, {})
    if cn_neighbors:
        grouped: dict[str, list[str]] = {}
        for nbr, rels in cn_neighbors.items():
            for rel in rels:
                grouped.setdefault(rel, []).append(nbr)
        synsets.append({
            "definition": "conceptual associations",
            "examples": [],
            "pos": "",
            "relations": {rel: sorted(ws) for rel, ws in grouped.items()},
        })
    return synsets


def get_senses(word: str) -> list[dict]:
    """Definitions and example sentences for each sense of a word."""
    with driver.session() as session:
        result = session.run(SENSES_QUERY, word=word)
        senses = []
        for rec in result:
            if not rec["definition"]:
                continue
            pos_key = (rec["synset_uri"] or "").rsplit("-", 1)[-1]
            senses.append({
                "pos": POS_LABELS.get(pos_key, ""),
                "definition": rec["definition"],
                "examples": [e for e in rec["examples"] if e],
            })
        order = {label: i for i, label in enumerate(dict.fromkeys(POS_LABELS.values()))}
        senses.sort(key=lambda s: order.get(s["pos"], len(order)))
        return senses


def get_neighbors_grouped(word: str) -> dict[str, list[str]]:
    """Related words grouped by relation label, for display."""
    neighbors = get_neighbors_batch([word]).get(word, {})
    grouped: dict[str, list[str]] = {}
    for nbr, rels in neighbors.items():
        for rel in rels:
            grouped.setdefault(rel, []).append(nbr)
    return {rel: sorted(ws) for rel, ws in grouped.items()}


def random_words(n: int) -> list[str]:
    """Return n random single-word entries that pass the puzzle frequency threshold."""
    with driver.session() as session:
        result = session.run(RANDOM_WORDS_QUERY, n=n * 30)
        words: list[str] = []
        for rec in result:
            w = rec["w"]
            if w and is_common(w, PUZZLE_WORD_MIN_ZIPF):
                words.append(w)
                if len(words) >= n:
                    break
        return words


def _bfs_levels(
    start: str,
    max_depth: int,
    stop_at: str | None = None,
    max_frontier: int = 500,
    game_mode: bool = False,
    conceptual: bool = False,
) -> tuple[list[list[str]], dict[str, str], str | None]:
    """BFS over the relation graph, one batched query per level.

    Returns (levels, parent, hit) where levels[d] holds the words first reached
    in d steps, parent maps each word to its predecessor, and hit is the word
    matching stop_at (case-insensitive) if it was reached.

    When the next frontier exceeds max_frontier, it is randomly sampled down to
    that size so query times stay bounded. For shortest_path() pass a larger
    max_frontier to ensure the target isn't accidentally pruned.
    """
    if game_mode:
        fetch = lambda words: get_game_neighbors_batch(words, conceptual=conceptual)
    else:
        fetch = get_neighbors_batch
    visited = {start.lower()}
    parent: dict[str, str] = {}
    levels = [[start]]
    frontier = [start]

    for _ in range(max_depth):
        neighbors_by_word = fetch(frontier)
        next_frontier: list[str] = []
        for word in frontier:
            for neighbor in neighbors_by_word.get(word, {}):
                key = neighbor.lower()
                if key in visited:
                    continue
                visited.add(key)
                parent[neighbor] = word
                next_frontier.append(neighbor)
                if stop_at is not None and key == stop_at:
                    levels.append(next_frontier)
                    return levels, parent, neighbor
        if not next_frontier:
            break
        if len(next_frontier) > max_frontier:
            next_frontier = random.sample(next_frontier, max_frontier)
        levels.append(next_frontier)
        frontier = next_frontier

    return levels, parent, None


def shortest_path(start: str, end: str, max_depth: int = 6) -> list[str] | None:
    """BFS over full relations. Returns the word chain or None if unreachable."""
    if start.lower() == end.lower():
        return [start]
    _, parent, hit = _bfs_levels(start, max_depth, stop_at=end.lower(), max_frontier=5000)
    if hit is None:
        return None
    path = [hit]
    while path[-1].lower() != start.lower():
        path.append(parent[path[-1]])
    return list(reversed(path))


def random_puzzle(min_steps: int = 3, max_steps: int = 5) -> dict | None:
    """Pick a random start/end word pair solvable via game-mode relations.

    Candidates are filtered by PUZZLE_WORD_MIN_ZIPF; BFS uses only the
    restricted game-mode relation set so the optimal_steps count reflects
    what the player can actually navigate.
    """
    candidates = random_words(100)
    neighbors_by_word = get_game_neighbors_batch(candidates)
    starts = [w for w in candidates if len(neighbors_by_word.get(w, {})) >= 2]
    random.shuffle(starts)

    best: dict | None = None
    for start in starts:
        target_depth = random.randint(min_steps, max_steps)
        levels, _, _ = _bfs_levels(start, target_depth, game_mode=True)
        depth = len(levels) - 1
        if best is None or depth > best["optimal_steps"]:
            best = {
                "start": start,
                "end": random.choice(levels[depth]),
                "optimal_steps": depth,
            }
        if depth >= min_steps:
            return best
    if best is not None and best["optimal_steps"] >= 2:
        return best
    return None
