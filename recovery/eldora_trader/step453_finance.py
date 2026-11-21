"""Opt-in STEP453 numeric safety adapter. No trading or I/O."""
import math

class NumericSafetyError(ValueError):
    pass

def npv(rate, cashflows):
    if isinstance(rate, bool) or not isinstance(rate, (float, int)) or not math.isfinite(rate) or rate <= -1:
        raise NumericSafetyError('rate must be finite and greater than -1')
    if not isinstance(cashflows, (list, tuple)) or not cashflows:
        raise NumericSafetyError('cashflows must be nonempty')
    total = 0.0
    for t, value in enumerate(cashflows):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise NumericSafetyError('cashflow must be finite')
        try:
            discounted = value / ((1.0 + rate) ** t)
            total = math.fsum((total, discounted))
        except (OverflowError, ZeroDivisionError) as exc:
            raise NumericSafetyError('numerically unstable NPV') from exc
        if not math.isfinite(total):
            raise NumericSafetyError('nonfinite NPV')
    return total

def solve_linear(a, b):
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in (a, b)):
        raise NumericSafetyError('finite coefficients required')
    if a == 0:
        return {'type': 'infinite_solutions' if b == 0 else 'no_solution'}
    x = -b / a
    if not math.isfinite(x):
        raise NumericSafetyError('nonfinite root')
    return {'type': 'unique_solution', 'x': x}
