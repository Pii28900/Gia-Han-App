# Sổ Gia Hạn — app Windows mở trong Chrome

Giao diện quản lý gia hạn tiếng Việt, mở trong tab Chrome. Dữ liệu chỉ lưu trên máy. Không gửi email và không cần tài khoản dịch vụ.

## Dùng bản EXE (không cần cài Python)

1. Đăng nhập GitHub, mở tab **Actions** của repository, chọn lần chạy **Build Windows App** thành công mới nhất.
2. Kéo xuống **Artifacts**, tải **SoGiaHan-Windows**, giải nén vào thư mục cố định.
3. Mở `SoGiaHan.exe`. App chạy máy chủ nội bộ và mở tab Chrome; nếu không tìm thấy Chrome sẽ dùng trình duyệt mặc định. Mở EXE lần nữa sẽ mở lại tab, không khởi tạo thêm máy chủ.
4. Bấm **Nhập Excel** và chọn HSD.xlsx trên máy hoặc bấm **Thêm email**.
5. Bấm **Thử thông báo**, chọn **Cho phép** trong Chrome. App sẽ tạo thông báo thử ngay, không phải chờ 18:00.
6. Bấm **Nhắc cả khi đóng tab** để đăng ký lịch Windows lúc 18:00 mỗi ngày.

Thông báo Chrome tự động chỉ phát từ 18:00 theo giờ Việt Nam khi tab đang mở; nếu mở lại sau 18:00 sẽ kiểm tra và nhắc bù trong ngày. Nút gửi thử không phải chờ đến 18:00. Lịch Windows chạy lúc 18:00 theo múi giờ máy, nên đặt Windows về múi giờ Việt Nam nếu dùng lịch này. Sau khi cập nhật từ lịch 09:00 cũ, bấm lại **Nhắc cả khi đóng tab** để thay lịch thành 18:00. Khi đóng tab, lịch Windows vẫn có thể hiện cửa sổ nhắc riêng, không giả lập thông báo Chrome. Máy cần đang bật, bạn đã đăng nhập; Windows được cấu hình chạy bù khi bỏ lỡ lịch. Không nhắc khi máy tắt. Chrome/Windows có thể chặn thông báo nếu quyền bị tắt hoặc chế độ không làm phiền đang bật.

Giữ nguyên vị trí EXE. Nếu di chuyển EXE hoặc cập nhật từ bản cũ, mở bản mới rồi bấm lại **Nhắc cả khi đóng tab** để cập nhật đường dẫn tác vụ. Tắt lịch: xóa `SoGiaHanReminder` trong Task Scheduler.

Đóng tab không tắt tiến trình nền. Muốn thoát hoàn toàn, dùng Task Manager kết thúc `SoGiaHan.exe`. Khi thay phiên bản, đóng tiến trình cũ trước khi mở EXE mới. Máy chủ chỉ lắng nghe loopback cổng 8000, không triển khai lên Internet. Nếu cổng này đang được app khác dùng, hãy đóng ứng dụng đó trước.

## Giao diện Ngày / Đêm

Nút **Chế độ đêm / Chế độ ngày** ở góc trên bên phải chuyển giữa giao diện sáng và tối. Lựa chọn được lưu trong trình duyệt, giữ nguyên sau khi tải lại hoặc mở lại cùng địa chỉ. Dùng Chrome profile khác hoặc xóa dữ liệu trang sẽ đặt lại lựa chọn. Chữ, bảng và nút có cỡ lớn hơn và tương phản cao trong cả hai chế độ; không cần tải font từ Internet.

## Thử thông báo và hoàn tác

