records = [
    {"name": "Alice", "score": 10},
    {"name": "Alice", "score": 10},  # duplicate
    {"name": "Bob", "score": None},
    {"name": "Alice", "score": 5},
]


#build a function to dedupe and aggregate

def dedupe_and_aggregate(records):
    seen = set()
    totals = {}

    for record in records:
        key = (record["name"], record["score"])
        if key in seen:
            continue
        seen.add(key)

        score = record["score"]
        if score is None:
            score = 0

        name = record["name"]
        totals[name] = totals.get(name, 0) + score

    result = []
    for name, total in totals.items():
        result.append({"name": name, "score": total})

    return result
deduped_records = dedupe_and_aggregate(records)
print(deduped_records)