# Bài tập lớn Lý thuyết mật mã - Nhóm 7

**Đề tài:** Cài đặt và mô phỏng thuật toán mã dòng MICKEY 2.0 (Mutual Irregular Clocking KEYstream generator).

## Thành viên nhóm

| STT |   MSSV   | Họ và tên                                       |
| :-: | :------: | :------------------------------------------------- |
|  1  | 20233483 | **Phạm Nguyễn Anh Kiệt** (Nhóm trưởng) |
|  2  | 20233373 | Nguyễn Khắc Giang                                |
|  3  | 20233308 | Nguyễn Văn Đạt                                 |
|  4  | 20233473 | Đặng Trung Kiên                                 |
|  5  | 20233468 | Hoàng Tuấn Khôi                                 |
|  6  | 20233451 | Nguyễn Quang Huy                                  |

## Giới thiệu thuật toán

MICKEY 2.0 là một thuật toán mã hóa luồng (stream cipher) được thiết kế bởi Steve Babbage và Matthew Dodd, thuộc dự án eSTREAM. Thuật toán được tối ưu hóa đặc biệt cho các thiết bị phần cứng có tài nguyên hạn chế.

**Đặc điểm kỹ thuật cốt lõi:**

- **Độ dài Khóa (Key):** 80 bit.
- **Độ dài Vector khởi tạo (IV):** Từ 0 đến 80 bit.
- **Kiến trúc:** Dựa trên hai thanh ghi dịch (Shift Registers) hoạt động song song:
  - **R (Linear Feedback Shift Register):** Thanh ghi tuyến tính 100 bit.
  - **S (Non-linear Feedback Shift Register):** Thanh ghi phi tuyến 100 bit.
- **Cơ chế Clocking:** Đặc trưng nhất của MICKEY 2.0 là cơ chế xung nhịp bất quy tắc tương hỗ (Mutual Irregular Clocking). Trạng thái của thanh ghi này sẽ quyết định cách dịch bit (clocking mode) của thanh ghi kia.

---

**Dành cho các thành viên trong nhóm:**
Vui lòng đọc kỹ file [CONTRIBUTING.md](./CONTRIBUTING.md) trước khi tạo nhánh và bắt đầu code.