- **Thử thông báo** gửi thông báo thật qua service worker của Chrome với tiêu đề **Sổ Gia Hạn · Thông báo thử**. Nội dung mẫu cho biết lịch nhắc 18:00, trước hạn 3 ngày. Nếu Chrome không hỗ trợ service worker sẽ dùng Notification API trực tiếp.
- Nếu đã cho phép nhưng không thấy banner: kiểm tra trung tâm thông báo Windows (**Windows + N**), bật thông báo Google Chrome trong Windows và tắt Không làm phiền. App chỉ xác nhận đã gửi yêu cầu tới Chrome, không thể ép Windows hiển thị khi hệ thống chặn.
- **Hoàn tác** cạnh **Sao lưu** khôi phục lần thêm, sửa, xóa, xác nhận gia hạn hoặc nhập Excel gần nhất. Có xác nhận trước khi thực hiện. Bấm tiếp để lùi nhiều bước, tối đa 20 thay đổi; lịch sử giữ trong SQLite khi đóng/mở app.
- Nếu dữ liệu đã thay đổi ngoài lịch sử hoặc có thao tác mới từ tab khác, app yêu cầu tải lại để tránh hoàn tác đè lên dữ liệu mới. Hoàn tác không thu hồi một thông báo đã gửi hoặc một khoản đã thanh toán thực tế.
- Nút **Lịch iPad** đã được bỏ khỏi giao diện theo yêu cầu. Bản này chỉ chạy trên Windows; không có đồng bộ HTTPS.

## Dữ liệu và quản lý tài khoản

- SQLite tại `%LOCALAPPDATA%\SoGiaHan\accounts.db`, dùng chung với bản desktop cũ nên giữ được dữ liệu hiện có. Bản GitHub không kèm Gmail/Excel/DB cá nhân.
- **Thêm email**: Gmail, app, ngày đến hạn, số tiền VNĐ, thiết bị/ghi chú. **Sửa** để cập nhật.
- Chọn checkbox một hoặc nhiều dòng rồi **Xóa đã chọn**. Chỉ xóa khỏi lịch nhắc, không xóa tài khoản Gmail thật.
- **Sao lưu** tải bản SQLite nhất quán. Giữ bản sao riêng vì chứa dữ liệu cá nhân. Có thể phục hồi bằng cách đóng app hoàn toàn rồi thay file SQLite ở đường dẫn trên bằng bản sao.
- **Đã gia hạn** chuyển ngày tới kỳ tương lai gần nhất; không tự thanh toán. Cột kỳ tiếp dự kiến tính sau kỳ hiện tại. Ngày gốc giữ qua tháng ngắn: 31/01 → 28/02 → 31/03.
- Bộ lọc trạng thái, tìm Gmail/app, tổng chi phí hàng tháng và số tài khoản sắp/quá hạn.

Excel: nhận cột theo tên `Địa chỉ mail`, `Ngày gia hạn sắp tới`, `giá tiền`, `App`, `Mail đang login ở`; nhận cả bản có cột `Quy cách gia hạn`. Chỉ hỗ trợ chu kỳ hàng tháng. Số tiền Excel tính theo nghìn đồng: **165 → 165.000đ**; số tiền nhập thủ công là VNĐ: **165000**. Import bỏ qua cùng Gmail/app/ngày đã có.

## Phát triển và build

Python 3.12+ và Tkinter, không cần thư viện ngoài cho app:

```
python -m unittest discover -s tests -v
python browser_app.py
```

`Start-Windows.bat` mở bản mã nguồn trong trình duyệt (cần Python); `desktop.py` vẫn giữ giao diện Tkinter và cung cấp cửa sổ nhắc nền Windows.

Kiểm tra trình duyệt: cài Playwright, chạy `python tests/browser_smoke.py` với Chrome đã cài; Linux có thể đặt `CHROME_PATH=/usr/bin/chromium`.

GitHub Actions tự chạy khi push `main` hoặc workflow_dispatch: kiểm tra logic, Tk trên Windows, giao diện Chrome thực, thông báo đăng ký trong service worker, hoàn tác nhiều bước, đóng gói rồi kiểm tra HTTP của EXE trước khi upload artifact.

Build trên Windows:

```
python -m pip install pyinstaller==6.16.0
pyinstaller --noconfirm --onefile --windowed --add-data "static;static" --name SoGiaHan browser_app.py
```

EXE chưa ký số. Không đưa DB, Excel, thông tin riêng vào Git. Việc phân phối thông báo thật trên máy người dùng còn phụ thuộc quyền Chrome/Windows và trạng thái đăng nhập.
