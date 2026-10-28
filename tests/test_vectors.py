"""Test vector cho MICKEY 2.0 - Đặng Trung Kiên (20233473).

Bảng vector và giải thích: docs/test_vectors.md
"""
import pytest

from src.mickey2 import crypt, keystream


def h(s):
    """Chuỗi hex (có thể có dấu cách) -> bytes."""
    return bytes.fromhex(s.replace(" ", ""))


# Vector trong bộ test vector eSTREAM của tác giả (key, iv, keystream đầu)
KAT = [
    ("12 34 56 78 9a bc de f0 12 34", "21 43 65 87",
     "98 21 e1 0c 5e d2 8d 32 bb c3"),
    ("f1 1a 56 27 ce 43 b6 1f 89 12", "9c 53 2f 8a c3 ea 4b 2e a0 f5",
     "21 a0 43 66 19 cb 9f 3f 6f 1f b3 03 f5 6a 09 a9"),
]


@pytest.mark.parametrize("key, iv, expected", KAT)
def test_kat(key, iv, expected):
    want = h(expected)
    assert keystream(h(key), h(iv), len(want)) == want


# Trường hợp biên (key, iv, iv_bits, 16 byte keystream đầu)
EDGE = [
    ("00000000000000000000", "", None, "fdc3e90a235253dd99c7d5a254cb5424"),
    ("ffffffffffffffffffff", "", None, "c6230ad0f78e0555623b60e700a64bd4"),
    ("80000000000000000000", "", None, "dc5c36e2d2887710ccc9182553874798"),
    ("00000000000000000000", "00000000000000000000", None, "bc5de7db0b931fc99bd5f021fda49657"),
    ("00000000000000000000", "80", 1, "b8b86dc5a510ee219992304aa70e8f31"),
    ("0123456789abcdef0123", "fedcba98", 31, "1d56ffd2db4227c32d31a93c61facb04"),
]


@pytest.mark.parametrize("key, iv, iv_bits, expected", EDGE)
def test_edge_vectors(key, iv, iv_bits, expected):
    assert keystream(h(key), h(iv), 16, iv_bits) == h(expected)


def test_decrypt_gives_back_plaintext():
    key, iv = h("0123456789abcdef0123"), h("fedcba98")
    pt = "Nhom 7 - MICKEY 2.0".encode()
    ct = crypt(key, iv, pt)
    assert ct != pt
    assert crypt(key, iv, ct) == pt


def test_change_one_bit_changes_keystream():
    key, iv = h("0123456789abcdef0123"), h("fedcba98")
    base = keystream(key, iv, 16)
    assert keystream(h("0123456789abcdef0122"), iv, 16) != base  # đổi 1 bit key
    assert keystream(key, h("fedcba99"), 16) != base             # đổi 1 bit IV


def test_iv_bits_zero_same_as_empty_iv():
    key = h("0123456789abcdef0123")
    assert keystream(key, b"\xff", 16, 0) == keystream(key, b"", 16)


@pytest.mark.parametrize("key_len", (9, 11))
def test_wrong_key_length_is_rejected(key_len):
    with pytest.raises(AssertionError):
        keystream(bytes(key_len), b"", 1)


def test_iv_longer_than_80_bits_is_rejected():
    with pytest.raises(AssertionError):
        keystream(bytes(10), bytes(11), 1)
