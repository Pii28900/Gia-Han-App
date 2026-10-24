# Sổ Gia Hạn — app Windows mở trong Chrome

Giao diện quản lý gia hạn tiếng Việt, mở trong tab Chrome. Dữ liệu chỉ lưu trên máy. Không gửi email và không cần tài khoản dịch vụ.

## Dùng bản EXE (không cần cài Python)

1. Đăng nhập GitHub, mở tab **Actions** của repository, chọn lần chạy **Build Windows App** thành công mới nhất.
2. Kéo xuống **Artifacts**, tải **SoGiaHan-Windows**, giải nén vào thư mục cố định.
3. Mở `SoGiaHan.exe`. App chạy máy chủ nội bộ và mở tab Chrome; nếu không tìm thấy Chrome sẽ dùng trình duyệt mặc định. Mở EXE lần nữa sẽ mở lại tab, không khởi tạo thêm máy chủ.
4. Bấm **Nhập Excel** và chọn HSD.xlsx trên máy hoặc bấm **Thêm email**.
5. Bấm **Bật thông báo Chrome**, chọn **Cho phép** trong trình duyệt.
6. Bấm **Nhắc cả khi đóng tab** để đăng ký lịch Windows lúc 09:00 mỗi ngày.

Thông báo Chrome chỉ hoạt động khi tab đang mở. Khi đóng tab, lịch Windows vẫn có thể hiện cửa sổ nhắc riêng, không giả lập thông báo Chrome. Máy cần đang bật, bạn đã đăng nhập; Windows được cấu hình chạy bù khi bỏ lỡ lịch. Không nhắc khi máy tắt. Chrome/Windows có thể chặn thông báo nếu quyền bị tắt hoặc chế độ không làm phiền đang bật.

Giữ nguyên vị trí EXE. Nếu di chuyển EXE hoặc cập nhật từ bản cũ, mở bản mới rồi bấm lại **Nhắc cả khi đóng tab** để cập nhật đường dẫn tác vụ. Tắt lịch: xóa `SoGiaHanReminder` trong Task Scheduler.

Đóng tab không tắt tiến trình nền. Muốn thoát hoàn toàn, dùng Task Manager kết thúc `SoGiaHan.exe`. Khi thay phiên bản, đóng tiến trình cũ trước khi mở EXE mới. Máy chủ chỉ lắng nghe loopback cổng 8000, không triển khai lên Internet. Nếu cổng này đang được app khác dùng, hãy đóng ứng dụng đó trước.

## Giao diện Ngày / Đêm

Nút **Chế độ đêm / Chế độ ngày** ở góc trên bên phải chuyển giữa giao diện sáng và tối. Lựa chọn được lưu trong trình duyệt, giữ nguyên sau khi tải lại hoặc mở lại cùng địa chỉ. Dùng Chrome profile khác hoặc xóa dữ liệu trang sẽ đặt lại lựa chọn. Chữ, bảng và nút có cỡ lớn hơn và tương phản cao trong cả hai chế độ; không cần tải font từ Internet.

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

GitHub Actions tự chạy khi push `main` hoặc workflow_dispatch: kiểm tra logic, Tk trên Windows, giao diện Chrome thực, đóng gói rồi kiểm tra HTTP của EXE trước khi upload artifact.

Build trên Windows:

```
python -m pip install pyinstaller==6.16.0
pyinstaller --noconfirm --onefile --windowed --add-data "static;static" --name SoGiaHan browser_app.py
```

EXE chưa ký số. Không đưa DB, Excel, thông tin riêng vào Git. Việc phân phối thông báo thật trên máy người dùng còn phụ thuộc quyền Chrome/Windows và trạng thái đăng nhập.
