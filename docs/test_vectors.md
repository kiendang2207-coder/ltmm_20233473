# Test vector MICKEY 2.0

Người làm: Đặng Trung Kiên (20233473). Code kiểm thử: [`tests/test_vectors.py`](../tests/test_vectors.py),
bản cài đặt tham chiếu: [`tests/reference_mickey2.py`](../tests/reference_mickey2.py).

Chạy kiểm thử:

```bash
python -m pip install pytest
python -m pytest -v
```

## Quy ước

- Khóa và IV ghi dạng hex. Mỗi byte được nạp **bit cao nhất trước**: byte đầu `0x80` nghĩa là `k0 = 1`, các bit sau bằng 0.
- Bit keystream `z0 z1 …` được ghép thành byte theo thứ tự bit cao trước: `z0` là bit cao nhất của byte keystream đầu tiên.
- Cột `iv_bits` để trống nghĩa là dùng toàn bộ số bit của IV (`8 × số byte`).

## A. Vector có đáp án biết trước (KAT)

File `mickey_p3.pdf` **không có** test vector. Hai vector dưới đây lấy từ bộ vector đi kèm gói nộp MICKEY 2.0 của tác giả lên eSTREAM.
Khi trang eSTREAM truy cập lại được, cần tải file gốc để đối chiếu và bổ sung vector thứ ba.

| # | Key | IV | Keystream mong đợi | Kết quả |
|:-:|---|---|---|:-:|
| 1 | `12 34 56 78 9a bc de f0 12 34` | `21 43 65 87` | `98 21 e1 0c 5e d2 8d 32 bb c3` | Đạt |
| 2 | `f1 1a 56 27 ce 43 b6 1f 89 12` | `9c 53 2f 8a c3 ea 4b 2e a0 f5` | `21 a0 43 66 19 cb 9f 3f 6f 1f b3 03 f5 6a 09 a9` | Đạt |

## B. Vector biên (16 byte keystream đầu)

Mỗi giá trị đều được `src/mickey2.py` và bản tham chiếu viết độc lập cho ra giống nhau.

| Trường hợp | Key | IV | iv_bits | Keystream |
|---|---|---|:-:|---|
| Key 0, IV rỗng | `00000000000000000000` | (rỗng) | | `fdc3e90a235253dd99c7d5a254cb5424` |
| Key FF, IV rỗng | `ffffffffffffffffffff` | (rỗng) | | `c6230ad0f78e0555623b60e700a64bd4` |
| Chỉ bit k0 = 1 | `80000000000000000000` | (rỗng) | | `dc5c36e2d2887710ccc9182553874798` |
| Key 0, IV 0 đủ 80 bit | `00000000000000000000` | `00000000000000000000` | | `bc5de7db0b931fc99bd5f021fda49657` |
| IV 1 bit = 1 | `00000000000000000000` | `80` | 1 | `b8b86dc5a510ee219992304aa70e8f31` |
| IV 32 bit | `0123456789abcdef0123` | `fedcba98` | | `15e77f03e60059be39e79ace4663954a` |
| IV 31 bit | `0123456789abcdef0123` | `fedcba98` | 31 | `1d56ffd2db4227c32d31a93c61facb04` |
| IV 77 bit | `0123456789abcdef0123` | `fedcba9876543210fedc` | 77 | `a311de5c80ce681c37626a68a8a4dab2` |

## C. Kiểm thử chéo

- Cho mỗi độ dài IV từ 0 đến 80 bit (81 trường hợp), sinh ngẫu nhiên một cặp key/IV với seed `20233473` và so 32 byte keystream của hai bản cài đặt.
- So thêm 1000 byte keystream (8000 nhịp) cho một cặp key/IV cố định.
- So từng nhịp `clock_r`, `clock_s`, `clock_kg` trên trạng thái ngẫu nhiên, với đủ mọi tổ hợp `input_bit`, `control_bit` và `mixing`.
- So trạng thái R, S sau giai đoạn khởi tạo.

Bản tham chiếu khác `src/` ở 3 điểm, nên hai bản khó có chuyện cùng sai:
1. Thanh ghi biểu diễn bằng số nguyên thay cho list.
2. Hằng số chép lại theo từng khối 25 cột của bảng trong PDF.
3. Không import gì từ `src/`.

## D. Tính chất

| Kiểm tra | Kết quả |
|---|---|
| Giải mã bản mã ra đúng bản rõ | Đạt |
| Keystream sinh lại cho kết quả như cũ; 16 byte đầu khớp với khi sinh 64 byte | Đạt |
| `iv_bits = 0` cho kết quả như IV rỗng | Đạt |
| `iv_bits = 4` bỏ qua 4 bit thấp của byte IV | Đạt |
| IV `00` (8 bit) cho keystream khác IV rỗng | Đạt |
| Lật lần lượt từng bit trong 80 bit khóa: trung bình số bit đổi trên 256 bit đầu ra nằm trong khoảng 112–144 | Đạt |
| Lật lần lượt từng bit trong 80 bit IV: điều kiện như trên | Đạt |
| Trong 8000 bit keystream, số bit 1 lệch khỏi 4000 ít hơn 4 độ lệch chuẩn | Đạt |
| Khóa không đủ 10 byte, IV trên 80 bit, `iv_bits` lớn hơn số bit có sẵn đều bị từ chối | Đạt |

## E. Bộ test có bắt được lỗi không (kiểm thử đột biến)

Mình cố tình cài từng lỗi vào một bản sao của `src/`, rồi chạy `tests/test_vectors.py` (122 test):

| Lỗi cài vào | Số test báo lỗi |
|---|:-:|
| Bit điều khiển R lấy `R66` thay vì `R67` | 97 |
| Bỏ phép XOR với `S50` khi `mixing` | 96 |
| Preclock 99 nhịp thay vì 100 | 93 |
| Nạp bit theo thứ tự thấp trước | 92 |
| `ŝ99 = s99` thay vì `s98` | 102 |
| Đảo vai trò FB0 và FB1 | 102 |
| Lật 1 bit trong bảng FB0 | 100 |
| Đầu ra lấy `r0 ⊕ s1` thay vì `r0 ⊕ s0` | 92 |

## Việc còn lại

- Tải bộ vector chính thức trong gói eSTREAM để đối chiếu lại nhóm A và bổ sung vector thứ ba.
- Báo lại với nhóm: `docs/README.md` đang ghi là PDF có test vector, điều này không đúng.
