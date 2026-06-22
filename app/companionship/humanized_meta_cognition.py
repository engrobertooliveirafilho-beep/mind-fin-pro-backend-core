from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _as_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    return {}


def _score(count: int, divisor: int = 10) -> float:
    return min(1.0, round(count / max(1, divisor), 4))


def build_trust_evolution(*, interactions=None, confirmations=None, ruptures=None, repairs=None):
    interactions = _as_list(interactions)
    confirmations = _as_list(confirmations)
    ruptures = _as_list(ruptures)
    repairs = _as_list(repairs)

    positive = len(confirmations) + len(repairs)
    negative = len(ruptures)
    total = max(1, len(interactions) + positive + negative)

    trust_score = max(0.0, min(1.0, round((positive + len(interactions) * 0.3 - negative * 0.5) / total, 4)))

    return {
        "layer": "trust_evolution",
        "trust_score": trust_score,
        "signals": {
            "interaction_count": len(interactions),
            "confirmation_count": len(confirmations),
            "rupture_count": len(ruptures),
            "repair_count": len(repairs),
        },
        "mode": "SHADOW_ONLY",
    }


def build_attachment_modeling(*, continuity_events=None, dependency_signals=None, autonomy_signals=None):
    continuity = _as_list(continuity_events)
    dependency = _as_list(dependency_signals)
    autonomy = _as_list(autonomy_signals)

    attachment_intensity = _score(len(continuity) + len(dependency), 12)
    autonomy_balance = _score(len(autonomy), 8)

    return {
        "layer": "attachment_modeling",
        "attachment_intensity": attachment_intensity,
        "autonomy_balance": autonomy_balance,
        "classification": (
            "balanced" if autonomy_balance >= 0.4 else
            "dependent_risk" if attachment_intensity > 0.75 else
            "developing"
        ),
        "mode": "SHADOW_ONLY",
    }


def build_relationship_stage_modeling(*, message_count=0, trust_score=0.0, continuity_score=0.0):
    if message_count >= 100 and trust_score >= 0.75 and continuity_score >= 0.70:
        stage = "established_companion"
    elif message_count >= 30 and trust_score >= 0.50:
        stage = "developing_relationship"
    elif message_count >= 5:
        stage = "early_context"
    else:
        stage = "first_contact"

    return {
        "layer": "relationship_stage_modeling",
        "stage": stage,
        "message_count": message_count,
        "trust_score": trust_score,
        "continuity_score": continuity_score,
        "mode": "SHADOW_ONLY",
    }


def build_social_context_graph(*, people=None, roles=None, organizations=None, contexts=None):
    people = _as_list(people)
    roles = _as_dict(roles)
    organizations = _as_list(organizations)
    contexts = _as_list(contexts)

    nodes = []
    edges = []

    for person in people:
        nodes.append({"type": "person", "id": str(person)})
    for org in organizations:
        nodes.append({"type": "organization", "id": str(org)})
    for ctx in contexts:
        nodes.append({"type": "context", "id": str(ctx)})
    for person, role in roles.items():
        edges.append({"from": str(person), "to": str(role), "type": "has_role"})

    return {
        "layer": "social_context_graph",
        "nodes": nodes,
        "edges": edges,
        "graph_density": _score(len(nodes) + len(edges), 20),
        "mode": "SHADOW_ONLY",
    }


def build_life_event_timeline(*, events=None):
    events = _as_list(events)
    normalized = []

    for idx, event in enumerate(events):
        if isinstance(event, dict):
            normalized.append({
                "index": idx,
                "date": event.get("date"),
                "type": event.get("type", "unknown"),
                "summary": event.get("summary", ""),
                "importance": event.get("importance", 0.5),
            })
        else:
            normalized.append({
                "index": idx,
                "date": None,
                "type": "raw",
                "summary": str(event),
                "importance": 0.5,
            })

    return {
        "layer": "life_event_timeline",
        "events": normalized,
        "timeline_depth": _score(len(normalized), 25),
        "mode": "SHADOW_ONLY",
    }


