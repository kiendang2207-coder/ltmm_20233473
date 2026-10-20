"""Hằng số MICKEY 2.0 - chép CHÍNH XÁC từ đặc tả eSTREAM."""

# Các vị trí của R có phản hồi (danh sách chỉ số, từ đặc tả)
RTAPS = []

# 100 phần tử mỗi bảng, giá trị 0 hoặc 1, theo đúng thứ tự i = 0..99
COMP0 = []
COMP1 = []
FB0 = []
FB1 = []


def validate():
    """Gọi trước khi dùng để bắt lỗi chép hằng."""
    for name, tab in (("COMP0", COMP0), ("COMP1", COMP1), ("FB0", FB0), ("FB1", FB1)):
        assert len(tab) == 100, f"{name} phải có 100 phần tử, hiện có {len(tab)}"
        assert all(b in (0, 1) for b in tab), f"{name} chỉ chứa 0 hoặc 1"
    assert len(RTAPS) > 0, "RTAPS đang trống"
    assert len(set(RTAPS)) == len(RTAPS), "RTAPS có phần tử trùng"
    assert all(0 <= t < 100 for t in RTAPS), "RTAPS phải nằm trong 0..99"