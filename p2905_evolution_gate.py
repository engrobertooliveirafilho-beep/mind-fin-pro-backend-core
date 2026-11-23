"""P2905 promotion gate derived from the recovered Drive chain.

Proxy payoff/stability values are descriptive only. They cannot certify a
specialist. No broker, network, or order-execution capability is included.
"""

def classify_specialist(payoff_proxy, stability_proxy, independent_oos_evidence=None):
    """Return a non-promotable status unless independently verifiable evidence exists.

    The historical chain does not define a verifiable evidence schema, so this
    gate intentionally keeps every specialist unverified rather than inventing
    acceptance thresholds or trusting self-attested metrics.
    """
    return {
        "status": "UNVERIFIED_CANDIDATE",
        "certification_basis": "BLOCKED_NO_INDEPENDENT_OOS_EVIDENCE",
        "proxy_metrics": {
            "payoff_proxy": payoff_proxy,
            "stability_proxy": stability_proxy,
        },
        "mutation_allowed": True,
        "retirement_candidate": False,
    }


def summarize(records):
    classified = [classify_specialist(
        r.get("payoff_proxy"), r.get("stability_proxy"),
        r.get("independent_oos_evidence")
    ) for r in records]
    return {
        "specialists": len(classified),
        "certified_core": 0,
        "unverified_candidates": len(classified),
        "records": classified,
    }
