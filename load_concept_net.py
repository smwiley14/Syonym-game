import gzip
import json
import csv


RELATION_MIN_WEIGHT = {
    'default': 1.0,
    '/r/RelatedTo': 2.0,  # stricter — RelatedTo is very broad
}
RELATION_WHITELIST = {
    '/r/UsedFor', '/r/CapableOf', '/r/AtLocation', '/r/MadeOf',
    '/r/HasProperty', '/r/Causes', '/r/PartOf', '/r/SimilarTo', '/r/IsA', 
    '/r/Synonym',
}

def passes_weight(rel, weight):
    threshold = RELATION_MIN_WEIGHT.get(rel, RELATION_MIN_WEIGHT['default'])
    return weight >= threshold


with gzip.open('/Users/sam/Downloads/conceptnet-assertions-5.7.0.csv.gz', 'rt', encoding='utf-8') as infile, \
     open('/Users/sam/Downloads/conceptnet_game_ready.csv', 'w', newline='', encoding='utf-8') as outfile:

    writer = csv.writer(outfile)
    writer.writerow(['start', 'rel', 'end', 'weight'])

    for line in infile:
        parts = line.strip().split('\t')
        if len(parts) != 5:
            continue
        _, rel, start, end, meta = parts
        if not (start.startswith('/c/en/') and end.startswith('/c/en/')):
            continue
        if rel not in RELATION_WHITELIST:
            continue
        try:
            weight = json.loads(meta).get('weight', 1.0)
        except (json.JSONDecodeError, AttributeError):
            weight = 1.0
        if not passes_weight(rel, weight):
            continue
        start_term = start.split('/')[3]
        end_term = end.split('/')[3]
        rel_clean = rel.split('/')[-1]
        writer.writerow([start_term, rel_clean, end_term, weight])

print("Done")




# import gzip, json
# from collections import Counter

# rel_counts = Counter()

# with gzip.open('/Users/sam/Downloads/conceptnet-assertions-5.7.0.csv.gz', 'rt', encoding='utf-8') as infile:
#     for i, line in enumerate(infile):
#         parts = line.rstrip('\n').split('\t')
#         if len(parts) != 5:
#             continue
#         _, rel, start, end, meta = parts
#         if not (start.startswith('/c/en/') and end.startswith('/c/en/')):
#             continue
#         try:
#             weight = json.loads(meta).get('weight', 1.0)
#         except (json.JSONDecodeError, AttributeError):
#             weight = 1.0
#         if weight <= 1.0:
#             continue
#         rel_counts[rel] += 1
#         if i % 5_000_000 == 0:
#             print(f"...{i:,} scanned")

# print("\nRelation counts (en-en, weight > 1.0):")
# for rel, c in rel_counts.most_common(40):
#     print(f"{rel}: {c:,}")

# import gzip, json
# from collections import Counter

# target_rels = {'/r/Synonym', '/r/Antonym'}
# weight_buckets = {r: Counter() for r in target_rels}

# with gzip.open('/Users/sam/Downloads/conceptnet-assertions-5.7.0.csv.gz', 'rt', encoding='utf-8') as infile:
#     for line in infile:
#         parts = line.rstrip('\n').split('\t')
#         if len(parts) != 5:
#             continue
#         _, rel, start, end, meta = parts
#         if rel not in target_rels:
#             continue
#         if not (start.startswith('/c/en/') and end.startswith('/c/en/')):
#             continue
#         try:
#             weight = json.loads(meta).get('weight', 1.0)
#         except (json.JSONDecodeError, AttributeError):
#             weight = 1.0
#         weight_buckets[rel][round(weight, 1)] += 1

# for rel, buckets in weight_buckets.items():
#     print(f"\n{rel}:")
#     for w in sorted(buckets):
#         print(f"  weight {w}: {buckets[w]:,}")