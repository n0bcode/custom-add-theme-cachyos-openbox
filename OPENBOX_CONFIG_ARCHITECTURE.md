# CachyOS Openbox Configuration Architecture (Joyful Desktop)

## 1. Mục Đích Của Tài Liệu
Tài liệu này cung cấp cái nhìn tổng quan về hệ thống cấu hình Openbox tùy chỉnh (dựa trên framework "Joyful Desktop") đang được sử dụng trong thư mục này. Mục tiêu là giúp các AI Agents hoặc Developer sau này nhanh chóng nắm bắt kiến trúc, luồng hoạt động và **các quy tắc nghiêm ngặt** khi thao tác với repository, từ đó phục vụ đúng nhu cầu debug, phát triển và custom theme của người dùng.

## 2. Quy Tắc Quan Trọng (CRITICAL RULES Bắt Buộc Tuân Thủ)
*   **CHỈ CHỈNH SỬA FILE, KHÔNG THỰC THI LỆNH LÀM THAY ĐỔI TRẠNG THÁI HỆ THỐNG:** Thư mục `cachyos-openbox` này là môi trường staging (chuẩn bị) được dùng để mang sang các Virtual Desktop hoặc Live Linux (CachyOS) để kiểm tra. **TUYỆT ĐỐI KHÔNG** chạy các lệnh làm thay đổi trạng thái của host system đang chạy thông qua terminal (ví dụ: không chạy `openbox --reconfigure`, `killall tint2`, hay trực tiếp execute các file `.sh` như `toggle-mode.sh` hoặc `python3 file.py` lên hệ thống hiện tại).
*   **Kiểm Tra An Toàn (Safe Testing & Validation):** Nếu cần kiểm tra logic của các file cấu hình, kịch bản bash (bash scripts) hoặc sự liên kết giữa chúng, hãy tạo các **file test riêng biệt** (ví dụ: test scripts, dummy configs) ngay tại thư mục này để dry-run thay vì chạy trực tiếp các script hệ thống. Điều này đảm bảo chất lượng code và tránh conflict/phá hỏng logic sau khi edit/custom theme.
*   **Bảo Toàn Cấu Trúc Regex (`sed` patterns):** Hệ thống chuyển theme phụ thuộc rất nhiều vào công cụ `sed` với các pattern Regex cụ thể để tìm và ghi đè giá trị (màu sắc, đường dẫn, tên theme). Khi chỉnh sửa cấu trúc các file config gốc (như `rc.xml`, `.rasi`, `.tint2rc`, `themerc`), **phải đảm bảo không phá vỡ định dạng** mà các script `sed` đang bám vào.

## 3. Kiến Trúc Tổng Quan (Joyful Desktop Framework)
Hệ thống này không chỉ cấu hình Openbox đơn thuần mà là một giải pháp đồng bộ toàn bộ Desktop Environment (DE). Khi một theme được chọn, nó sẽ đồng bộ: Openbox (WM), GTK, Icons, Rofi (Menu), Tint2 (Panel), Dunst (Notifications), Nitrogen (Wallpaper), và URxvt/Terminal.

### 3.1. Các Thành Phần Lưu Trữ Cốt Lõi (State & Config)
*   **`.joyfuld`** (Thư mục gốc): File trung tâm (core environment) chứa toàn bộ biến môi trường, định nghĩa mã màu (HEX), tên GTK Theme, Icon, đường dẫn thư mục và các alias/function shell dùng chung (như `joyd_theme_set`).
*   **`.config/openbox/joyful-desktop/db.mode.joy`**: Database nhỏ lưu trạng thái hiện tại của hệ thống (`current_theme`, `current_mode`).
*   **`.config/openbox/joyful-desktop/db.theme.joy`**: Lưu cấu hình chi tiết cho từng theme tương ứng (ví dụ: kiểu nút bấm, hình nền nào đi với theme nào).
*   **`.config/openbox/rc.xml`**: File cấu hình chính của Openbox. Lưu ý: File này được các script chỉnh sửa *động* (sửa tên thẻ `<theme><name>`, đổi thứ tự nút `<titleLayout>`) chứ không tĩnh 100%.
*   **`.config/openbox/joyful-desktop/themerc`**: File quy định giao diện chi tiết của Openbox, nơi các mã màu sẽ được tiêm (inject) vào trực tiếp.

### 3.2. Luồng Hoạt Động Chuyển Theme (Workflow)
Hành động chuyển đổi theme thường được kích hoạt qua phím tắt (VD: `W-S-r`) gọi đến `toggle-mode.sh`, sau đó diễn ra chuỗi xử lý sau:

1.  **Dọn dẹp (Kill processes):** Tắt `tint2`, `dunst` ngay lập tức để giải phóng UI và tránh xung đột đồ họa.
2.  **Xác định & Lưu Trạng thái:** Đọc biến, xác định vòng lặp theme tiếp theo và cập nhật state vào `db.mode.joy`.
3.  **Giai đoạn 1: `theme-set.sh` (Xử lý Cấu trúc & Assets):**
    *   Copy các file ảnh `.xbm` (chứa hình ảnh nút close, maximize, minimize) của theme mới vào thư mục theme Openbox hiện hành.
    *   Dùng `sed` sửa đổi thẻ `<titleLayout>` và `<name>` (tên theme) trực tiếp trong `rc.xml`.
    *   Sửa `gtk-theme-name` và `gtk-icon-theme-name` trong cấu hình GTK 2/3 (`settings.ini`, `.gtkrc-2.0`).
4.  **Giai đoạn 2: `user-interface-set.sh` (Xử lý Màu sắc & Reload WM):**
    *   Dùng `sed` ghi đè mã màu HEX (lấy từ `.joyfuld`) vào các file giao diện: `themerc` (Openbox), `.rasi` (Rofi), `.dunstrc` (Dunst), `.tint2rc` (Tint2).
    *   **Thực thi `openbox --reconfigure &`** để ép Window Manager đọc lại `rc.xml` và `themerc` mới ngay lập tức.
    *   Đổi hình nền bằng `nitrogen` và khởi động lại các daemon (`tint2`, `dunst`) với file cấu hình đã được inject màu mới.

## 4. Hướng Dẫn Dành Cho Developer / Agent
*   **Khi cần Thêm/Sửa Màu Sắc:** Hãy bắt đầu từ việc phân tích và chỉnh sửa các biến màu sắc (HEX) trong file `.joyfuld`.
*   **Khi cần Sửa Layout/Logic Openbox:** Có thể chỉnh sửa `rc.xml`, nhưng phải luôn ghi nhớ rằng các giá trị trong thẻ `<theme><name>` và `<titleLayout>` sẽ liên tục bị các script bash ghi đè.
*   **Khi cần Tùy chỉnh Menu/Panel:** Chỉnh sửa các template config trong `.config/rofi/`, `.config/tint2/`. Tuy nhiên, trước khi sửa cấu trúc, hãy dùng công cụ tìm kiếm (`grep`) kiểm tra xem file `user-interface-set.sh` có đang chứa lệnh `sed` nào dựa dẫm vào dòng bạn định thay đổi hay không để tránh làm hỏng cơ chế tự động đổi màu.