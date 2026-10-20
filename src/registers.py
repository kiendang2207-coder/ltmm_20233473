from .constants import RTAPS, COMP0, COMP1, FB0, FB1


def clock_r(R, inp, ctrl):
    """Xung nhịp thanh ghi R (LFSR 100 bit)."""
    fb = R[99] ^ inp
    new = [0] + R[:99]              # R'_i = R_{i-1}, R'_0 = 0
    for t in RTAPS:
        new[t] ^= fb
    if ctrl:
        new = [new[i] ^ R[i] for i in range(100)]
    return new


def clock_s(S, inp, ctrl):
    """Xung nhịp thanh ghi S (phi tuyến 100 bit)."""
    new = [0] * 100
    for i in range(1, 99):
        new[i] = S[i - 1] ^ ((S[i] ^ COMP0[i]) & (S[i + 1] ^ COMP1[i]))
    new[99] = S[98]
    fb = S[99] ^ inp
    table = FB1 if ctrl else FB0
    return [new[i] ^ (table[i] & fb) for i in range(100)]