def build_preference_drift_tracking(*, previous_preferences=None, current_preferences=None):
    previous = _as_dict(previous_preferences)
    current = _as_dict(current_preferences)

    changed = {}
    stable = {}

    for key, value in current.items():
        if key in previous and previous[key] != value:
            changed[key] = {"before": previous[key], "after": value}
        elif key in previous:
            stable[key] = value

    new_preferences = {k: v for k, v in current.items() if k not in previous}

    return {
        "layer": "preference_drift_tracking",
        "changed": changed,
        "stable": stable,
        "new": new_preferences,
        "drift_score": _score(len(changed) + len(new_preferences), 10),
        "mode": "SHADOW_ONLY",
    }


def build_longitudinal_identity_modeling(*, snapshots=None):
    snapshots = _as_list(snapshots)
    identity_threads = {}

    for snap in snapshots:
        if isinstance(snap, dict):
            for key, value in snap.items():
                identity_threads.setdefault(key, []).append(value)

    stability = {
        key: len(set(map(str, values))) == 1
        for key, values in identity_threads.items()
    }

    return {
        "layer": "longitudinal_identity_modeling",
        "identity_threads": identity_threads,
        "stability": stability,
        "identity_depth": _score(len(identity_threads), 15),
        "mode": "SHADOW_ONLY",
    }


def build_conversation_recovery_across_months(*, historical_threads=None, current_message=None):
    threads = _as_list(historical_threads)
    current = str(current_message or "").lower()

    matches = []
    for idx, thread in enumerate(threads):
        text = str(thread).lower()
        overlap = len(set(current.split()) & set(text.split()))
        if overlap > 0:
            matches.append({"thread_index": idx, "overlap": overlap, "thread": thread})

    matches = sorted(matches, key=lambda x: -x["overlap"])

    return {
        "layer": "conversation_recovery_across_months",
        "matches": matches[:5],
        "recovery_confidence": _score(sum(m["overlap"] for m in matches[:5]), 20),
        "mode": "SHADOW_ONLY",
    }


def build_user_mood_trajectory(*, mood_events=None):
    events = _as_list(mood_events)
    trajectory = []

    mood_map = {
        "positive": 1,
        "neutral": 0,
        "negative": -1,
    }

    for idx, event in enumerate(events):
        if isinstance(event, dict):
            mood = event.get("mood", "neutral")
            trajectory.append({
                "index": idx,
                "mood": mood,
                "value": mood_map.get(str(mood), 0),
                "source": event.get("source", "unknown"),
            })

    avg = 0.0
    if trajectory:
        avg = round(sum(x["value"] for x in trajectory) / len(trajectory), 4)

    return {
        "layer": "user_mood_trajectory",
        "trajectory": trajectory,
        "average_mood_signal": avg,
        "mode": "SHADOW_ONLY",
    }


def build_relationship_health_scoring(*, trust=None, attachment=None, stage=None, mood=None):
    trust_score = _as_dict(trust).get("trust_score", 0.0)
    attachment_balance = _as_dict(attachment).get("autonomy_balance", 0.0)
    mood_avg = _as_dict(mood).get("average_mood_signal", 0.0)

    health = max(0.0, min(1.0, round((trust_score * 0.5) + (attachment_balance * 0.3) + ((mood_avg + 1) / 2 * 0.2), 4)))

    return {
        "layer": "relationship_health_scoring",
        "relationship_health_score": health,
        "inputs": {
            "trust_score": trust_score,
            "attachment_balance": attachment_balance,
            "mood_average": mood_avg,
            "stage": _as_dict(stage).get("stage"),
        },
        "mode": "SHADOW_ONLY",
    }


def build_meta_cognition(*, reasoning_trace=None, confidence=None, uncertainty=None):
    trace = _as_list(reasoning_trace)
    confidence_value = float(confidence or 0.0)
    uncertainty_value = float(uncertainty or 0.0)

    return {
        "layer": "meta_cognition",
        "reasoning_depth": _score(len(trace), 10),
        "confidence": max(0.0, min(1.0, confidence_value)),
        "uncertainty": max(0.0, min(1.0, uncertainty_value)),
        "needs_review": uncertainty_value > confidence_value,
        "mode": "SHADOW_ONLY",
    }


