# Test vector MICKEY 2.0

Người làm: Đặng Trung Kiên (20233473). Code kiểm thử nằm ở [`tests/test_vectors.py`](../tests/test_vectors.py).

Cách chạy:

```bash
python -m pip install pytest
python -m pytest tests/test_vectors.py -v
```

Quy ước: key và IV viết dạng hex. Mỗi byte được nạp bit cao trước, ví dụ byte `0x80` nghĩa là bit đầu tiên `k0 = 1`.
Keystream cũng được ghép thành byte theo thứ tự bit cao trước.

## 1. Vector chính thức

File `mickey_p3.pdf` không có test vector, nên mình lấy theo bộ test vector đi kèm bản nộp eSTREAM của tác giả.

| # | Key | IV | Keystream mong đợi | Kết quả |
|:-:|---|---|---|:-:|
| 1 | `12 34 56 78 9a bc de f0 12 34` | `21 43 65 87` | `98 21 e1 0c 5e d2 8d 32 bb c3` | Đạt |
| 2 | `f1 1a 56 27 ce 43 b6 1f 89 12` | `9c 53 2f 8a c3 ea 4b 2e a0 f5` | `21 a0 43 66 19 cb 9f 3f 6f 1f b3 03 f5 6a 09 a9` | Đạt |

## 2. Trường hợp biên

Các giá trị dưới đây do chương trình của nhóm sinh ra. Mình đã kiểm tra lại bằng một bản tự viết riêng theo đặc tả và thấy kết quả giống nhau.
Bảng này dùng để phát hiện khi ai đó sửa code làm keystream bị thay đổi.

| Trường hợp | Key | IV | Số bit IV | 16 byte keystream đầu |
|---|---|---|:-:|---|
| Key toàn 0, không IV | `00000000000000000000` | (rỗng) | 0 | `fdc3e90a235253dd99c7d5a254cb5424` |
| Key toàn 1, không IV | `ffffffffffffffffffff` | (rỗng) | 0 | `c6230ad0f78e0555623b60e700a64bd4` |
| Chỉ bit đầu của key = 1 | `80000000000000000000` | (rỗng) | 0 | `dc5c36e2d2887710ccc9182553874798` |
| IV toàn 0 dài tối đa | `00000000000000000000` | `00000000000000000000` | 80 | `bc5de7db0b931fc99bd5f021fda49657` |
| IV chỉ 1 bit | `00000000000000000000` | `80` | 1 | `b8b86dc5a510ee219992304aa70e8f31` |
| Số bit IV lẻ | `0123456789abcdef0123` | `fedcba98` | 31 | `1d56ffd2db4227c32d31a93c61facb04` |

## 3. Kiểm tra khác

| Kiểm tra | Kết quả |
|---|:-:|
| Mã hóa rồi giải mã ra lại đúng bản rõ | Đạt |
| Đổi 1 bit key hoặc 1 bit IV thì keystream thay đổi | Đạt |
| `iv_bits = 0` cho kết quả giống không có IV | Đạt |
| Key khác 10 byte hoặc IV dài hơn 80 bit thì báo lỗi | Đạt |

## Ghi chú

- Khi tải được bộ test vector gốc trên trang eSTREAM, mình sẽ đối chiếu lại mục 1.
- `docs/README.md` đang ghi là PDF có test vector, nhưng thực tế không có. Mình sẽ báo lại để nhóm sửa.
