from __future__ import annotations
import json, math, random, statistics
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

class USDECore:
    """
    P4.46X — Universal Scientific Discovery Engine.
    Motor científico universal para ingestão, validação, refutação, walk-forward,
    baseline, red team, anti-overfitting e decisão de hipótese.
    """

    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.seed = seed

    def validate_events(self, events: list[dict]) -> list[dict]:
        assert isinstance(events, list) and len(events) >= 3, "dataset_insufficient"
        ids = [e["id"] for e in events]
        assert ids == sorted(ids), "temporal_order_invalid"
        assert len(ids) == len(set(ids)), "duplicate_event_id"
        return events

    def normalize(self, events: list[dict]) -> list[dict]:
        clean = []
        for e in events:
            values = sorted(set(e.get("values", [])))
            clean.append({"id": int(e["id"]), "values": values})
        return self.validate_events(clean)

    def event_matrix(self, events: list[dict]) -> dict:
        universe = sorted(set(v for e in events for v in e["values"]))
        matrix = []
        for e in events:
            s = set(e["values"])
            matrix.append({"id": e["id"], **{str(v): int(v in s) for v in universe}})
        return {"universe": universe, "matrix": matrix}

    def frequency_metrics(self, events: list[dict]) -> dict:
        n = len(events)
        c = Counter(v for e in events for v in e["values"])
        universe = sorted(c)
        return {
            str(v): {
                "count": c[v],
                "frequency": c[v] / n,
                "absence_frequency": 1 - (c[v] / n)
            } for v in universe
        }

    def interval_metrics(self, events: list[dict]) -> dict:
        universe = sorted(set(v for e in events for v in e["values"]))
        out = {}
        for v in universe:
            pos = [i for i, e in enumerate(events) if v in e["values"]]
            gaps = [b - a for a, b in zip(pos, pos[1:])]
            current_gap = len(events) - 1 - pos[-1] if pos else None
            out[str(v)] = {
                "occurrences": len(pos),
                "avg_gap": statistics.mean(gaps) if gaps else None,
                "max_gap": max(gaps) if gaps else None,
                "current_gap": current_gap
            }
        return out

    def combo_metrics(self, events: list[dict], k: int) -> dict:
        c = Counter()
        for e in events:
            for combo in combinations(sorted(e["values"]), k):
                c[combo] += 1
        return {"-".join(map(str, k_)): v for k_, v in c.most_common()}

    def markov_matrix(self, events: list[dict]) -> dict:
        universe = sorted(set(v for e in events for v in e["values"]))
        trans = defaultdict(lambda: Counter())
        base = Counter()
        for a, b in zip(events, events[1:]):
            A, B = set(a["values"]), set(b["values"])
            for x in universe:
                if x in A:
                    base[x] += 1
                    for y in universe:
                        if y in B:
                            trans[x][y] += 1
        return {
            str(x): {str(y): (trans[x][y] / base[x] if base[x] else 0.0) for y in universe}
            for x in universe
        }

    def shannon_entropy(self, events: list[dict]) -> dict:
        freq = self.frequency_metrics(events)
        probs = [v["frequency"] for v in freq.values()]
        entropy = -sum(p * math.log2(p) for p in probs if p > 0)
        return {"shannon_entropy": entropy, "variables": len(probs)}

    def monte_carlo_baseline(self, events: list[dict], trials: int = 10000) -> dict:
        universe = sorted(set(v for e in events for v in e["values"]))
        k = round(statistics.mean(len(e["values"]) for e in events))
        samples = []
        for _ in range(trials):
            s = set(random.sample(universe, k))
            samples.append(len(s))
        return {
            "trials": trials,
            "universe_size": len(universe),
            "sample_size": k,
            "mean_random_size": statistics.mean(samples)
        }

    def walk_forward(self, events: list[dict]) -> dict:
        records = []
        for i in range(2, len(events) - 1):
            train = events[:i+1]
            target = set(events[i+1]["values"])
            freq = self.frequency_metrics(train)
            ranked = sorted(freq, key=lambda x: freq[x]["frequency"], reverse=True)
            k = len(events[i+1]["values"])
            hypothesis = set(map(int, ranked[:k]))
            hit = len(hypothesis & target)
            records.append({
                "train_until": events[i]["id"],
                "test_event": events[i+1]["id"],
                "hit": hit,
                "target_size": k,
                "accuracy": hit / k
            })
        avg = statistics.mean(r["accuracy"] for r in records) if records else 0
        return {"records": records, "avg_accuracy": avg}

    def red_team(self, wf: dict) -> dict:
        flags = []
        if wf["avg_accuracy"] >= 0.90:
            flags.append("EXTREME_ACCURACY_REQUIRES_LEAKAGE_AUDIT")
        if len(wf["records"]) < 30:
            flags.append("LOW_SAMPLE_SIZE")
        return {
            "flags": flags,
            "status": "AUDIT_REQUIRED" if flags else "NO_CRITICAL_FLAGS"
        }

    def decide(self, wf: dict, red: dict) -> dict:
        if red["status"] == "AUDIT_REQUIRED":
            decision = "INCONCLUSIVA"
        elif wf["avg_accuracy"] > 0.0:
            decision = "INCONCLUSIVA"
        else:
            decision = "HIPOTESE_REJEITADA"
        return {
            "decision": decision,
            "avg_accuracy": wf["avg_accuracy"],
            "red_team_status": red["status"],
            "rule": "Aprovação exige baseline, p-value, IC positivo, baixa degradação e ausência de vazamento."
        }

    def run(self, events: list[dict], outdir: str) -> dict:
        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        events = self.normalize(events)

        artifacts = {
            "normalized_dataset.json": events,
            "event_matrix.json": self.event_matrix(events),
            "frequency_metrics.json": self.frequency_metrics(events),
            "interval_metrics.json": self.interval_metrics(events),
            "pair_metrics.json": self.combo_metrics(events, 2),
            "trio_metrics.json": self.combo_metrics(events, 3),
            "markov_matrix.json": self.markov_matrix(events),
            "entropy_report.json": self.shannon_entropy(events),
            "monte_carlo_report.json": self.monte_carlo_baseline(events, 10000),
        }

        wf = self.walk_forward(events)
        red = self.red_team(wf)
        decision = self.decide(wf, red)

        artifacts["walk_forward_report.json"] = wf
        artifacts["red_team_report.json"] = red
        artifacts["hypothesis_decision.json"] = decision

        for name, data in artifacts.items():
            (out / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        (out / "final_audit_report.md").write_text(
            f"# P4.46X USDE FINAL AUDIT\n\nDecision: {decision['decision']}\nAccuracy: {decision['avg_accuracy']}\nRed Team: {decision['red_team_status']}\n",
            encoding="utf-8"
        )
        return decision
