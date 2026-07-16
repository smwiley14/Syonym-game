"""
WordNet Relation Explorer — Open English WordNet via the `wn` library
Prints every relation available in OEWN for a given word.

Setup (run once):
    pip install wn
    python -c "import wn; wn.download('oewn:2024')"

Usage:
    python wordnet_explorer.py <word>
    python wordnet_explorer.py <word> --pos n|v|a|r
    python wordnet_explorer.py          (interactive mode)
"""

import sys
import textwrap
from collections import defaultdict

try:
    import wn
except ImportError:
    print("wn not installed. Run: pip install wn")
    sys.exit(1)

LEXICON = "oewn:2024"

POS_LABELS = {
    "n": "noun",
    "v": "verb",
    "a": "adjective",
    "s": "adjective satellite",
    "r": "adverb",
    "t": "phrase",
    "c": "conjunction",
    "p": "adposition",
    "x": "other",
    "u": "unknown",
}

W = 72  # output width

# ── Human-readable labels for every OEWN relation type ──────────────────────

SYNSET_REL_LABELS = {
    # Core taxonomy
    "hypernym":                   "hypernyms (broader / is-a)",
    "instance_hypernym":          "instance hypernyms (this is an instance of)",
    "hyponym":                    "hyponyms (narrower / kinds of this)",
    "instance_hyponym":           "instance hyponyms (specific instances of this)",
    "eq_synonym":                 "equivalent synonyms",
    "ir_synonym":                 "irregular synonyms",
    "similar":                    "similar to",
    "also":                       "also see",
    "attribute":                  "attribute (noun linked to this adj)",
    "antonym":                    "antonyms",
    "anto_gradable":              "gradable antonyms",
    "anto_simple":                "simple antonyms",
    "anto_converse":              "converse antonyms",
    # Part/whole
    "meronym":                    "meronyms (parts of this — general)",
    "mero_part":                  "part meronyms (component parts)",
    "mero_member":                "member meronyms (members of this group)",
    "mero_substance":             "substance meronyms (made of this)",
    "mero_location":              "location meronyms",
    "mero_portion":               "portion meronyms",
    "holonym":                    "holonyms (wholes that include this — general)",
    "holo_part":                  "part holonyms (wholes this is part of)",
    "holo_member":                "member holonyms (groups this belongs to)",
    "holo_substance":             "substance holonyms (things made of this substance)",
    "holo_location":              "location holonyms",
    "holo_portion":               "portion holonyms",
    # Verbal / causal / event
    "entails":                    "entailments (this verb implies)",
    "is_entailed_by":             "entailed by",
    "causes":                     "causes",
    "is_caused_by":               "is caused by",
    "subevent":                   "subevents (component events)",
    "is_subevent_of":             "is subevent of",
    # State
    "be_in_state":                "be in state",
    "state_of":                   "state of",
    # Manner
    "in_manner":                  "in manner of",
    "manner_of":                  "manner of",
    # Role relations (FrameNet-style)
    "role":                       "role",
    "involved":                   "involved (inverse of role)",
    "agent":                      "agent role",
    "involved_agent":             "involved agent",
    "patient":                    "patient role",
    "involved_patient":           "involved patient",
    "result":                     "result role",
    "involved_result":            "involved result",
    "instrument":                 "instrument role",
    "involved_instrument":        "involved instrument",
    "location":                   "location role",
    "involved_location":          "involved location",
    "direction":                  "direction role",
    "involved_direction":         "involved direction",
    "target_direction":           "target direction",
    "involved_target_direction":  "involved target direction",
    "source_direction":           "source direction",
    "involved_source_direction":  "involved source direction",
    # Co-roles
    "co_role":                    "co-role",
    "co_agent_patient":           "co-agent / patient",
    "co_patient_agent":           "co-patient / agent",
    "co_agent_instrument":        "co-agent / instrument",
    "co_instrument_agent":        "co-instrument / agent",
    "co_agent_result":            "co-agent / result",
    "co_result_agent":            "co-result / agent",
    "co_patient_instrument":      "co-patient / instrument",
    "co_instrument_patient":      "co-instrument / patient",
    "co_result_instrument":       "co-result / instrument",
    "co_instrument_result":       "co-instrument / result",
    # Domain
    "domain_topic":               "domain topic (this belongs to topic)",
    "has_domain_topic":           "has domain topic (topic members)",
    "domain_region":              "domain region (this belongs to region)",
    "has_domain_region":          "has domain region (regional members)",
    "exemplifies":                "exemplifies (this is an example of)",
    "is_exemplified_by":          "is exemplified by",
    # Classification
    "classifies":                 "classifies",
    "classified_by":              "classified by",
    "restricts":                  "restricts",
    "restricted_by":              "restricted by",
    # Gender / morphological
    "feminine":                   "feminine form",
    "has_feminine":               "has feminine form",
    "masculine":                  "masculine form",
    "has_masculine":              "has masculine form",
    "young":                      "young / juvenile form",
    "has_young":                  "has young form",
    "diminutive":                 "diminutive of",
    "has_diminutive":             "has diminutive",
    "augmentative":               "augmentative of",
    "has_augmentative":           "has augmentative",
    # Figurative
    "metaphor":                   "metaphor of",
    "has_metaphor":               "has metaphor",
    "metonym":                    "metonym of",
    "has_metonym":                "has metonym",
    # Aspect (Slavic-style)
    "simple_aspect_ip":           "simple aspect (imperfective → perfective)",
    "secondary_aspect_ip":        "secondary aspect (imperfective → perfective)",
    "simple_aspect_pi":           "simple aspect (perfective → imperfective)",
    "secondary_aspect_pi":        "secondary aspect (perfective → imperfective)",
    # Catch-all
    "other":                      "other relation",
}

