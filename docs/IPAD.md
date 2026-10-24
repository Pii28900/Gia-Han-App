# Nhận nhắc bằng ứng dụng Lịch trên iPad

Bản này xuất lịch độc lập, không cần EXE chạy trên iPad hoặc máy chủ HTTPS, không tự đồng bộ với Windows.

1. Trong app Windows, chọn **Lịch iPad** → **Tải lịch iPad**. File `SoGiaHan-iPad.ics` chứa các tài khoản hiện có.
2. Chuyển file sang iPad dưới dạng tệp đính kèm Mail của chính bạn. Đây chỉ là thao tác chuyển file; các nhắc sau đó do Lịch phát, không gửi email.
3. Mở tệp đính kèm `.ics` trong ứng dụng Mail trên iPad, dùng tùy chọn thêm sự kiện/Thêm tất cả và chọn một lịch riêng tên **Sổ Gia Hạn**. Nếu iPad không hiện tùy chọn nhập, cần kiểm tra phiên bản iPadOS và ảnh màn hình trước khi hướng dẫn tiếp; việc tải file qua Files/Safari không phải lúc nào cũng cho cùng luồng nhập.
4. Vào Cài đặt iPad → Thông báo → Lịch, bật cho phép thông báo. Mở một sự kiện đã nhập để kiểm tra cảnh báo **3 ngày trước** được giữ lại. Kiểm tra chế độ Tập trung nếu không thấy thông báo.

Sự kiện gia hạn lúc 18:00 giờ Việt Nam, báo trước 3 ngày. Ví dụ hạn ngày 30 sẽ nhắc lúc 18:00 ngày 27. Các tháng ngắn dùng ngày cuối tháng, rồi trở lại ngày gốc ở tháng đủ ngày. Cảnh báo đã qua thời điểm khi nhập sẽ không phát lại; kiểm tra kỳ sắp tới để biết lần nhắc đầu tiên.

File được kiểm tra bằng bộ đọc ICS độc lập và kiểm tra recurrence qua tháng 2, nhưng chưa kiểm tra trên iPad thực tế. iPadOS/quyền thông báo/cài đặt Lịch có thể ảnh hưởng việc hiển thị cảnh báo; cần xác nhận trên thiết bị.

Khi sửa/xóa tài khoản hoặc thay đổi lịch trên Windows, xuất lại file. Xóa **lịch riêng Sổ Gia Hạn đã nhập cũ**, rồi nhập bản mới để tránh trùng. Không xóa các lịch cá nhân khác. Các kỳ trong Lịch tự lặp, không phản ánh trạng thái đã thanh toán trong Windows. Lịch có thể tiếp tục nhắc một tài khoản đã xóa khỏi Windows cho đến khi bạn cập nhật lịch trên iPad.

File chứa Gmail và số tiền của bạn; chỉ chuyển qua tài khoản của bạn. Dữ liệu này không được đưa lên GitHub.
