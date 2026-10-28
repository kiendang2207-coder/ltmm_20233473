
import unittest

from .registers import clock_r
from .constants import RTAPS


def reference_clock_r(R, inp, ctrl):
    """
    Tính trạng thái tham chiếu theo công thức CLOCK_R.
    Dùng để so sánh với hàm clock_r() cần kiểm thử.
    """
    old = R.copy()

    # 1. Bit hồi tiếp từ trạng thái cũ.
    fb = old[99] ^ inp

    # 2. Dịch thanh ghi.
    expected = [0] + old[:99]

    # 3. XOR hồi tiếp tại các vị trí RTAPS.
    for t in RTAPS:
        expected[t] ^= fb

    # 4. Nếu ctrl = 1, XOR trạng thái cũ vào trạng thái mới.
    if ctrl == 1:
        expected = [
            expected[i] ^ old[i]
            for i in range(100)
        ]

    return expected


class TestClockR(unittest.TestCase):

    def test_all_zero_register(self):
        """TC01: Thanh ghi toàn 0, đầu vào và điều khiển bằng 0."""
        R = [0] * 100

        result = clock_r(R, 0, 0)

        self.assertEqual(result, [0] * 100)

    def test_all_one_register(self):
        """TC02: Kiểm tra thanh ghi toàn 1."""
        R = [1] * 100

        for inp in (0, 1):
            for ctrl in (0, 1):
                with self.subTest(inp=inp, ctrl=ctrl):
                    result = clock_r(R, inp, ctrl)
                    expected = reference_clock_r(R, inp, ctrl)
                    self.assertEqual(result, expected)

    def test_single_one_at_boundary(self):
        """TC03: Kiểm tra trạng thái chỉ có một bit bằng 1."""
        for position in (0, 33, 67, 99):
            R = [0] * 100
            R[position] = 1

            for inp in (0, 1):
                for ctrl in (0, 1):
                    with self.subTest(
                        position=position,
                        inp=inp,
                        ctrl=ctrl
                    ):
                        result = clock_r(R, inp, ctrl)
                        expected = reference_clock_r(
                            R, inp, ctrl
                        )
                        self.assertEqual(result, expected)

    def test_all_control_combinations(self):
        """TC04: Kiểm tra đủ bốn tổ hợp inp và ctrl."""
        R = [(i * 7 + 3) % 2 for i in range(100)]

        for inp in (0, 1):
            for ctrl in (0, 1):
                with self.subTest(inp=inp, ctrl=ctrl):
                    result = clock_r(R, inp, ctrl)
                    expected = reference_clock_r(R, inp, ctrl)
                    self.assertEqual(result, expected)

    def test_output_is_100_binary_bits(self):
        """TC05: Đầu ra phải có 100 bit nhị phân."""
        R = [(i + 1) % 2 for i in range(100)]

        result = clock_r(R, 1, 1)

        self.assertEqual(len(result), 100)
        self.assertTrue(all(bit in (0, 1) for bit in result))

    def test_input_state_unchanged(self):
        """TC06: Hàm không được sửa trạng thái đầu vào."""
        R = [(i * 3) % 2 for i in range(100)]
        original = R.copy()

        clock_r(R, 1, 1)

        self.assertEqual(R, original)

    def test_taps_are_valid(self):
        """TC07: Danh sách RTAPS không trùng và nằm trong 0..99."""
        self.assertEqual(len(RTAPS), len(set(RTAPS)))
        self.assertTrue(all(0 <= t < 100 for t in RTAPS))


if __name__ == "__main__":
    unittest.main(verbosity=2)