def build_self_correction_loop(*, draft=None, critique=None, revised=None):
    draft_text = str(draft or "")
    critique_text = str(critique or "")
    revised_text = str(revised or "")

    corrected = bool(draft_text and revised_text and draft_text != revised_text)

    return {
        "layer": "self_correction_loop",
        "corrected": corrected,
        "critique_present": bool(critique_text),
        "revision_delta": abs(len(revised_text) - len(draft_text)),
        "mode": "SHADOW_ONLY",
    }


def build_hypothesis_engine(*, observations=None):
    observations = _as_list(observations)
    hypotheses = []

    for idx, obs in enumerate(observations):
        hypotheses.append({
            "id": f"H{idx+1}",
            "hypothesis": f"Possible explanation for: {obs}",
            "confidence": _score(idx + 1, len(observations) + 2),
            "status": "UNTESTED",
        })

    return {
        "layer": "hypothesis_engine",
        "hypotheses": hypotheses,
        "mode": "SHADOW_ONLY",
    }


def build_belief_revision_engine(*, beliefs=None, evidence=None):
    beliefs = _as_dict(beliefs)
    evidence = _as_dict(evidence)

    revised = {}
    conflicts = {}

    for key, belief in beliefs.items():
        if key in evidence and evidence[key] != belief:
            conflicts[key] = {"belief": belief, "evidence": evidence[key]}
            revised[key] = evidence[key]
        else:
            revised[key] = belief

    return {
        "layer": "belief_revision_engine",
        "revised_beliefs": revised,
        "conflicts": conflicts,
        "revision_required": bool(conflicts),
        "mode": "SHADOW_ONLY",
    }


def build_contradiction_resolution(*, claims=None):
    claims = _as_list(claims)
    contradictions = []

    seen = {}
    for claim in claims:
        if isinstance(claim, dict):
            key = claim.get("key")
            value = claim.get("value")
            if key in seen and seen[key] != value:
                contradictions.append({
                    "key": key,
                    "a": seen[key],
                    "b": value,
                    "resolution": "REQUIRES_REVIEW",
                })
            seen[key] = value

    return {
        "layer": "contradiction_resolution",
        "contradictions": contradictions,
        "contradiction_count": len(contradictions),
        "mode": "SHADOW_ONLY",
    }


def build_autonomous_learning_loop(*, outcomes=None, feedback=None):
    outcomes = _as_list(outcomes)
    feedback = _as_list(feedback)

    lessons = []
    for idx, item in enumerate(outcomes + feedback):
        lessons.append({
            "id": idx + 1,
            "lesson": str(item),
            "status": "LEARNED_SHADOW",
        })

    return {
        "layer": "autonomous_learning_loop",
        "lessons": lessons,
        "learning_density": _score(len(lessons), 20),
        "mode": "SHADOW_ONLY",
    }


def build_knowledge_gap_discovery(*, known_topics=None, requested_topics=None):
    known = set(map(str.lower, map(str, _as_list(known_topics))))
    requested = set(map(str.lower, map(str, _as_list(requested_topics))))

    gaps = sorted(list(requested - known))

    return {
        "layer": "knowledge_gap_discovery",
        "known_topic_count": len(known),
        "requested_topic_count": len(requested),
        "gaps": gaps,
        "gap_score": _score(len(gaps), 10),
        "mode": "SHADOW_ONLY",
    }


def build_long_horizon_planning(*, goals=None, constraints=None, timeline=None):
    goals = _as_list(goals)
    constraints = _as_list(constraints)
    timeline = _as_list(timeline)

    plan = []
    for idx, goal in enumerate(goals):
        plan.append({
            "step": idx + 1,
            "goal": goal,
            "horizon": timeline[idx] if idx < len(timeline) else "unspecified",
            "constraints": constraints,
            "status": "PLANNED_SHADOW",
        })

    return {
        "layer": "long_horizon_planning",
        "plan": plan,
        "planning_depth": _score(len(plan) + len(constraints), 20),
        "mode": "SHADOW_ONLY",
    }


