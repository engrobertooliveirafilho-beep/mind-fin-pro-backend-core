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
def reconcile_finance_steps(source_by_step):
    if not isinstance(source_by_step,dict): raise TypeError("source mapping required")
    if any(type(k) is not int or k not in FINANCE_STEPS or not isinstance(v,str) for k,v in source_by_step.items()):
        raise ValueError("invalid STEP source")
    results=[]
    for step in FINANCE_STEPS:
        source=source_by_step.get(step)
        if source is None:
            state="NOT_YET_VERIFIED"
        elif f"STEP_ID = {step}" not in source:
            raise ValueError("STEP identity mismatch")
        elif 'STEP_STATUS = "approved_stub"' in source and "A lógica REAL deste STEP deve ser implementada" in source:
            state="APPROVED_STUB"
        else:
            state="REQUIRES_CODE_REVIEW"
        results.append({"step_id":step,"state":state,"drive_source_id":DRIVE_STUBS.get(step),"certified":False})
    return results
