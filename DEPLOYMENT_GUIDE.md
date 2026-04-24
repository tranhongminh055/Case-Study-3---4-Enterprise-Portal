# Hướng dẫn Deploy Lên Public

## 1. Chuẩn bị

### Frontend (Vite + React)
- Firebase config đã cập nhật: `enterprise-portal-ac043`
- Tạo `.env.production` để cấu hình API URL
- Tạo `firebase.json` để cấu hình Firebase Hosting

### Backend (FastAPI)
- Cần deploy backend tới server công cộng (Heroku, Azure, AWS, VPS, v.v.)
- Cập nhật `FRONTEND_ORIGIN` trong backend `.env` thành domain frontend public

## 2. Build Frontend

```bash
cd frontend
npm install
npm run build
```

## 3. Deploy Frontend lên Firebase Hosting

### Bước 3.1: Cập nhật API URL
Sửa file `frontend/.env.production`:
```
VITE_API_URL=https://your-backend-domain.com
```

### Bước 3.2: Build lại với environment production
```bash
npm run build
```

### Bước 3.3: Deploy lên Firebase
```bash
firebase deploy --only hosting
```

## 4. Deploy Backend

### Tùy chọn: Heroku (nếu chọn Heroku)

```bash
cd backend
heroku login
heroku create your-app-name
heroku config:set FRONTEND_ORIGIN=https://your-firebase-domain.web.app
git push heroku main
```

### Tùy chọn: Azure App Service
```bash
az login
az webapp up --name your-app-name --resource-group your-group
```

### Tùy chọn: VPS riêng
- Upload code lên server
- Cài đặt Python, uvicorn
- Chạy: `uvicorn backend.main:app --host 0.0.0.0 --port 8000`
- Setup nginx/reverse proxy trỏ tới backend

## 5. Cập nhật CORS trên Backend

Trong `backend/.env`, cập nhật:
```
FRONTEND_ORIGIN=https://your-firebase-domain.web.app
```

## 6. Kiểm tra

1. Truy cập: https://your-firebase-domain.web.app
2. Thử login/register
3. Kiểm tra console browser (F12) xem có lỗi CORS không

---

**Lưu ý:**
- Thay `your-backend-domain.com` bằng URL backend thực tế
- Thay `your-firebase-domain.web.app` bằng domain Firebase Hosting thực tế
- Không commit `.env` files chứa secrets lên git
