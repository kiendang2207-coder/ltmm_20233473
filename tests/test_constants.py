import pytest

from src import constants as c

TABLES = {"COMP0": c.COMP0, "COMP1": c.COMP1, "FB0": c.FB0, "FB1": c.FB1}


def test_validate_passes():
    c.validate()


@pytest.mark.parametrize("name", TABLES)
def test_table_length_and_bits(name):
    tab = TABLES[name]
    assert len(tab) == 100, f"{name} có {len(tab)} phần tử"
    assert set(tab) <= {0, 1}, f"{name} có giá trị khác 0/1"


def test_rtaps_sorted_unique_in_range():
    assert c.RTAPS == sorted(set(c.RTAPS)), "RTAPS có phần tử trùng lặp hoặc chưa sắp xếp"
    assert all(0 <= t < 100 for t in c.RTAPS), "Có giá trị trong RTAPS nằm ngoài khoảng 0-99"


def test_rtaps_count_matches_spec():
    assert len(c.RTAPS) == 50


def test_rtaps_ends():
    # tap đầu và cuối trong đặc tả là 0 và 97, không có 98, 99
    assert c.RTAPS[0] == 0
    assert c.RTAPS[-1] == 97


# Đọc tay từ bảng trong docs/mickey_p3.pdf (trang 2-3), mỗi dòng là
# i: (COMP0, COMP1, FB0, FB1). Chọn cột đầu của mỗi khối 25 cột và hai đầu bảng.
SPEC_COLUMNS = {
    1: (0, 1, 1, 1),
    25: (1, 0, 1, 0),
    50: (0, 0, 0, 0),
    75: (1, 1, 1, 0),
    98: (1, 0, 0, 0),
}


@pytest.mark.parametrize("i", SPEC_COLUMNS)
def test_columns_match_spec(i):
    got = (c.COMP0[i], c.COMP1[i], c.FB0[i], c.FB1[i])
    assert got == SPEC_COLUMNS[i], f"cột i={i} lệch đặc tả"


def test_fb_ends_match_spec():
    # FB0, FB1 có đủ i = 0..99 trong đặc tả
    assert (c.FB0[0], c.FB1[0]) == (1, 1)
    assert (c.FB0[99], c.FB1[99]) == (0, 1)
