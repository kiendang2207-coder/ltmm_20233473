from .constants import validate
from .registers import clock_r, clock_s


def clock_kg(R, S, mixing, inp):
    """Một nhịp chung của bộ sinh khóa."""
    ctrl_r = S[34] ^ R[67]
    ctrl_s = S[67] ^ R[33]
    inp_r = inp ^ S[50] if mixing else inp
    return clock_r(R, inp_r, ctrl_r), clock_s(S, inp, ctrl_s)


def bytes_to_bits(data: bytes, nbits: int):
    """MSB trước trong từng byte."""
    return [(data[i // 8] >> (7 - i % 8)) & 1 for i in range(nbits)]


def init_state(key: bytes, iv: bytes, iv_bits=None):
    """Khởi tạo: nạp IV, nạp khóa, 100 nhịp preclock."""
    validate()
    assert len(key) == 10, "Khóa phải 80 bit (10 byte)"
    if iv_bits is None:
        iv_bits = len(iv) * 8
    assert 0 <= iv_bits <= 80 and iv_bits <= len(iv) * 8

    R, S = [0] * 100, [0] * 100
    for b in bytes_to_bits(iv, iv_bits):
        R, S = clock_kg(R, S, True, b)
    for b in bytes_to_bits(key, 80):
        R, S = clock_kg(R, S, True, b)
    for _ in range(100):
        R, S = clock_kg(R, S, True, 0)
    return R, S


def keystream(key: bytes, iv: bytes, nbytes: int, iv_bits=None) -> bytes:
    """Sinh nbytes byte keystream."""
    R, S = init_state(key, iv, iv_bits)
    out = bytearray()
    for _ in range(nbytes):
        byte = 0
        for _ in range(8):
            byte = (byte << 1) | (R[0] ^ S[0])
            R, S = clock_kg(R, S, False, 0)
        out.append(byte)
    return bytes(out)


def crypt(key: bytes, iv: bytes, data: bytes, iv_bits=None) -> bytes:
    """Mã hóa và giải mã là cùng một phép XOR với keystream."""
    ks = keystream(key, iv, len(data), iv_bits)
    return bytes(a ^ b for a, b in zip(data, ks))
