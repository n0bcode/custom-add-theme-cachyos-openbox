#!/usr/bin/env bash
# ─────────────────────────────────────────────
# import-joyful-theme.sh — Joyful Desktop Theme Importer
# Sử dụng: ./import-joyful-theme.sh <path_to_theme_folder> [--apply]
#
# Nếu không có cờ --apply, script sẽ chạy ở chế độ DRY-RUN (Mô phỏng).
# ─────────────────────────────────────────────

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ $# -eq 0 ]]; then
    echo -e "${YELLOW}Cách sử dụng: $0 <path_to_theme_folder> [--apply]${NC}"
    echo -e "   Thư mục theme mẫu có thể tham khảo tại: ${GREEN}joyful-theme-template/${NC}"
    exit 1
fi

THEME_SRC="${1%/}" # Xóa dấu / ở cuối nếu có
APPLY_MODE=0

if [[ "${2:-}" == "--apply" ]]; then
    APPLY_MODE=1
fi

if [[ ! -d "$THEME_SRC" ]]; then
    echo -e "${RED}[✗] Thư mục nguồn không tồn tại: $THEME_SRC${NC}"
    exit 1
fi

THEME_NAME="$(basename "$THEME_SRC")"
# Tạo tiền tố 4 ký tự viết hoa cho THEME_NAME
UCTM=$(echo "$THEME_NAME" | tr '[:lower:]' '[:upper:]')
PREFIX_T="${UCTM:0:4}"

echo -e "${BLUE}══════════════════════════════════════════════════${NC}"
echo -e "${BLUE}    JOYFUL DESKTOP THEME IMPORTER                 ${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════${NC}"
echo -e "Theme name: ${GREEN}${THEME_NAME}${NC}"
echo -e "Prefix (4 chars): ${YELLOW}${PREFIX_T}${NC}"

if [[ $APPLY_MODE -eq 0 ]]; then
    echo -e "${YELLOW}[!] Đang chạy ở chế độ DRY-RUN (Mô phỏng). Không có file hệ thống nào bị thay đổi.${NC}"
    echo -e "${YELLOW}    Thêm cờ --apply ở cuối lệnh để thực thi thật.${NC}"
    echo -e "${BLUE}══════════════════════════════════════════════════${NC}"
    DEST_DIR="${SCRIPT_DIR}/mock-import-${THEME_NAME}"
    rm -rf "$DEST_DIR"
    mkdir -p "$DEST_DIR"
    # Copy hệ thống gốc sang mock
    cp -r "${SCRIPT_DIR}/.config" "$DEST_DIR/" 2>/dev/null || mkdir -p "$DEST_DIR/.config"
    cp -r "${SCRIPT_DIR}/.themes" "$DEST_DIR/" 2>/dev/null || mkdir -p "$DEST_DIR/.themes"
    cp -r "${SCRIPT_DIR}/.icons" "$DEST_DIR/" 2>/dev/null || mkdir -p "$DEST_DIR/.icons"
    cp -r "${SCRIPT_DIR}/.wallpapers" "$DEST_DIR/" 2>/dev/null || mkdir -p "$DEST_DIR/.wallpapers"
    cp "${SCRIPT_DIR}/.joyfuld" "$DEST_DIR/" 2>/dev/null || touch "$DEST_DIR/.joyfuld"
else
    echo -e "${RED}[!] CHẾ ĐỘ THỰC THI (--apply). File hệ thống sẽ bị thay đổi.${NC}"
    echo -e "${BLUE}══════════════════════════════════════════════════${NC}"
    DEST_DIR="${SCRIPT_DIR}"
fi

# Hàm tiện ích copy
copy_file() {
    local src="$1"
    local dest="$2"
    local desc="$3"
    
    if [[ -f "$src" ]]; then
        mkdir -p "$(dirname "$dest")"
        if [[ $APPLY_MODE -eq 1 ]]; then
            cp "$src" "$dest"
        else
            cp "$src" "$dest" # Vẫn copy trong mock
        fi
        echo -e "  ${GREEN}[✓]${NC} ${desc} -> ${dest}"
    else
        echo -e "  ${RED}[✗]${NC} Thiếu file nguồn: ${src}"
        exit 1
    fi
}

append_snippet() {
    local src="$1"
    local dest="$2"
    local desc="$3"
    
    if [[ -f "$src" ]]; then
        if grep -q "THEME_NAME" "$src"; then
             echo -e "  ${YELLOW}[!]${NC} Cảnh báo: File $src vẫn còn chứa chữ 'THEME_NAME' chưa được đổi tên."
        fi
        
        # Nếu chưa tồn tại phần theme này thì mới append
        if grep -qiE ".*${THEME_NAME}.*" "$dest"; then
             echo -e "  ${YELLOW}[!]${NC} ${desc}: Dữ liệu cho ${THEME_NAME} dường như đã tồn tại. Bỏ qua ghi đè để an toàn."
        else
             echo "" >> "$dest"  # Đảm bảo xuống dòng trước khi append
             cat "$src" >> "$dest"
             echo -e "  ${GREEN}[✓]${NC} Đã gộp (append) ${desc} vào ${dest}"
        fi
    else
        echo -e "  ${RED}[✗]${NC} Thiếu file snippet: ${src}"
        exit 1
    fi
}

