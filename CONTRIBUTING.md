# Quy ước làm việc nhóm (Workflow Guidelines)

Để đảm bảo dự án hoạt động trơn tru, hạn chế conflict và ghi nhận công bằng điểm số cho từng thành viên, toàn nhóm thống nhất tuân thủ các quy tắc sau:

## Quy tắc Git & Branching
1. **Không commit thẳng lên nhánh `main`:** Nhánh `main` đã được khóa, mọi thay đổi đều phải thông qua Pull Request (PR).
2. **Quy tắc đặt tên nhánh:** Mỗi công việc làm trên một nhánh riêng biệt.
   - Tính năng mới: `feature/<tên-việc>` (VD: `feature/constants-fill`)
   - Sửa lỗi: `fix/<tên-lỗi>` (VD: `fix/clock-s-boundary`)
3. **Luôn đồng bộ trước khi tạo nhánh:** 
   ```bash
   git checkout main
   git pull
   git checkout -b feature/<tên-việc>
   ```
4. **Vòng đời nhánh ngắn:** Làm xong tính năng -> Mở PR -> Được duyệt -> Merge -> **Xóa nhánh ngay lập tức**.

## Quy tắc Commit

Sử dụng chuẩn Conventional Commits để lịch sử rõ ràng:

* `feat(...)`: Thêm tính năng/hàm mới.
* `fix(...)`: Sửa lỗi logic hoặc bug.
* `test(...)`: Thêm hoặc sửa Unit Test.
* `docs(...)`: Cập nhật tài liệu, README, docstring.
* *Ví dụ:* `feat(constants): fill RTAPS, COMP and FB tables from eSTREAM spec`

## Quy tắc Phối hợp & Code Review

* **Giao tiếp:** Không tự ý chỉnh sửa file đang thuộc quyền phụ trách của người khác khi chưa báo trước.
* **Review chéo:** Bắt buộc phải có **ít nhất 1 người khác** trong nhóm vào xem code và Approve thì mới được merge. **Tuyệt đối không tự merge Pull Request của chính mình.**
