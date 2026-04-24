# Deploy Backend lên Railway

## 1. Chuẩn bị

1. Đăng ký tài khoản Railway: https://railway.app
2. Có GitHub account và push code lên GitHub

## 2. Deploy trên Railway

### Bước 1: Đăng nhập Railway
```bash
npx railway login
```

### Bước 2: Khởi tạo project
```bash
npx railway init
```

Chọn project name (hoặc tạo mới).

### Bước 3: Thêm biến môi trường
```bash
npx railway variables
```

Hoặc thêm trực tiếp trên dashboard Railway:

```
FRONTEND_ORIGIN=https://your-firebase-domain.web.app
SQLSERVER_DATABASE=HUMAN
SQLSERVER_SERVER=your-sqlserver-instance
USE_TRUSTED_CONNECTION=true
MYSQL_HOST=your-mysql-host
MYSQL_PORT=3306
MYSQL_DATABASE=PAYROLL
MYSQL_USER=your-mysql-user
MYSQL_PASSWORD=your-mysql-password
ENABLE_TEST_FAILURE_HOOKS=false
```

### Bước 4: Deploy
```bash
npx railway up
```

Hoặc push code lên GitHub, Railway sẽ auto-deploy.

## 3. Lấy URL Backend

Sau khi deploy thành công, Railway sẽ cung cấp URL công cộng, ví dụ:
```
https://your-app-name.railway.app
```

## 4. Cập nhật Frontend

Cập nhật `frontend/.env.production`:
```
VITE_API_URL=https://your-app-name.railway.app
```

Rebuild và redeploy Firebase Hosting:
```bash
cd frontend
npm run build
firebase deploy --only hosting
```

## 5. Kiểm tra CORS

Backend cần cấu hình CORS đúng. Kiểm tra `backend/main.py`:
```python
frontend_origins = os.getenv("FRONTEND_ORIGIN", "http://localhost:5174,http://localhost:5175")
allow_origins = [origin.strip() for origin in frontend_origins.split(",") if origin.strip()]
```

## 6. Troubleshoot

Nếu có lỗi, kiểm tra logs:
```bash
npx railway logs
```

---

**Note:**
- Railway có free tier ~$5/tháng
- Cần cấu hình database connection (SQL Server hoặc MySQL)
- Nếu dùng SQL Server/MySQL on-premises, cần whitelist Railway IP hoặc dùng VPN
