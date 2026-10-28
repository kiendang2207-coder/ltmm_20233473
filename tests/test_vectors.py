"""Test vector cho MICKEY 2.0 (Đặng Trung Kiên - 20233473).

Gồm 6 nhóm:
  A. KAT: vector có đáp án biết trước, không do code của nhóm sinh ra.
  B. Vector biên: đáp án đã được hai bản cài đặt độc lập cùng xác nhận.
  C. Kiểm thử chéo ngẫu nhiên với tests/reference_mickey2.py, đủ IV 0..80 bit.
  D. Vector trạng thái: từng nhịp clock_r/clock_s/clock_kg và trạng thái sau init.
  E. Tính chất: giải mã, độ nhạy với key/IV, hiệu ứng thác, quy ước bit.
  F. Đầu vào sai phải bị từ chối.
Đáp án đầy đủ để đưa vào báo cáo: docs/test_vectors.md.
"""
import random

import pytest

from src.mickey2 import bytes_to_bits, clock_kg, crypt, init_state, keystream
from src.registers import clock_r, clock_s
from tests import reference_mickey2 as ref

SEED = 20233473  # MSSV, để lần nào chạy cũng ra cùng bộ số ngẫu nhiên


def h(s):
    return bytes.fromhex(s.replace(" ", ""))


# ---------------------------------------------------------------- A. KAT
# Bộ vector đi kèm gói nộp MICKEY 2.0 của tác giả lên eSTREAM (không có trong
# mickey_p3.pdf). TODO: đối chiếu lại với file gốc khi tải được gói eSTREAM;
# vector thứ ba (key 3b80fc8c71d5597839bb, IV rỗng) để lại tới lúc đó.
KAT = [
    # (key, iv, đầu keystream mong đợi)
    ("12 34 56 78 9a bc de f0 12 34", "21 43 65 87",
     "98 21 e1 0c 5e d2 8d 32 bb c3"),
    ("f1 1a 56 27 ce 43 b6 1f 89 12", "9c 53 2f 8a c3 ea 4b 2e a0 f5",
     "21 a0 43 66 19 cb 9f 3f 6f 1f b3 03 f5 6a 09 a9"),
]


@pytest.mark.parametrize("key, iv, expected", KAT)
def test_kat(key, iv, expected):
    want = h(expected)
    assert keystream(h(key), h(iv), len(want)) == want


# ---------------------------------------------------------------- B. biên
# (tên, key, iv, iv_bits, 16 byte keystream đầu)
EDGE = [
    ("key 0, IV rỗng", "00000000000000000000", "", None,
     "fdc3e90a235253dd99c7d5a254cb5424"),
    ("key FF, IV rỗng", "ffffffffffffffffffff", "", None,
     "c6230ad0f78e0555623b60e700a64bd4"),
    ("key chỉ bit k0 = 1", "80000000000000000000", "", None,
     "dc5c36e2d2887710ccc9182553874798"),
    ("key 0, IV 0 đủ 80 bit", "00000000000000000000", "00000000000000000000", None,
     "bc5de7db0b931fc99bd5f021fda49657"),
    ("key 0, IV 1 bit = 1", "00000000000000000000", "80", 1,
     "b8b86dc5a510ee219992304aa70e8f31"),
    ("IV 32 bit", "0123456789abcdef0123", "fedcba98", None,
     "15e77f03e60059be39e79ace4663954a"),
    ("IV 31 bit (lẻ)", "0123456789abcdef0123", "fedcba98", 31,
     "1d56ffd2db4227c32d31a93c61facb04"),
    ("IV 77 bit (lẻ)", "0123456789abcdef0123", "fedcba9876543210fedc", 77,
     "a311de5c80ce681c37626a68a8a4dab2"),
]


@pytest.mark.parametrize("name, key, iv, iv_bits, expected", EDGE, ids=[e[0] for e in EDGE])
def test_edge_vectors(name, key, iv, iv_bits, expected):
    got = keystream(h(key), h(iv), 16, iv_bits)
    assert got == h(expected), f"{name}: {got.hex()}"
    assert got == ref.keystream(h(key), h(iv), 16, iv_bits)


