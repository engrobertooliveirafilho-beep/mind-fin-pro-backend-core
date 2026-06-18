from __future__ import annotations
import statistics

class WalkForwardEngine:
    def evaluate(self, events:list[dict], predictor)->dict:
        records=[]

        for i in range(2,len(events)-1):
            train=events[:i+1]
            target=set(events[i+1]["values"])

            prediction=set(predictor(train))

            hit=len(prediction & target)

            records.append({
                "train_until":events[i]["id"],
                "test_event":events[i+1]["id"],
                "hit":hit,
                "prediction_size":len(prediction),
                "target_size":len(target),
                "accuracy":hit/max(1,len(target))
            })

        avg=statistics.mean(r["accuracy"] for r in records) if records else 0.0

        return {
            "records":records,
            "evaluations":len(records),
            "avg_accuracy":avg
        }
