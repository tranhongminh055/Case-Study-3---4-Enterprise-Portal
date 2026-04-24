## Mục đích
Tài liệu này mô tả ánh xạ dữ liệu giữa:
- API (payload JSON) được frontend gửi/nhận
- Backend SQLAlchemy models / cột trong SQL Server (nguồn truth)
- Bảng MySQL dùng cho payroll/replica (`employees_payroll`, `salaries`, ...)

Mục tiêu: giúp dev hiểu rõ tên trường, chuyển đổi `first_name`/`last_name` <-> `full_name`, và các khác biệt giữa SQL Server và MySQL.

## Tổng quan thực thể chính
- Employee (nhân viên)
- Department (phòng ban)
- Position (vị trí)
- Payroll (lương/attendance — lưu ở MySQL)

---

## Employee — ánh xạ chi tiết

- API payload (frontend) fields:
  - `first_name` (string)
  - `last_name` (string)
  - `email` (string, unique)
  - `phone` (string | null)
  - `hire_date` (yyyy-mm-dd)
  - `date_of_birth` (yyyy-mm-dd) — optional in payloads
  - `department_id` (int | null)
  - `position_id` (int | null)
  - `status` (string) — `active` | `inactive` | `terminated`

- Frontend form names: (see [frontend/src/components/EmployeeForm.jsx](frontend/src/components/EmployeeForm.jsx)) — same as API keys above.

- SQLAlchemy model (`backend/models/employee.py`) attributes and DB columns:
  - `id` -> column `EmployeeID` (primary key)
  - `full_name` -> column `FullName` (backend stores full name as single field)
  - `date_of_birth` -> column `DateOfBirth`
  - `gender` -> column `Gender`
  - `phone` -> column `PhoneNumber`
  - `email` -> column `Email`
  - `hire_date` -> column `HireDate`
  - `department_id` -> column `DepartmentID` (FK -> departments.id)
  - `position_id` -> column `PositionID` (FK -> positions.id)
  - `status` -> column `Status`
  - `created_at` -> column `CreatedAt`
  - `updated_at` -> column `UpdatedAt`

- MySQL replica / payroll table (`employees_payroll`) columns (used by MySQL writes):
  - `EmployeeID` (maps to `id`)
  - `FullName` (maps to `full_name`)
  - `DepartmentID`
  - `PositionID`
  - `Status`
  - `SyncedAt` (optional timestamp maintained by replication code)

### Ghi chú về `full_name` vs `first_name`/`last_name`
- API và frontend sử dụng `first_name` / `last_name`.
- Backend repository code (see [backend/repositories/employee_repository.py](backend/repositories/employee_repository.py)) xây dựng `full_name` từ `first_name` + `last_name` trước khi tạo bản ghi SQL Server.
- Khi ghi vào MySQL `employees_payroll`, backend truyền `EmployeeID` và `FullName` (không bắt buộc truyền `first_name`/`last_name`).

### Ví dụ payload tạo (POST /employees)
{
  "first_name": "Patch",
  "last_name": "Fix",
  "email": "patchfix@example.com",
  "phone": "012345000",
  "hire_date": "2022-05-05",
  "date_of_birth": "1985-05-05",
  "department_id": 1,
  "position_id": 1,
  "status": "active"
}

---

## API endpoints liên quan (backend/controllers/employees.py)
- `GET /employees` — trả về danh sách, mỗi item có thể chứa `first_name`/`last_name` (được tách từ `full_name`) hoặc `full_name` nếu không có tách.
- `GET /employees/{id}` — chi tiết nhân viên (serialize trực tiếp model SQL Server)
- `POST /employees` — payload: `EmployeePayload` (xem code). Backend sẽ:
  - xây `full_name` từ `first_name` / `last_name` trước khi tạo SQL Server
  - tạo bản ghi MySQL `employees_payroll` (chuyển `full_name` và `EmployeeID`) trong cùng giao dịch chéo (có cơ chế bồi hoàn)
- `PUT /employees/{id}` — payload: `EmployeeUpdatePayload` (các trường optional). Nếu cập nhật tên, backend cập nhật `full_name` và đồng bộ sang MySQL.
- `DELETE /employees/{id}` — xóa SQL Server và cố gắng xóa MySQL; có cơ chế bồi hoàn nếu MySQL thất bại.

---

## Frontend — trường hiển thị và sử dụng
- [frontend/src/components/EmployeeForm.jsx](frontend/src/components/EmployeeForm.jsx): sử dụng các keys `first_name`, `last_name`, `email`, `phone`, `hire_date`, `department_id`, `position_id`, `status`.
- [frontend/src/components/EmployeeList.jsx](frontend/src/components/EmployeeList.jsx): danh sách chấp nhận `employee` object có thể có `full_name` hoặc `first_name`/`last_name`; cũng hiển thị `latest_salary.amount` nếu có.

---

## Department & Position (tóm tắt)
- `Department`: `id`, `name`, `description` (SQL Server master). Frontend sends `department_id`.
- `Position`: `id`, `title`, `grade`, `description` (SQL Server master). Frontend sends `position_id`.

---

## Payroll / Salary
- Lịch sử lương lưu trong MySQL `salaries` (repository: `payroll_repository`). API `GET /employees/with-payroll` kết hợp SQL Server employee và MySQL salary bằng `employee.id`.

---

## Best practices & chú ý khi phát triển
- Luôn gửi `first_name`/`last_name` từ frontend; backend chịu trách nhiệm ghép `full_name` cho SQL Server / MySQL.
- Không ép `id` từ frontend khi tạo mới — SQL Server tạo `EmployeeID`; backend truyền `id` này sang MySQL sau khi insert SQL Server.
- MySQL employees_payroll có schema hạn chế (chỉ FullName, DepartmentID, PositionID, Status, EmployeeID). Tránh gửi trường không tồn tại trực tiếp cho MySQL inserts/updates.
- Kiểm tra uniqueness của `email` bên client để giảm lỗi; backend vẫn kiểm tra và trả Conflict nếu trùng.

---

Nếu bạn muốn, tôi có thể:
- thêm một bảng ánh xạ CSV/Excel để dễ đọc cho QA
- tự động sinh phần mapping dưới dạng bảng Markdown chi tiết hơn
- hoặc cập nhật README với ví dụ request/response cụ thể

File ánh xạ chính: [docs/data-mapping.md](docs/data-mapping.md)
