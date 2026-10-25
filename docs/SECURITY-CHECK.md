# Kiểm tra cảnh báo tải xuống

Chrome báo “đã chặn tệp tải xuống nguy hiểm” không đủ để kết luận cảnh báo nhầm. Không tắt Safe Browsing/Defender hoặc bấm bỏ qua chỉ vì app chạy được trong kiểm tra chức năng.

Workflow `Review downloaded Windows executable` tải lại đúng artifact đã phát hành từ run được chỉ định, không chạy EXE, cập nhật nhận diện Microsoft Defender rồi quét file đó. Báo cáo có SHA-256, thời điểm, engine/nhận diện, trạng thái chữ ký và run nguồn. Có thể chạy thủ công với run ID khác trong Actions. Bản mặc định kiểm tra run 40154168865.

Workflow build bình thường cũng quét file EXE mới trước khi chạy smoke test hoặc upload. Nếu scanner không chạy được, cập nhật thất bại, phát hiện đe dọa, file bị sửa/cách ly, hoặc không xác minh được kết quả thì dừng phát hành EXE; báo cáo vẫn được lưu khi có thể. Không thay đổi cách đóng gói để cố vượt cảnh báo.

`NoThreatsDetected` chỉ có nghĩa Microsoft Defender không phát hiện trên SHA-256 đó tại lần quét đã ghi; không phải bảo đảm file an toàn, không phải kết luận của Google Safe Browsing và không đảm bảo file trên máy người dùng giống file được quét.

Đối chiếu file trên Windows mà không chạy:

```powershell
Get-FileHash -Algorithm SHA256 'C:\duong-dan\SoGiaHan.exe'
```

Đối chiếu với báo cáo đúng run/bản phát hành. Bản build đã quét có file `.sha256` đi kèm để đối chiếu tính nguyên vẹn; checksum không thay thế quét mã độc hay chữ ký nhà phát hành. Nếu Chrome đã chặn/cách ly và bạn không còn file, không cần bỏ qua cảnh báo để lấy file chỉ nhằm làm bước này.

Bản hiện tại chưa có bước ký số bằng chứng chỉ nhà phát hành đáng tin cậy. Việc thiếu chữ ký có thể liên quan đến đánh giá uy tín nhưng chưa chứng minh nguyên nhân cảnh báo “nguy hiểm”. Các kiểm tra UI/API trước đây chỉ xác minh chức năng, không phải kiểm tra chống mã độc.
