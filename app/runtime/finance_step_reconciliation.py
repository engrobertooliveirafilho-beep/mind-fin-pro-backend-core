"""Read-only reconciliation of 13 finance STEPs from MIND agent registry."""
FINANCE_STEPS=(124,136,139,154,170,177,190,210,211,239,281,497,498)
DRIVE_STUBS={
124:"1F9MfIvzFhb4awCEWjcsawTEgtlmLjT5m",
136:"130Y9fZW_3mxb7i-hbHzDdcK0fKjYBDne",
139:"178we-IFCNAwy_vWNTRXBaC-rcbzAFgR0",
154:"16wZkGPqt-oTLW-RWIEQ1K12Kiycg_3Ws",
170:"1ARqGyiPOXpzGqtYjnnzy8u3iKRd3dZAH",
190:"15Lk7VouGO0myTlUFxJgze61NB6Xr2lXO",
211:"1yB_j0ash_XHcQwvwN3ldJu82g_Qay7fT",
281:"1mNWkT4r9sCXR972wZCG4fP9ipbJMfnrN",
}
import ast

def _literal_assignments(source):
    try:
        tree=ast.parse(source)
    except SyntaxError as exc:
        raise ValueError("invalid STEP Python source") from exc
    assignments={}
    for node in tree.body:
        if not isinstance(node,ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target,ast.Name) and target.id in ("STEP_ID","STEP_STATUS"):
                if target.id in assignments:
                    raise ValueError("duplicate STEP metadata")
                try:
                    assignments[target.id]=ast.literal_eval(node.value)
                except (ValueError,TypeError,MemoryError,RecursionError) as exc:
                    raise ValueError("nonliteral STEP metadata") from exc
    return assignments,tree

def reconcile_finance_steps(source_by_step):
    if not isinstance(source_by_step,dict):
        raise TypeError("source mapping required")
    if any(type(k) is not int or k not in FINANCE_STEPS or not isinstance(v,str)
           for k,v in source_by_step.items()):
        raise ValueError("invalid STEP source")
    results=[]
    for step in FINANCE_STEPS:
        source=source_by_step.get(step)
        if source is None:
            state="NOT_YET_VERIFIED"
        else:
            metadata,tree=_literal_assignments(source)
            if type(metadata.get("STEP_ID")) is not int or metadata["STEP_ID"] != step:
                raise ValueError("STEP identity mismatch")
            approved=(metadata.get("STEP_STATUS") == "approved_stub")
            has_original_marker=any(
                isinstance(node,ast.Expr) and isinstance(node.value,ast.Constant)
                and isinstance(node.value.value,str)
                and "A lógica REAL deste STEP deve ser implementada" in node.value.value
                for node in tree.body
            )
            state="APPROVED_STUB" if approved and has_original_marker else "REQUIRES_CODE_REVIEW"
        results.append({"step_id":step,"state":state,
                        "drive_source_id":DRIVE_STUBS.get(step),"certified":False})
    return results
