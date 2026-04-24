# CachyOS Openbox - Joyful Desktop Theming Guide
Tài liệu này là cẩm nang toàn tập về cách hoạt động, tùy biến và thiết lập một giao diện (Theme) mới cho hệ thống Openbox trên CachyOS, kế thừa và tuân thủ chặt chẽ kiến trúc của **Joyful Desktop Framework**.

## 1. Nguyên Tắc Cốt Lõi (CRITICAL RULES)
1. **Không sửa cứng (Hardcode) cấu hình:** Toàn bộ hệ thống Openbox, Rofi, Dunst, Tint2 trong kiến trúc này được điều khiển **ĐỘNG** thông qua mã lệnh `sed` từ các bash script.
   - *Ví dụ:* Bạn không được mở `rc.xml` ra và đổi thẻ `<name>` thành tên theme mới. Script sẽ tự động dùng Regex đè lại nó.
2. **Nơi thiết lập Màu sắc (Colors) và Biến (Variables):** Toàn bộ dữ liệu "linh hồn" của hệ thống được tập trung tại một file ẩn tên là `~/.joyfuld` (và database phụ `db.theme.joy`). Khi muốn làm một theme mới, bạn phải định nghĩa toàn bộ biến của theme đó vào đây.
3. **Tiền tố Biến (Prefix):** Bất kể tên theme của bạn là gì (vd: `dracula`), hệ thống sẽ cắt đúng **4 KÝ TỰ ĐẦU**, IN HOA (vd: `DRAC`) để gán làm tiền tố biến. (Vd: `DRAC_GTK`, `DRAC_ART_ROFI_ACCNT1`).

---

## 2. Quy Trình Tạo Theme Mới an toàn (Theming Workflow)

Chúng ta có một bộ công cụ 3 món (Toolchain) hỗ trợ tận răng việc này, nhằm loại bỏ rủi ro bạn làm "vỡ" giao diện của CachyOS.

### Bước 1: Khởi tạo từ Template
Bạn **KHÔNG BAO GIỜ** phải viết các file cấu hình Rofi, Tint2 hay Dunst từ con số 0.
Hãy dùng thư mục gốc `joyful-theme-template/`:
1. Copy thư mục này thành một tên mới (ví dụ: `my-theme`).
2. Vào các file bên trong (`env.joyfuld.snippet`, `db.theme.joy.snippet`) và thay thế từ khóa `THEME_NAME` thành `my-theme`. Cập nhật lại các mã màu HEX cho đúng gu thẩm mỹ của bạn. Sửa lại prefix 4 ký tự cho khớp.
3. Cung cấp hình nền và icon thật cho vào các thư mục `wallpapers/` và `icons/`.

### Bước 2: Kiểm Tra & Mô Phỏng (Dry-Run Test)
Trước khi đưa theme của bạn vào máy thật, hãy sử dụng công cụ Đa năng (Multi-tool):
```bash
# Kiểm tra xem bạn có khai báo thiếu biến Environment nào trong template không?
./joyful-tester.sh check my-theme

# Chạy giả lập (Mock/Dry-run) quá trình chuyển theme để xem có bị lỗi format Regex không?
./joyful-tester.sh dry-run my-theme
```

### Bước 3: Đưa vào Hệ Thống (Import)
Khi script Test đã báo `Hoàn hảo (Errors: 0)`, bạn tiến hành "Bơm" theme của bạn vào hệ thống CachyOS gốc một cách cực kỳ an toàn bằng công cụ Import:
```bash
./import-joyful-theme.sh my-theme --apply
```
*Lưu ý: Lệnh này KHÔNG xóa các theme cũ như `nordic` hay `mechanical`. Nó chỉ Append (gắn thêm) các cấu hình của bạn vào `.joyfuld` và copy các file mới đứng cạnh các file cũ.*

---

## 3. Các Điểm Mạnh & Cải Tiến Đáng Giá (Learned from Fork)
Mặc dù chúng ta không sử dụng cấu trúc thư mục rải rác (`~/.local`) của repo Fork (dotfiles-linux), nhưng bộ mã nguồn của họ chứa những tinh chỉnh System/Bash cực kỳ đáng giá mà CachyOS có thể áp dụng vào script khởi động (`autostart.sh`) hoặc script chuyển theme (`theme-set.sh` / `user-interface-set.sh`):

### 3.1. Sửa lỗi Tràn CPU của Thunar (Tumblerd Bug)
- **Vấn đề:** Trình xem trước hình ảnh `tumblerd` của XFCE (dùng kèm với Thunar trên Openbox) hay bị kẹt và ngốn 100% CPU/RAM sau một thời gian dài.
- **Giải pháp:** Repo fork đã gọi một background script tên là `tumblerd-fix &` chạy ngầm trong `autostart.sh` để giám sát và tự động "kill" process này khi nó bắt đầu bị kẹt. Rất khuyến nghị thêm logic này vào máy.

### 3.2. Hiệu Suất File System (Symlink vs Copy)
- **Vấn đề:** Mỗi lần bạn đổi theme, `theme-set.sh` cũ dùng lệnh `cp -f` để copy đè hàng chục tấm hình nút bấm (Close/Max/Min `.xbm`) vào thư mục Openbox. Quá trình này tạo rác I/O và làm chậm ổ cứng.
- **Cải tiến:** Tác giả thay thế bằng **Liên Kết Mềm (Relative Symlink)**:
  `ln -fnrs "${OB_BUTTON_STYLE_DIR}/${CHK_OB_BUTTON_STYLE}"/*.'xbm' "${OBT_D}/"`
  Giúp việc chuyển theme đạt tốc độ gần như tức thời.

### 3.3. `Feh` Nhẹ và Tốt Hơn `Nitrogen`
- **Vấn đề:** Nitrogen đôi khi bị lỗi lưu cấu hình multi-monitor và nặng nề khi chạy dạng command-line để chuyển hình nền.
- **Cải tiến:** Repo Fork đã dùng `feh` để thay thế hoàn toàn trong file `user-interface-set.sh`:
  `feh --bg-fill --no-fehbg "${CHK_WALLPAPER_DIR}/${CHK_WALLPAPER}"`
  *(Thậm chí họ còn tích hợp lệnh `xfconf-query` để đổi luôn hình nền cho XFCE Desktop nếu bạn dùng mix DE)*.

### 3.4. Hệ Thống Âm Thanh Hiện Đại (PipeWire)
- Cấu trúc khởi động của CachyOS nên được chuyển dịch từ `pulseaudio` truyền thống sang `pipewire`, `pipewire-pulse` và `wireplumber` trong `autostart.sh`. Điều này giúp quản lý âm thanh (Đặc biệt với Bluetooth hoặc Stream) mượt mà và ít độ trễ hơn rất nhiều.