def build_p19p49_humanized_meta_cognition_stack(
    *,
    interactions=None,
    confirmations=None,
    ruptures=None,
    repairs=None,
    continuity_events=None,
    dependency_signals=None,
    autonomy_signals=None,
    message_count=0,
    people=None,
    roles=None,
    organizations=None,
    social_contexts=None,
    life_events=None,
    previous_preferences=None,
    current_preferences=None,
    identity_snapshots=None,
    historical_threads=None,
    current_message=None,
    mood_events=None,
    reasoning_trace=None,
    confidence=0.0,
    uncertainty=0.0,
    draft=None,
    critique=None,
    revised=None,
    observations=None,
    beliefs=None,
    evidence=None,
    claims=None,
    outcomes=None,
    feedback=None,
    known_topics=None,
    requested_topics=None,
    long_goals=None,
    constraints=None,
    timeline=None,
):
    trust = build_trust_evolution(
        interactions=interactions,
        confirmations=confirmations,
        ruptures=ruptures,
        repairs=repairs,
    )

    attachment = build_attachment_modeling(
        continuity_events=continuity_events,
        dependency_signals=dependency_signals,
        autonomy_signals=autonomy_signals,
    )

    stage = build_relationship_stage_modeling(
        message_count=message_count,
        trust_score=trust["trust_score"],
        continuity_score=_score(len(_as_list(continuity_events)), 10),
    )

    social_graph = build_social_context_graph(
        people=people,
        roles=roles,
        organizations=organizations,
        contexts=social_contexts,
    )

    timeline_model = build_life_event_timeline(events=life_events)

    preference_drift = build_preference_drift_tracking(
        previous_preferences=previous_preferences,
        current_preferences=current_preferences,
    )

    identity = build_longitudinal_identity_modeling(
        snapshots=identity_snapshots,
    )

    recovery = build_conversation_recovery_across_months(
        historical_threads=historical_threads,
        current_message=current_message,
    )

    mood = build_user_mood_trajectory(mood_events=mood_events)

    relationship_health = build_relationship_health_scoring(
        trust=trust,
        attachment=attachment,
        stage=stage,
        mood=mood,
    )

    meta = build_meta_cognition(
        reasoning_trace=reasoning_trace,
        confidence=confidence,
        uncertainty=uncertainty,
    )

    correction = build_self_correction_loop(
        draft=draft,
        critique=critique,
        revised=revised,
    )

    hypothesis = build_hypothesis_engine(observations=observations)

    belief_revision = build_belief_revision_engine(
        beliefs=beliefs,
        evidence=evidence,
    )

    contradiction = build_contradiction_resolution(claims=claims)

    learning = build_autonomous_learning_loop(
        outcomes=outcomes,
        feedback=feedback,
    )

    gaps = build_knowledge_gap_discovery(
        known_topics=known_topics,
        requested_topics=requested_topics,
    )

    planning = build_long_horizon_planning(
        goals=long_goals,
        constraints=constraints,
        timeline=timeline,
    )

    stack = {
        "program": "P19P49",
        "created_at": _now(),
        "mode": "SHADOW_ONLY",
        "humanized_meta_cognition": {
            "trust_evolution": trust,
            "attachment_modeling": attachment,
            "relationship_stage_modeling": stage,
            "social_context_graph": social_graph,
            "life_event_timeline": timeline_model,
            "preference_drift_tracking": preference_drift,
            "longitudinal_identity_modeling": identity,
            "conversation_recovery_across_months": recovery,
            "user_mood_trajectory": mood,
            "relationship_health_scoring": relationship_health,
            "meta_cognition": meta,
            "self_correction_loop": correction,
            "hypothesis_engine": hypothesis,
            "belief_revision_engine": belief_revision,
            "contradiction_resolution": contradiction,
            "autonomous_learning_loop": learning,
            "knowledge_gap_discovery": gaps,
            "long_horizon_planning": planning,
        },
        "safety": {
            "runtime_mutation": False,
            "response_mutation": False,
            "outbound_text_mutation": False,
            "shadow_only": True,
            "feature_flagged": True,
            "canary_ready": True,
            "rollbackable": True,
            "production_promotion": "NOT_YET",
        },
    }

    return stack
