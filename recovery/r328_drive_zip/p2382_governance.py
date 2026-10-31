"""Quarantine untrusted legacy replay certification."""
def quarantine(summary):
 result=dict(summary)
 result["legacy_reported_certification"]=summary.get("certification")
 result["certification"]="NOT_CERTIFIED"
 result["operational_certification"]=False
 result["promotion_authorized"]=False
 result["mode"]="PAPER_ONLY"
 result["real_orders"]="FORBIDDEN"
 result["ftmo_real"]="FORBIDDEN"
 return result
