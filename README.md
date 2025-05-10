# Quản Lý Thu Phí Chung Cư - Nhóm 18

Dự án Django giúp quản lý cư dân, hộ gia đình và các khoản thu phí trong chung cư.

## Yêu cầu hệ thống

- Python 3.8 trở lên
- pip (trình quản lý gói của Python)

## Cài đặt và chạy dự án

### 1️. Tạo môi trường ảo (ở thư mục gốc dự án)

```bash
# Tạo môi trường ảo tên là venv
python -m venv venv

# Kích hoạt môi trường ảo
# Trên macOS / Linux
source venv/bin/activate

# Trên Windows
.\venv\Scripts\activate
```
### 2️. Cài đặt các thư viện phụ thuộc

```bash
pip install -r requirements.txt
```

### 3️. Tạo cơ sở dữ liệu

```bash
# Tạo file migration từ các model
python manage.py makemigrations

# Tạo database và các bảng
python manage.py migrate
```

### 4. Chạy dự án

```bash
python manage.py runserver
```
