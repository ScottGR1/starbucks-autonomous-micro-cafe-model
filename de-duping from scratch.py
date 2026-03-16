records = [
    {"name": "Alice", "score": 10},
    {"name": "Alice", "score": 10},  # duplicate
    {"name": "Bob", "score": None},
    {"name": "Alice", "score": 5},
]



def dedupe_and_aggregate(records):
#creating a set to track dupes based on name and score
    SeenBefore = set()
    totals = {} # to hold aggregated scores

    for i in records:
        key = (i["name"], i["score"])
        if key in SeenBefore:
            continue
        SeenBefore.add(key)
        print("Unique record:", i)

    #lets normalize nulls (we wont be able to sum with nulls)
        if i["score"] is None:
            i["score"] = 0
            print(i)

    #time to aggregate scores by name
    name = i["name"]
    score = i["score"]

    if name not in totals:
        totals[name] = 0
        totals[name]+= score
    return totals


deduped_records = dedupe_and_aggregate(records)