# ---------------------------------------------------------------- C. chéo
def _random_case(rng, iv_bits):
    key = bytes(rng.randrange(256) for _ in range(10))
    iv = bytes(rng.randrange(256) for _ in range((iv_bits + 7) // 8))
    return key, iv


@pytest.mark.parametrize("iv_bits", range(81))
def test_cross_check_every_iv_length(iv_bits):
    key, iv = _random_case(random.Random(SEED + iv_bits), iv_bits)
    assert keystream(key, iv, 32, iv_bits) == ref.keystream(key, iv, 32, iv_bits)


def test_cross_check_long_keystream():
    # 1000 byte = 8000 nhịp, để bắt lỗi chỉ lộ ra sau nhiều nhịp
    key, iv = h("0123456789abcdef0123"), h("fedcba9876543210fedc")
    assert keystream(key, iv, 1000) == ref.keystream(key, iv, 1000)


# ---------------------------------------------------------------- D. trạng thái
def _random_state(rng):
    return [rng.randrange(2) for _ in range(100)]


@pytest.mark.parametrize("inp", (0, 1))
@pytest.mark.parametrize("ctrl", (0, 1))
def test_clock_r_matches_reference(inp, ctrl):
    rng = random.Random(SEED)
    for _ in range(50):
        R = _random_state(rng)
        assert clock_r(R, inp, ctrl) == ref.from_int(ref.clock_r(ref.to_int(R), inp, ctrl))


@pytest.mark.parametrize("inp", (0, 1))
@pytest.mark.parametrize("ctrl", (0, 1))
def test_clock_s_matches_reference(inp, ctrl):
    rng = random.Random(SEED)
    for _ in range(50):
        S = _random_state(rng)
        assert clock_s(S, inp, ctrl) == ref.from_int(ref.clock_s(ref.to_int(S), inp, ctrl))


def test_clock_s_boundary_states():
    # thanh ghi toàn 0 / toàn 1 / chỉ một bit ở các vị trí đặc biệt
    states = [[0] * 100, [1] * 100]
    for pos in (0, 1, 50, 98, 99):
        st = [0] * 100
        st[pos] = 1
        states.append(st)
    for S in states:
        for inp in (0, 1):
            for ctrl in (0, 1):
                want = ref.from_int(ref.clock_s(ref.to_int(S), inp, ctrl))
                assert clock_s(S, inp, ctrl) == want


@pytest.mark.parametrize("mixing", (False, True))
@pytest.mark.parametrize("inp", (0, 1))
def test_clock_kg_matches_reference(mixing, inp):
    rng = random.Random(SEED)
    for _ in range(50):
        R, S = _random_state(rng), _random_state(rng)
        r2, s2 = ref.clock_kg(ref.to_int(R), ref.to_int(S), mixing, inp)
        assert clock_kg(R, S, mixing, inp) == (ref.from_int(r2), ref.from_int(s2))


def test_state_after_init_matches_reference():
    key, iv = h("12 34 56 78 9a bc de f0 12 34"), h("21 43 65 87")
    R, S = init_state(key, iv)
    r, s = ref.init_phases(key, iv)["preclock"]
    assert (ref.to_int(R), ref.to_int(S)) == (r, s)


def test_state_after_init_all_zero_input():
    # key = 0, IV rỗng: R vẫn phải thoát khỏi trạng thái toàn 0 (mục 8.4)
    R, S = init_state(bytes(10), b"")
    assert any(R) and any(S)


# ---------------------------------------------------------------- E. tính chất
def test_bit_order_msb_first():
    assert bytes_to_bits(b"\x80", 8) == [1, 0, 0, 0, 0, 0, 0, 0]
    assert bytes_to_bits(b"\x01", 8) == [0, 0, 0, 0, 0, 0, 0, 1]
    assert bytes_to_bits(b"\xa0", 3) == [1, 0, 1]


def test_decrypt_recovers_plaintext():
    key, iv = h("0123456789abcdef0123"), h("fedcba98")
    pt = "Nhóm 7 - Lý thuyết mật mã - MICKEY 2.0".encode()
    ct = crypt(key, iv, pt)
    assert ct != pt
    assert crypt(key, iv, ct) == pt


def test_keystream_is_deterministic_and_prefix_stable():
    key, iv = h("0123456789abcdef0123"), h("fedcba98")
    assert keystream(key, iv, 64) == keystream(key, iv, 64)
    assert keystream(key, iv, 64)[:16] == keystream(key, iv, 16)


def test_iv_bits_zero_equals_empty_iv():
    key = h("0123456789abcdef0123")
    assert keystream(key, b"\xff", 16, 0) == keystream(key, b"", 16)


def test_iv_bits_ignores_unused_low_bits():
    key = h("0123456789abcdef0123")
    assert keystream(key, b"\xff", 16, 4) == keystream(key, b"\xf0", 16, 4)


def test_iv_of_different_length_gives_different_keystream():
    # IV 0x00 dài 8 bit khác IV rỗng: độ dài IV cũng là một phần của đầu vào
    key = h("0123456789abcdef0123")
    assert keystream(key, b"\x00", 16) != keystream(key, b"", 16)


def _flip(data, i):
    out = bytearray(data)
    out[i // 8] ^= 0x80 >> (i % 8)
    return bytes(out)


def _hamming(a, b):
    return sum(bin(x ^ y).count("1") for x, y in zip(a, b))


def test_every_key_bit_matters():
    key, iv = h("0123456789abcdef0123"), h("fedcba9876543210fedc")
    base = keystream(key, iv, 32)
    distances = [_hamming(base, keystream(_flip(key, i), iv, 32)) for i in range(80)]
    assert min(distances) > 0
    # 256 bit đầu ra, lý tưởng đổi một nửa; trung bình 80 lần phải sát 128
    assert 112 <= sum(distances) / 80 <= 144


def test_every_iv_bit_matters():
    key, iv = h("0123456789abcdef0123"), h("fedcba9876543210fedc")
    base = keystream(key, iv, 32)
    distances = [_hamming(base, keystream(key, _flip(iv, i), 32)) for i in range(80)]
    assert min(distances) > 0
    assert 112 <= sum(distances) / 80 <= 144


def test_keystream_bit_balance():
    # 8000 bit keystream: số bit 1 phải nằm trong khoảng ±4 độ lệch chuẩn quanh 4000
    ks = keystream(h("0123456789abcdef0123"), h("fedcba98"), 1000)
    ones = sum(bin(b).count("1") for b in ks)
    assert abs(ones - 4000) < 4 * 45


# ---------------------------------------------------------------- F. đầu vào sai
# Code hiện kiểm tra bằng assert; chấp nhận cả ValueError nếu sau này nhóm đổi.
BAD_INPUT = (AssertionError, ValueError)


@pytest.mark.parametrize("key_len", (0, 9, 11, 16))
def test_reject_wrong_key_length(key_len):
    with pytest.raises(BAD_INPUT):
        keystream(bytes(key_len), b"", 1)


def test_reject_iv_longer_than_80_bits():
    with pytest.raises(BAD_INPUT):
        keystream(bytes(10), bytes(11), 1)


def test_reject_iv_bits_more_than_available():
    with pytest.raises(BAD_INPUT):
        keystream(bytes(10), bytes(2), 1, iv_bits=17)