# 1. Append snippets
echo -e "\n${BLUE}[1] Cập nhật Biến Môi Trường và Database...${NC}"
append_snippet "${THEME_SRC}/env.joyfuld.snippet" "${DEST_DIR}/.joyfuld" "Môi trường .joyfuld"
mkdir -p "${DEST_DIR}/.config/openbox/joyful-desktop"
touch "${DEST_DIR}/.config/openbox/joyful-desktop/db.theme.joy"
append_snippet "${THEME_SRC}/db.theme.joy.snippet" "${DEST_DIR}/.config/openbox/joyful-desktop/db.theme.joy" "Database db.theme.joy"

# Lấy tên GTK để đặt thư mục Openbox cho đúng (Vì .joyfuld khai báo NORD_GTK='Nordic')
GTK_NAME=$(grep -oP "(?<=^${PREFIX_T}_GTK=')[^']*" "${THEME_SRC}/env.joyfuld.snippet" || echo "${THEME_NAME}")

# 2. Copy Openbox/GTK theme
echo -e "\n${BLUE}[2] Cập nhật cấu trúc Openbox...${NC}"
copy_file "${THEME_SRC}/openbox/themerc" "${DEST_DIR}/.themes/${GTK_NAME}/openbox-3/themerc" "Openbox themerc"

# 3. Copy Rofi
echo -e "\n${BLUE}[3] Cập nhật Rofi...${NC}"
copy_file "${THEME_SRC}/rofi/colorscheme.rasi" "${DEST_DIR}/.config/rofi/themes/colorschemes/${THEME_NAME}.rasi" "Rofi Colorscheme"

# 4. Copy Dunst
echo -e "\n${BLUE}[4] Cập nhật Dunst...${NC}"
copy_file "${THEME_SRC}/dunst/artistic.dunstrc" "${DEST_DIR}/.config/dunst/${THEME_NAME}.artistic.dunstrc" "Dunst Artistic"
copy_file "${THEME_SRC}/dunst/interactive.dunstrc" "${DEST_DIR}/.config/dunst/${THEME_NAME}.interactive.dunstrc" "Dunst Interactive"

# 5. Copy Tint2
echo -e "\n${BLUE}[5] Cập nhật Tint2...${NC}"
copy_file "${THEME_SRC}/tint2/top.interactive.tint2rc" "${DEST_DIR}/.config/tint2/${THEME_NAME}-top.interactive.tint2rc" "Tint2 Top"
copy_file "${THEME_SRC}/tint2/horizontal.artistic.tint2rc" "${DEST_DIR}/.config/tint2/${THEME_NAME}-horizontal.artistic.tint2rc" "Tint2 Horizontal"
copy_file "${THEME_SRC}/tint2/vertical.artistic.tint2rc" "${DEST_DIR}/.config/tint2/${THEME_NAME}-vertical.artistic.tint2rc" "Tint2 Vertical"

# 6. Copy Notification Icons
echo -e "\n${BLUE}[6] Cập nhật Notification Icons...${NC}"
copy_file "${THEME_SRC}/icons/artistic.png" "${DEST_DIR}/.icons/Gladient/${THEME_NAME}.artistic.png" "Icon Artistic"
copy_file "${THEME_SRC}/icons/interactive.png" "${DEST_DIR}/.icons/Gladient/${THEME_NAME}.interactive.png" "Icon Interactive"

# 7. Copy Wallpapers
echo -e "\n${BLUE}[7] Cập nhật Wallpapers...${NC}"
copy_file "${THEME_SRC}/wallpapers/artistic.jpg" "${DEST_DIR}/.wallpapers/${THEME_NAME}/${THEME_NAME}.artistic.jpg" "Wallpaper Artistic"
copy_file "${THEME_SRC}/wallpapers/interactive.jpg" "${DEST_DIR}/.wallpapers/${THEME_NAME}/${THEME_NAME}.interactive.jpg" "Wallpaper Interactive"

echo -e "\n${BLUE}══════════════════════════════════════════════════${NC}"
if [[ $APPLY_MODE -eq 0 ]]; then
    echo -e "${GREEN}MOCK IMPORT HOÀN TẤT.${NC}"
    echo -e "Bạn có thể kiểm tra kết quả tại thư mục: ${YELLOW}${DEST_DIR}${NC}"
    echo -e "Để xác minh mock, hãy chạy: ${GREEN}./joyful-tester.sh dry-run ${THEME_NAME}${NC} (Sửa script tester để trỏ vào thư mục mock nếu cần)"
else
    echo -e "${GREEN}NHẬP THEME HOÀN TẤT THÀNH CÔNG!${NC}"
    echo -e "Vui lòng chạy ${GREEN}./joyful-tester.sh check ${THEME_NAME}${NC} để kiểm tra tính toàn vẹn hệ thống."
fi
