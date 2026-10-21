from src import constants as c


def test_validate_passes():
    # Gọi hàm validate (nếu bạn đã định nghĩa trong constants.py)
    if hasattr(c, 'validate'):
        c.validate()


def test_table_lengths():
    for t in (c.COMP0, c.COMP1, c.FB0, c.FB1):
        assert len(t) == 100, f"Mảng bị thiếu hoặc thừa phần tử, hiện đang có {len(t)} phần tử"


def test_rtaps_sorted_unique_in_range():
    assert c.RTAPS == sorted(set(c.RTAPS)), "RTAPS có phần tử trùng lặp hoặc chưa sắp xếp"
    assert all(0 <= t < 100 for t in c.RTAPS), "Có giá trị trong RTAPS nằm ngoài khoảng 0-99"


def test_rtaps_count_matches_spec():
    assert len(c.RTAPS) == 50
