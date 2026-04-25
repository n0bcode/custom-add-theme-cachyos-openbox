# 🤖 Agent Developer Guide: CachyOS Openbox (Joyful Desktop)

Tài liệu này được soạn thảo đặc biệt dành cho các AI Agents (như Cline, Cursor, hay Copilot) hoặc các lập trình viên mới khi tiếp nhận và chỉnh sửa dự án **CachyOS Openbox - Joyful Desktop**. 

Đây là một dự án không sử dụng file config tĩnh thông thường mà dùng cơ chế **"Dynamic Injection"** (Bơm cấu hình động) bằng Regex. Bất kỳ sự thay đổi cấu trúc nào không cẩn thận cũng sẽ làm hỏng hệ thống (break).

Dưới đây là những nguyên tắc SỐNG CÒN (Critical Rules) và bài học xương máu (Lessons Learned) đã đúc kết được sau các bản vá lỗi:

---

## 1. Kiến trúc Tiêm cấu hình (Dynamic Injection)

Hệ thống hoạt động dựa trên Bash script kết hợp `sed` để thay đổi màu sắc/theme real-time.
- **KHÔNG hardcode** bất cứ màu sắc nào vào thẳng file cấu hình của Openbox (`rc.xml`, `themerc`), Rofi (`.rasi`), Dunst (`.dunstrc`), hay Tint2 (`.tint2rc`).
- Tất cả màu sắc và trạng thái phải được lấy từ file môi trường tổng: **`~/.joyfuld`**
- Script **`user-interface-set.sh`** là trái tim của hệ thống. Nó đọc `.joyfuld` và dùng `sed` chèn đè lên các file config đang chạy, sau đó reload lại dịch vụ.

> **CRITICAL RULE:** Khi sửa các file mẫu (templates) như Rofi hoặc Tint2, **phải đảm bảo chuẩn xác về Regex**. Script bash đi tìm cụm ký tự kết thúc bằng `#<mã hex>;` hoặc `='#mãhex'` để thay thế. Nếu bạn vô tình làm mất dấu `#` hoặc thay bằng biến không hợp lệ, lệnh `sed` ở các lần chạy sau sẽ bị mù và không thể đổi màu nữa.

---

## 2. Tiền tố Theme (Prefix Generation) & Bash Variables

Khi import một theme mới (ví dụ thư mục tên là `icy-azure-anime-bloom`), script sẽ tự động tạo ra một **Tiền tố 4 ký tự viết hoa** để định danh cho mọi biến số của theme đó.

**Logic cũ (Gây lỗi rỗng biến):** Lấy 4 ký tự đầu (ví dụ: `icy-` thành `ICY-`). Bash không cho phép biến chứa dấu gạch ngang (VD: `$ICY-_GTK`), dẫn đến crash lệnh load cấu hình.
**Logic hiện tại (Bắt buộc tuân thủ):** Cả Python script (`joyful_theme_lib.py`), script import (`import-joyful-theme.sh`) và Core load (`.joyfuld` -> `joyd_cross_variables`) đều đã được cập nhật để loại bỏ tất cả các ký tự đặc biệt (chỉ giữ lại Alphanumeric) trước khi cắt chuỗi:
- `icy-azure-anime-bloom` -> Lọc còn `icyazureanimebloom` -> Upper case: `ICYAZURE...` -> Lấy 4 ký tự: **`ICYA`**.

> 💡 **NOTE CHO AGENT:** Nếu bạn viết thêm hàm hoặc tool nào dính đến Prefix Theme, hãy dùng biểu thức Regex xóa ký tự không hợp lệ `re.sub(r'[^a-zA-Z0-9]', '', string)` (Python) hoặc `tr -cd '[:alnum:]'` (Bash).

---

## 3. Cấu trúc và Định dạng File bắt buộc

### 3.1. Database Config (`db.theme.joy` và `.snippet`)
File chứa thông tin style nút bấm và hình nền của Openbox.
- **Định dạng sai:** Dấu bằng `=` và nháy đơn `''` (Vd: `wallpaper.theme.artistic='image.jpg'`) - *Sẽ gây lỗi đọc Regex của hàm `siq`*.
- **Định dạng chuẩn:** Phải sử dụng khoảng trắng (Tab/Space) và nháy kép `""`.
  ```
  ob_button_style.theme_name.artistic          "circles-filled"
  ob_button_location.theme_name.interactive    "right"
  wallpaper.theme_name.artistic                "my-wallpaper.jpg"
  ```

