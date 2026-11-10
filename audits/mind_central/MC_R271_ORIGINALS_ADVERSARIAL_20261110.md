# MC R271 — Historical source recovery + adversarial gateway checks

Drive sources preserved without modification in this branch:
- `r271/originals/purpose_kernel.py` Drive `1Nz9OgFwIR7hSnfh4ReNVmUCZwsIMkJkg`
- `r271/originals/computational_will.py` Drive `1k5vdvklut7SSeW0wgixI2zDxg5sqORKb`
- `r271/originals/auto_explanation.py` Drive `16NUyG3OdvLB7XrIjXfGIQjEFaISWIDTy`

Offline adversarial tests on R270 gateway (fake engines, not original modules): **4/4 PASS**. Cases: NaN across all five candidate positions, purpose NaN, ethics NaN, and explicit demonstration that nested metadata such as `authorization=real_orders` is passed through untouched. The latter is a **missing authorization boundary**, not evidence of execution or permission; it must be separately rejected by a higher-level authority gate. No actual order or external call.

The original modules were published for subsequent byte-accurate testing; this run did **not** execute those originals. No integrated certification. Ledger write blocked (Google 403). HP19 0/19; main untouched; R$0.