SENSE_REL_LABELS = {
    "antonym":            "antonyms",
    "anto_gradable":      "gradable antonyms",
    "anto_simple":        "simple antonyms",
    "anto_converse":      "converse antonyms",
    "also":               "also see",
    "similar":            "similar to",
    "participle":         "participle of",
    "pertainym":          "pertainyms (adj pertains to noun)",
    "derivation":         "derivationally related forms",
    "domain_topic":       "domain topic",
    "has_domain_topic":   "has domain topic",
    "domain_region":      "domain region",
    "has_domain_region":  "has domain region",
    "exemplifies":        "exemplifies",
    "is_exemplified_by":  "is exemplified by",
    "feminine":           "feminine form",
    "has_feminine":       "has feminine",
    "masculine":          "masculine form",
    "has_masculine":      "has masculine",
    "young":              "young form",
    "has_young":          "has young form",
    "diminutive":         "diminutive of",
    "has_diminutive":     "has diminutive",
    "augmentative":       "augmentative of",
    "has_augmentative":   "has augmentative",
    "simple_aspect_ip":   "simple aspect (ip)",
    "secondary_aspect_ip":"secondary aspect (ip)",
    "simple_aspect_pi":   "simple aspect (pi)",
    "secondary_aspect_pi":"secondary aspect (pi)",
    "metaphor":           "metaphor",
    "has_metaphor":       "has metaphor",
    "metonym":            "metonym",
    "has_metonym":        "has metonym",
    "agent":              "agent",
    "body_part":          "body part",
    "by_means_of":        "by means of",
    "destination":        "destination",
    "event":              "event",
    "instrument":         "instrument",
    "location":           "location",
    "material":           "material",
    "property":           "property",
    "result":             "result",
    "state":              "state",
    "undergoer":          "undergoer",
    "uses":               "uses",
    "vehicle":            "vehicle",
    "other":              "other",
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def hr(char="─"):
    return char * W


def heading(title):
    pad = W - len(title) - 2
    left = pad // 2
    right = pad - left
    return f"{'─' * left} {title} {'─' * right}"


def fmt_synset(s):
    words = s.lemmas()
    label = words[0] if words else s.id
    pos = POS_LABELS.get(s.pos, s.pos or "?")
    defn = s.definition() or ""
    snippet = (defn[:52] + "…") if len(defn) > 55 else defn
    return f"{label}  [{pos}]  — {snippet}"


def wrap_items(items, indent=4):
    if not items:
        return " " * indent + "(none)"
    bullet = " " * indent + "• "
    lines = []
    for item in items:
        wrapped = textwrap.fill(
            item,
            width=W,
            initial_indent=bullet,
            subsequent_indent=" " * (indent + 2),
        )
        lines.append(wrapped)
    return "\n".join(lines)


# ── Core relation collectors ─────────────────────────────────────────────────

def synset_relations(synset):
    """Return {label: [display_str]} for all populated synset relations."""
    raw = synset.relations()          # dict[str, list[Synset]]
    out = {}
    for rel_type, related in raw.items():
        if not related:
            continue
        label = SYNSET_REL_LABELS.get(rel_type, rel_type.replace("_", " "))
        out[label] = [fmt_synset(s) for s in related]
    return out


def sense_relations(sense):
    """Return {label: [display_str]} for all populated sense relations."""
    raw = sense.relations()           # dict[str, list[Sense]]
    out = {}
    for rel_type, related in raw.items():
        if not related:
            continue
        label = SENSE_REL_LABELS.get(rel_type, rel_type.replace("_", " "))
        entries = []
        for s in related:
            word = s.word()
            lemma = word.lemma() if word else "?"
            pos = POS_LABELS.get(s.synset().pos, "?")
            entries.append(f"{lemma}  [{pos}]")
        out[label] = entries
    return out


# ── Display ──────────────────────────────────────────────────────────────────

def print_synset_block(synset, word):
    pos_label = POS_LABELS.get(synset.pos, synset.pos or "?")
    synonyms = [l for l in synset.lemmas() if l.lower() != word.lower()]
    examples = synset.examples()
    defn = synset.definition() or "(no definition)"
    lexfile = synset.lexfile() or ""

    title = f"{synset.id}  [{pos_label}]"
    if lexfile:
        title += f"  {{{lexfile}}}"
    print(heading(title))
    print()
    print(f"  Definition : {defn}")

    if synonyms:
        print(f"  Synonyms   : {', '.join(synonyms)}")
    else:
        print(f"  Synonyms   : (sole lemma in this synset)")

    for ex in examples:
        print(f"  Example    : \"{ex}\"")
    print()

    # Synset-level relations
    print("  ── Synset relations ─────────────────────────────────────────────")
    s_rels = synset_relations(synset)
    if s_rels:
        for label, entries in s_rels.items():
            print(f"\n  {label.upper()}")
            print(wrap_items(entries, indent=4))
    else:
        print("    (none)")

    # Sense-level relations (per lemma)
    print()
    print("  ── Sense relations (per lemma) ──────────────────────────────────")
    any_sense_rel = False
    for sense in synset.senses():
        s_rels = sense_relations(sense)
        if s_rels:
            any_sense_rel = True
            word_obj = sense.word()
            lemma = word_obj.lemma() if word_obj else sense.id()
            print(f"\n  Lemma: {lemma}")
            for label, entries in s_rels.items():
                print(f"    {label.upper()}")
                print(wrap_items(entries, indent=6))
    if not any_sense_rel:
        print("    (none)")

    print()


def explore(word, pos_filter=None):
    try:
        en = wn.Wordnet(LEXICON)
    except wn.Error as e:
        print(f"\nCould not load lexicon '{LEXICON}': {e}")
        print("Run this once to download it:")
        print("  python -c \"import wn; wn.download('oewn:2024')\"")
        return

    words = en.words(word, pos=pos_filter)
    if not words:
        msg = f"No entries found for '{word}'"
        if pos_filter:
            msg += f" with pos='{pos_filter}'"
        print(msg)
        return

    # Collect all unique synsets across all matching words
    seen = set()
    synsets = []
    for w in words:
        for s in w.synsets():
            if s.id not in seen:
                seen.add(s.id)
                synsets.append(s)

    print()
    print(hr("═"))
    header = f"  WordNet relations for: {word.upper()}"
    if pos_filter:
        header += f"  (pos={pos_filter})"
    print(header)
    print(f"  {len(synsets)} sense{'s' if len(synsets) != 1 else ''} found  |  source: {LEXICON}")
    print(hr("═"))
    print()

    for synset in synsets:
        print_synset_block(synset, word)


# ── Entry points ─────────────────────────────────────────────────────────────

def interactive_mode():
    print()
    print("Open English WordNet Relation Explorer")
    print(f"Using: {LEXICON}")
    print("Type a word to explore. Optional POS filter, e.g.: happy --pos a")
    print("Type 'quit' to exit.")
    print()

    while True:
        try:
            raw = input("word> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not raw or raw.lower() in ("quit", "exit", "q"):
            break

        parts = raw.split()
        word = parts[0]
        pos_filter = None
        if "--pos" in parts:
            idx = parts.index("--pos")
            if idx + 1 < len(parts):
                pos_filter = parts[idx + 1]

        explore(word, pos_filter)


def main():
    args = sys.argv[1:]

    if not args:
        interactive_mode()
        return

    word = args[0]
    pos_filter = None
    if "--pos" in args:
        idx = args.index("--pos")
        if idx + 1 < len(args):
            pos_filter = args[idx + 1]

    explore(word, pos_filter)


if __name__ == "__main__":
    main()