### 3.2. Cấu trúc Template Rofi (`.rasi`)
File Rofi (đặc biệt trong thư mục `joyful-theme-template/rofi`) phải tuân thủ nghiêm ngặt định dạng cấu trúc CSS sau:
- Không chứa các biến dư thừa không được `sed` xử lý (`bg`, `fg`, `bg-alt`...)
- Tham số `background-alpha` bắt buộc phải là mã HEX 8 ký tự (ví dụ: `#1e1e2ef7`), vì `sed` sẽ đi tìm cụm 2 ký tự cuối (`f7`) để thay đổi độ mờ (opacity).
- Tham số `button-gradient` bắt buộc phải theo format chuẩn `linear-gradient(90, #hex1, #hex2);`
  ```css
  * {
    accent1:          #89b4fa;
    accent2:          #f5c2e7;
    button-gradient:  linear-gradient(90, #89b4fa, #f5c2e7);
    background-alpha: #1e1e2ef7;
    background:       #1e1e2e;
    ...
  }
  ```

### 3.3. Cấu trúc Tint2
Tint2 đã được mở rộng hỗ trợ cả màu Background và Foreground cho chế độ Interactive thay vì chỉ dựa vào `START_COLOR` như cũ.
- Khi tạo template Tint2 mới, hãy kế thừa từ thư mục `joyful-theme-template/tint2/`. Python script sẽ tự động tìm và thay thế tĩnh (Replace) các mã `#3b4252` và `#f9f9f9` thành mã màu do User chọn từ GUI (hoặc AI tạo ra) ngay trong lúc generate theme.

---

## 4. Công cụ (Toolchain)

Dự án có bộ công cụ tự động hóa, tuyệt đối không chỉnh sửa thủ công nếu có thể dùng script:

1. **`joyful-theme-porter.py` (GUI Application)**
   - Đã được refactor thành Python Package: `joyful_theme_ui/` cho module hóa (gồm `main_window`, `dialogs`, `pages/...`).
   - Cung cấp tính năng "AI Integration Bridge": Trích xuất JSON template cấu hình hệ thống (GTK, Icon, Font, Palettes) cho LLM xử lý, sau đó Import lại để sinh thư mục theme tự động.
   - Luôn cập nhật phần giao diện này (như file `pages/creator_page.py`) nếu có thêm biến màu sắc mới cho `.joyfuld`.

2. **`joyful-tester.sh` (The Validator)**
   - Dùng để chẩn đoán hệ thống: `./joyful-tester.sh check <theme_name>`
   - Quét qua 13+ file của theme, kiểm tra các tham số cần thiết trong `.joyfuld` và `db.theme.joy` để đảm bảo theme không thiếu tài nguyên làm crash UI khi đổi.

3. **`import-joyful-theme.sh` (The Deployer)**
   - Để cài đặt một theme vào hệ thống gốc: `./import-joyful-theme.sh custom-themes/my-theme --apply`
   - Tính năng mới: Khả năng chỉ định thư mục mục tiêu với `--target <dir>`. Vô cùng hữu dụng khi test trên máy ảo, máy remote hoặc người dùng lưu config ở thư mục ngoài luồng (VD: Không cài đè thẳng vào `/home/.config` mà cài vào repo dotfiles).
   - *Nếu không có `--apply`*, script chạy chế độ Dry-run, copy ra thư mục `mock-joyful-test` để kiểm thử an toàn.

---

## 5. Tổng kết Workflow (Dành cho Agent khi tạo chức năng mới)

1. **Hiểu Luồng (Trace Flow):** Bất cứ tính năng UI mới nào (thêm menu, đổi màu thanh bar, popup...) cũng phải bắt đầu từ việc định nghĩa biến HEX trong `.joyfuld`.
2. **Sửa Shell (Update Core):** Mở `user-interface-set.sh`, chèn thêm một lệnh `sed -e "s/#.../${NEW_VAR}/"` để bơm biến mới vào file cấu hình mục tiêu.
3. **Cập nhật Python:** Quay lại sửa `joyful_theme_ui/pages/creator_page.py` để bổ sung ô chọn màu cho biến mới (Thêm Color Picker vào Grid và xuất ra file snippet).
4. **Kiểm thử (Validate):** Luôn dùng `joyful-tester.sh` để bắt lỗi rò rỉ biến/thiếu file trước khi xác nhận.

*— Hãy coi CachyOS Openbox Joyful như một Framework DOM động (như ReactJS) thay vì các file tĩnh HTML. Mọi thứ đều được Render qua Bash Scripts.*