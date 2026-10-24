"""Planning arithmetic; exact finite-population tail inversion, stdlib only."""
from __future__ import annotations

import math
from statistics import NormalDist


def wilson_lower(successes, n, alpha=.05):
    if type(n) is not int or type(successes) is not int or not 0 <= successes <= n or not 0 < alpha < .5:
        raise ValueError("Invalid Wilson inputs")
    if not n:
        return None
    z = NormalDist().inv_cdf(1 - alpha)
    p = successes / n
    return (p + z*z/(2*n) - z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))) / (1 + z*z/n)


def required_support(errors=0, alpha=.05, bound=.995):
    if type(errors) is not int or errors < 0 or not 0 < bound < 1:
        raise ValueError("Invalid support inputs")
    low, high = errors, max(1, errors + 1)
    while wilson_lower(high-errors, high, alpha) < bound:
        high *= 2
    while low + 1 < high:
        mid = (low + high) // 2
        if wilson_lower(mid-errors, mid, alpha) >= bound:
            high = mid
        else:
            low = mid
    return high


def hypergeom_cdf_errors(N, D, n, errors):
    """P(X<=errors), X~Hypergeom(N,D,n), via integer combinatorial weights."""
    if any(type(v) is not int for v in (N, D, n, errors)) or not 0 <= D <= N or not 0 <= n <= N:
        raise ValueError("Invalid hypergeometric inputs")
    lo, hi = max(0, n - (N-D)), min(errors, D, n)
    if hi < lo:
        return 0.
    denominator = math.comb(N, n)
    return sum(math.comb(D, x) * math.comb(N-D, n-x) for x in range(lo, hi+1)) / denominator


def hypergeom_precision_lower(N, n, errors, alpha=.05):
    """Invert lower error-count tail; exact discrete one-sided design bound.

    Accept D when P_D(X<=observed_errors)>alpha. The largest accepted D
    bounds the fixed population's error total. No language-error iid model.
    Applies only to SRSWOR with a fixed, completely known frame/domain.
    """
    if type(errors) is not int or not 0 <= errors <= n or N < 1 or not 0 <= n <= N or not 0 < alpha < 1:
        raise ValueError("Invalid finite-population bound inputs")
    if not n:
        return 0.
    low, high = errors, N - n + errors + 1
    while low + 1 < high:
        middle = (low + high) // 2
        if hypergeom_cdf_errors(N, middle, n, errors) > alpha:
            low = middle
        else:
            high = middle
    return (N-low) / N


def iid_wilson_power(n, true_precision=.999, alpha=.05):
    """Planning illustration only, not the design-based audit's power."""
    if n < 1 or not 0 < true_precision < 1:
        raise ValueError("Invalid power inputs")
    e = 0
    probability = true_precision ** n
    power = 0.
    while e <= n and wilson_lower(n-e, n, alpha) >= .995:
        power += probability
        probability *= (n-e)/(e+1) * (1-true_precision)/true_precision
        e += 1
    return {"n": n, "maximum_passing_errors": e-1, "iid_power": power}


def hypergeom_zero_error_requirement(N, alpha=.05, bound=.995):
    """Planning minimum n for a known finite frame, at zero observed errors.

    Test the smallest error total whose precision would be below bound.
    Evaluate P(X=0) as a product over errors, avoiding enormous factorials.
    """
    if type(N) is not int or N < 0 or not 0 < alpha < 1 or not 0 < bound < 1:
        raise ValueError("Invalid finite frame")
    if not N:
        return None
    D = math.floor((1-bound)*N + 1e-10) + 1

    def rejects(n):
        if n > N-D:
            return True
        logp = sum(math.log1p(-n/(N-i)) for i in range(D))
        # Tail equality rejects. Avoid a spurious extra observation when the
        # log transform rounds e.g. 5/100 infinitesimally above log(.05).
        return logp <= math.log(alpha) or math.isclose(logp, math.log(alpha), rel_tol=0, abs_tol=1e-12)

    lo, hi = 0, N
    while lo + 1 < hi:
        mid = (lo+hi)//2
        if rejects(mid):
            hi = mid
        else:
            lo = mid
    return hi
