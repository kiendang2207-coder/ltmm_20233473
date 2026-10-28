"""Bản MICKEY 2.0 tham chiếu, viết lại độc lập từ docs/mickey_p3.pdf.

Chỉ dùng để kiểm thử chéo với src/: không import gì từ src, hằng số chép
theo từng khối 25 cột của bảng trong PDF (trang 2-3), và thanh ghi được biểu
diễn bằng số nguyên (bit i của số nguyên = r_i / s_i) thay cho list.
Hai cách viết khác nhau mà cho cùng kết quả thì khó có chuyện cùng sai.
"""

# Mục 4.2: các vị trí tap của R
RTAPS = (
    0, 1, 3, 4, 5, 6, 9, 12, 13, 16, 19, 20, 21, 22, 25, 28, 37, 38, 41, 42,
    45, 46, 50, 52, 54, 56, 58, 60, 61, 63, 64, 65, 66, 67, 71, 72, 79, 80, 81, 82,
    87, 88, 89, 90, 91, 92, 94, 95, 96, 97,
)

# Mục 4.3: COMP0, COMP1 chỉ có i = 1..98; FB0, FB1 có i = 0..99
COMP0_SPEC = "000110001011110100101010" "1010110100100000001010101" "0000101001111001010111111" "111010111111010100000011"
COMP1_SPEC = "101100101111001010001101" "0111011110001101011100001" "0001011100011111101011101" "111000100001110001001100"
FB0_SPEC = "1111010111111110010111111" "1111001100000011100100101" "0100101111010101000000000" "1101000110111001110011000"
FB1_SPEC = "1110111000011101001100010" "0110010110001100000110110" "0010001001001011010100101" "0001111011111000000100001"

MASK = (1 << 100) - 1
INNER = MASK & ~1 & ~(1 << 99)  # các vị trí i = 1..98


def _mask(bits, offset=0):
    return sum(1 << (i + offset) for i, b in enumerate(bits) if b == "1")


RTAPS_MASK = sum(1 << t for t in RTAPS)
COMP0 = _mask(COMP0_SPEC, offset=1)
COMP1 = _mask(COMP1_SPEC, offset=1)
FB0 = _mask(FB0_SPEC)
FB1 = _mask(FB1_SPEC)


def bit(x, i):
    return (x >> i) & 1


def clock_r(r, input_bit, control_bit):
    feedback = bit(r, 99) ^ input_bit
    new = (r << 1) & MASK          # r'_i = r_{i-1}, r'_0 = 0
    if feedback:
        new ^= RTAPS_MASK
    if control_bit:
        new ^= r
    return new


def clock_s(s, input_bit, control_bit):
    feedback = bit(s, 99) ^ input_bit
    # ŝ_i = s_{i-1} ^ ((s_i ^ COMP0_i) & (s_{i+1} ^ COMP1_i)) với i = 1..98,
    # ŝ_0 = 0, ŝ_99 = s_98
    hat = ((s << 1) ^ (((s ^ COMP0) & ((s >> 1) ^ COMP1)) & INNER)) & MASK
    if feedback:
        hat ^= FB1 if control_bit else FB0
    return hat


def clock_kg(r, s, mixing, input_bit):
    control_r = bit(s, 34) ^ bit(r, 67)
    control_s = bit(s, 67) ^ bit(r, 33)
    input_r = input_bit ^ bit(s, 50) if mixing else input_bit
    return clock_r(r, input_r, control_r), clock_s(s, input_bit, control_s)


def _bits(data, nbits):
    return [(data[i // 8] >> (7 - i % 8)) & 1 for i in range(nbits)]


def init_phases(key, iv, iv_bits=None):
    """Trả về trạng thái (R, S) sau từng giai đoạn: nạp IV, nạp khóa, preclock."""
    if iv_bits is None:
        iv_bits = len(iv) * 8
    r = s = 0
    for b in _bits(iv, iv_bits):
        r, s = clock_kg(r, s, True, b)
    after_iv = (r, s)
    for b in _bits(key, 80):
        r, s = clock_kg(r, s, True, b)
    after_key = (r, s)
    for _ in range(100):
        r, s = clock_kg(r, s, True, 0)
    return {"iv": after_iv, "key": after_key, "preclock": (r, s)}


def keystream(key, iv, nbytes, iv_bits=None):
    r, s = init_phases(key, iv, iv_bits)["preclock"]
    out = bytearray()
    for _ in range(nbytes):
        byte = 0
        for _ in range(8):
            byte = (byte << 1) | (bit(r, 0) ^ bit(s, 0))
            r, s = clock_kg(r, s, False, 0)
        out.append(byte)
    return bytes(out)


def to_int(bits):
    """list bit (chỉ số 0..99) -> số nguyên, để so với trạng thái của src."""
    return sum(b << i for i, b in enumerate(bits))


def from_int(x):
    return [bit(x, i) for i in range(100)]
