# Tài liệu tham khảo thuật toán MICKEY 2.0 (Reference Documents)

Thư mục này lưu trữ các tài liệu đặc tả chính thức của thuật toán mã dòng MICKEY 2.0 thuộc dự án eSTREAM:

1. **`mickey_p3.pdf`**:
   * **Tên đầy đủ:** *The Stream Cipher MICKEY 2.0*
   * **Tác giả:** Steve Babbage & Matthew Dodd
   * **Nội dung:** Đặc tả kỹ thuật đầy đủ của thuật toán MICKEY 2.0 (khóa 80-bit, IV 0-80 bit), bao gồm:
     * Cấu trúc hai thanh ghi $R$ (tuyến tính) và $S$ (phi tuyến) 100 bit.
     * Bảng hằng số phản hồi: `RTAPS` (50 vị trí), `COMP0`, `COMP1`, `FB0`, `FB1` (mỗi bảng 100 bit).
     * Cơ chế xung nhịp bất quy tắc tương hỗ (`CLOCK_KG`, `CLOCK_R`, `CLOCK_S`).
     * Quy trình nạp Key/IV và sinh Keystream.
     * Các test vector mẫu để đối chiếu.

2. **`mickey128_p3.pdf`**:
   * **Tên đầy đủ:** *The Stream Cipher MICKEY-128 2.0*
   * **Tác giả:** Steve Babbage & Matthew Dodd
   * **Nội dung:** Đặc tả biến thể MICKEY-128 hỗ trợ khóa bảo mật 128 bit và IV lên đến 128 bit.
