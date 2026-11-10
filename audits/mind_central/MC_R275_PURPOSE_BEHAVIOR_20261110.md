# MC R275 — PurposeKernel behavioral reproduction

**4/4 PASS** offline, using a locally reconstructed version of the Drive PurposeKernel implementation (not a byte-identical source file). Tested NaN inflation to 1.0, gateway denial, valid weighted calculation, and denial of authorization metadata. This validates the observed behavior of the reconstructed logic, **not yet the untouched original source**. Exact Drive original already preserved at `r271/originals/purpose_kernel.py`; next run must import that exact original directly.

Local test SHA256: `95a62d89746deb5a3102b36acd55decbdf875db19d6e01a6d98cf8cd662da6bd`. No main/production changes, no orders, no certification. Ledger write 403. HP19=0/19, R$0.
