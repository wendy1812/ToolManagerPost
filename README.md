# Quản lý Bài viết

Ứng dụng web quản lý bài viết với các chức năng:
- Thêm và quản lý dự án
- Thêm link bài viết
- Sắp xếp theo nền tảng (SNS)
- Copy link và mở trong tab mới
- Đánh dấu bài viết đã hoàn thành

## Cấu trúc dự án
```
quanlybaiviet/
├── app.py              # File chính chứa logic backend
├── data.json           # File lưu trữ dữ liệu
├── templates/          # Thư mục chứa file HTML
│   ├── index.html     # Trang chính
│   └── login.html     # Trang đăng nhập
└── README.md          # File hướng dẫn
```

## Các chức năng chính

### 1. Quản lý dự án
- Thêm dự án mới
- Xóa dự án
- Xóa tất cả dữ liệu

### 2. Quản lý bài viết
- Thêm link bài viết (nhiều link cùng lúc)
- Tự động nhận diện nền tảng (SNS)
- Sắp xếp theo SNS
- Copy link và mở trong tab mới
- Đánh dấu bài viết đã hoàn thành
- Xóa bài viết đã chọn

### 3. Bảo mật
- Đăng nhập với mật khẩu cố định
- Tất cả API endpoint đều có xác thực

## Các điểm cần lưu ý
1. Link mới sẽ tự động thêm vào dự án mới nhất
2. Thời gian được lưu theo múi giờ GMT+7
3. Dữ liệu được lưu trong file data.json
4. Giao diện được tối ưu cho cả desktop và mobile

## Cách sử dụng
1. Đăng nhập với mật khẩu: 9998
2. Thêm dự án mới (nếu cần)
3. Thêm link bài viết (mỗi link một dòng)
4. Sử dụng các chức năng quản lý bài viết

## Lưu ý khi chỉnh sửa code
1. Luôn backup file data.json trước khi sửa
2. Kiểm tra kỹ các thay đổi trước khi commit
3. Test đầy đủ các chức năng sau khi sửa
4. Giữ nguyên cấu trúc dữ liệu trong data.json 