# Sổ Gia Hạn — app Windows

Ứng dụng desktop Tkinter, lưu dữ liệu SQLite trên máy. Không gửi email và không cần chạy máy chủ. Python 3.12+ có Tkinter là đủ, không cần thư viện bên ngoài.

## Cài bản mã nguồn trên Windows

1. Cài Python 3.12+ từ python.org, bao gồm Tcl/Tk và Python Launcher.
2. Giải nén toàn bộ gói vào thư mục cố định, ví dụ Documents\SoGiaHan. Không chạy bên trong ZIP.
3. Bấm `Start-Windows.bat`.
4. Bấm **Bật nhắc Windows** trong app để đăng ký lịch nhắc lúc 09:00 mỗi ngày. Giữ nguyên thư mục này vì lịch tham chiếu tới đường dẫn app.

Thông báo là cửa sổ nhắc Windows chứa các tài khoản còn tối đa 3 ngày hoặc quá hạn. Khi cửa sổ app chính đã đóng, Windows Task Scheduler vẫn chạy phần nhắc. Máy phải đang bật và người dùng đăng nhập; nếu bỏ lỡ lịch, Windows được cấu hình chạy bù khi có thể. Không đánh thức máy đang tắt. Tắt nhắc bằng cách xóa tác vụ `SoGiaHanReminder` trong Task Scheduler.

Dữ liệu chính nằm ở `%LOCALAPPDATA%\SoGiaHan\accounts.db`. Bấm **Sao lưu** để xuất bản sao SQLite nhất quán. Bản ZIP riêng gửi người dùng có `seed/accounts.db` chứa 11 tài khoản đã nhập đúng từ HSD.xlsx. Seed chỉ được sao chép khi chưa có DB người dùng; không ghi đè dữ liệu cũ. Không đưa seed, Excel hoặc DB cá nhân lên Git. Bản build công khai không kèm dữ liệu riêng.

## Thêm hoặc xóa email cần nhắc

- Bấm **Thêm email cần nhắc**, nhập Gmail, app, ngày đến hạn, số tiền VNĐ và bấm **Lưu**. Email được đưa vào lịch nhắc hiện có, không cần bật lại lịch Windows.
- Chọn một hoặc nhiều dòng (giữ Ctrl/Shift), bấm **Xóa email đã chọn** rồi xác nhận. Chỉ xóa các dòng đã chọn và dừng nhắc cho chúng; không xóa tài khoản Gmail thật hoặc các app khác cùng Gmail.
- Nếu chưa bật lịch Windows, bấm **Bật nhắc Windows** một lần để nhận nhắc khi cửa sổ app đóng.
- Khi cập nhật, đóng app, giải nén vào cùng thư mục cũ. Dữ liệu tại `%LOCALAPPDATA%\SoGiaHan` được giữ nguyên. Nếu đổi thư mục cài, bấm lại **Bật nhắc Windows**.

## Tính năng

- Thêm/sửa/xóa, tìm Gmail/app, nhập Excel, sao lưu.
- Ngày tháng nhập thủ công dạng YYYY-MM-DD.
- Chu kỳ hàng tháng, giữ ngày gốc qua tháng ngắn: 31/01 → 28/02 → 31/03.
- Lịch kỳ tiếp dự kiến được tính tự động; hạn chưa thanh toán giữ nguyên cho đến khi bấm **Đã gia hạn**, chuyển tới kỳ tương lai gần nhất. Không tự thu tiền hoặc thao tác với nhà cung cấp.
- Excel: nhận diện các cột theo tên `Địa chỉ mail`, `Ngày gia hạn sắp tới`, `giá tiền`, `App`, `Mail đang login ở`; hỗ trợ cả bản có/không có cột `Quy cách gia hạn`. Hiện chỉ hỗ trợ chu kỳ hàng tháng.
- Tiền Excel tính theo nghìn đồng: 165 = 165.000đ. Tiền nhập trong app là VNĐ: nhập 165000. Không nhân lại khi mở app.
- Import bỏ qua cùng Gmail/app/ngày đã có; kiểm tra dữ liệu trước khi nhập lại sau khi sửa ngày thủ công.

## Build file EXE

Workflow `.github/workflows/windows.yml` tự chạy khi push lên `main`, hoặc chạy thủ công qua GitHub Actions. Workflow kiểm tra logic và giao diện trên Windows rồi tạo artifact `SoGiaHan-Windows` chứa `SoGiaHan.exe`. File EXE chưa ký số. Không cần Python trên máy dùng bản EXE.

Tải EXE: vào tab **Actions** của repository → chọn lần chạy **Build Windows App** đã thành công → phần **Artifacts** → tải **SoGiaHan-Windows** (cần đăng nhập GitHub). Giải nén, giữ EXE ở thư mục cố định và chạy. Bản build không chứa dữ liệu cá nhân: bấm **Nhập Excel**, chọn file HSD.xlsx trên máy, rồi bấm **Bật nhắc Windows**. Nếu chưa bật GitHub Actions, bật Actions trong repository trước khi chạy workflow.

Build trực tiếp trên máy Windows:

```
python -m pip install pyinstaller==6.16.0
pyinstaller --noconfirm --onefile --windowed --name SoGiaHan desktop.py
```

Để kèm seed riêng khi build cá nhân, thêm `--add-data "seed;seed"`; giữ dữ liệu riêng ngoài Git.

## Phát triển và kiểm tra

```
python -m unittest discover -s tests -v
python desktop.py
```

Trong cloud Linux không có màn hình Windows: đã kiểm tra logic lịch, tiền, hai cấu trúc Excel và đối chiếu 11 dòng dữ liệu; chưa xác minh giao diện và Task Scheduler trên Windows thực tế. Không coi kiểm tra cú pháp là bằng chứng thông báo Windows đã hoạt động.

Bản web nội bộ cũ vẫn chạy bằng `python app.py`, chỉ lắng nghe loopback cổng 8000; không có đăng nhập hay triển khai công khai. Nó dùng `data/accounts.db` riêng, không đồng bộ với desktop. Không dùng phần web để kiểm chứng thông báo desktop.
