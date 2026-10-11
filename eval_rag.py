from rag_test import ask

test_cases = [
    {
        "question": "What happens when I exceed my Fabric capacity",
        "expected_keywords": ["throttl", "smoothing", "24"],
        "should_find_answer" : True
        },

    {
        "question": "What does Dataflow Gen2 use as its underlying engine?",
        "expected_keywords":["Power Query", "M code"],
        "should_find_answer": True
        }
    ]


# results = []

# for case in test_cases:
#     question = case["question"]
#     actual_answer = ask(question)
#     results.append({
#         "question": question,
#         "actual_answer":actual_answer,
#         "expected_keywords": case["expected_keywords"]
#     })

# for r in results:
#     print(f"Q: {r['question']}")
#     print(f"A:{r['actual_answer']}")
#     print("---")



def check_answer(actual_answer, expected_keywords):
    actual_lower = actual_answer.lower()
    matched = [kw for kw in expected_keywords if kw.lower() in actual_lower]
    score = len(matched) / len(expected_keywords) if expected_keywords else 0
    return {
        "matched_keywords" : matched,
        "score" : score
    }

def run_eval(test_cases):
    results = []
    for case in test_cases:
        question = case["question"]
        actual_answer = ask(question)
        check = check_answer(actual_answer, case["expected_keywords"])
        results.append({
            "question": question,
            "actual_answer": actual_answer,
            "score": check["score"],
            "matched_keywords": check["matched_keywords"]
        })

    total_score = sum(r["score"] for r in results) / len(results)
    failed_cases = [r for r in results if r["score"] < 1.0]

    print(f"Overall average score: {total_score:.2f}")
    print(f"Failed cases: {len(failed_cases)} out of {len(results)}")
    for r in failed_cases:
        print(f"- {r['question']} (score: {r['score']:.2f})")

    for r in results:
        print(f"\nQ: {r['question']}")
        print(f"A: {r['actual_answer']}")
        print(f"Matched: {r['matched_keywords']}")

    return results


if __name__ == "__main__":
    run_eval(test_cases)