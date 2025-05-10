import sqlite3

# Kết nối hoặc tạo mới file cơ sở dữ liệu
con = sqlite3.connect('db.sqlite3')
cur = con.cursor()

# Tạo bảng nếu chưa tồn tại

# Chèn dữ liệu vào bảng (bỏ qua nếu SKU đã tồn tại)
cur.execute('''
    INSERT INTO apartment_management_nguoidung (password,username,is_superuser,is_staff,is_active,last_name,email,date_joined,first_name) VALUES
    ('ABC123', 'adminketoan',0,1,1,'Huyen','h@gmail.comm','2025-05-08 14:54:11.363977','Dinh')
''')
# INSERT INTO auth_user (password,username,is_superuser,is_staff,is_active,last_name,email,date_joined,first_name) VALUES
#     ('ABC123', 'adminketoan',0,1,1,'Huyen','h@gmail.comm','2025-05-08 14:54:11.363977','Dinh')
# Lưu thay đổi
con.commit()

# Đóng kết nối
con.close()
