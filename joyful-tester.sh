#!/usr/bin/env bash
# ─────────────────────────────────────────────
# joyful-tester.sh — CachyOS Joyful Desktop Multi-tool
# Mục đích: Quản lý, kiểm tra Asset và Dry-run mô phỏng quá trình
# chuyển theme mà không làm ảnh hưởng hệ thống đang chạy.
# Mở rộng: Rà soát tài nguyên hệ thống (Theme, Font, Icon)
# ─────────────────────────────────────────────

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_help() {
    echo -e "${BLUE}══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}    JOYFUL DESKTOP THEME TESTER (MULTI-TOOL)      ${NC}"
    echo -e "${BLUE}══════════════════════════════════════════════════${NC}"
    echo "Sử dụng: $0 [COMMAND] [THEME_NAME]"
    echo ""
    echo "Commands:"
    echo "  --help, -h       Hiển thị menu trợ giúp này"
    echo "  list             Danh sách các theme Joyful hiện có"
    echo "  check <theme>    Kiểm tra tính toàn vẹn (Asset/File/Màu sắc/Biến môi trường) của 1 theme"
    echo "  dry-run <theme>  Chạy mô phỏng (Mock) quá trình patch cấu hình bằng sed"
    echo "                   để đảm bảo file cấu hình không bị sai format"
    echo "                   (Hoàn toàn an toàn, KHÔNG tác động hệ thống)"
    echo "  scan-fonts       Liệt kê các font chữ UI / Nerd Fonts đã được cài đặt"
    echo "  scan-icons       Liệt kê các bộ Icon theme hiện có trong hệ thống"
    echo "  scan-gtk         Liệt kê các GTK theme hiện có trong hệ thống"
    echo ""
    echo "Examples:"
    echo "  $0 list"
    echo "  $0 check nordic"
    echo "  $0 dry-run nordic"
    echo "  $0 scan-fonts"
    echo -e "${BLUE}══════════════════════════════════════════════════${NC}"
}

list_themes() {
    echo -e "${BLUE}[*] Available Themes (detected from Rofi colorschemes):${NC}"
    if [[ -d "$SCRIPT_DIR/.config/rofi/themes/colorschemes" ]]; then
        for f in "$SCRIPT_DIR/.config/rofi/themes/colorschemes/"*.rasi; do
            theme_name=$(basename "$f" .rasi)
            echo "  - $theme_name"
        done
    else
        echo -e "${RED}[✗] Cannot find themes directory.${NC}"
    fi
}

scan_fonts() {
    echo -e "${BLUE}[*] Scanning system fonts (Nerd Fonts & common UI fonts)...${NC}"
    if command -v fc-list >/dev/null 2>&1; then
        fc-list : family | grep -iE "nerd|jetbrains|fira|hack|cantarell|comfortaa|awesome" | sort -u | while read -r font; do
            echo "  - $font"
        done
        echo -e "${YELLOW}(Lưu ý: Chỉ liệt kê các font UI phổ biến và Nerd Fonts. Dùng 'fc-list' để xem tất cả)${NC}"
    else
        echo -e "${RED}[✗] 'fc-list' command not found. Cannot scan fonts.${NC}"
    fi
}

scan_icons() {
    echo -e "${BLUE}[*] Scanning available Icon themes...${NC}"
    for dir in "$HOME/.icons" "$HOME/.local/share/icons" "/usr/share/icons"; do
        if [[ -d "$dir" ]]; then
            echo -e "${GREEN}>> Thư mục: $dir${NC}"
            find "$dir" -mindepth 1 -maxdepth 1 -type d | sort | while read -r icon; do
                if [[ -f "$icon/index.theme" ]]; then
                    echo "  - $(basename "$icon")"
                fi
            done
        fi
    done
}

scan_gtk() {
    echo -e "${BLUE}[*] Scanning available GTK themes...${NC}"
    for dir in "$HOME/.themes" "$HOME/.local/share/themes" "/usr/share/themes"; do
        if [[ -d "$dir" ]]; then
            echo -e "${GREEN}>> Thư mục: $dir${NC}"
            find "$dir" -mindepth 1 -maxdepth 1 -type d | sort | while read -r theme; do
                if [[ -d "$theme/gtk-3.0" || -d "$theme/gtk-2.0" ]]; then
                    echo "  - $(basename "$theme")"
                fi
            done
        fi
    done
}

check_theme() {
    local THEME_NAME="$1"
    local ERRORS=0
    local WARNINGS=0

    echo -e "${BLUE}══════════════════════════════════════════════════${NC}"
    echo -e "Đang kiểm tra Cấu trúc & Biến cho theme: ${GREEN}${THEME_NAME}${NC}"
    
    check_file() {
        local file_path="$1"
        local desc="$2"
        if [[ -f "$file_path" ]]; then
            echo -e "  ${GREEN}[✓]${NC} ${desc}: $(basename "$file_path")"
        else
            echo -e "  ${RED}[✗]${NC} Thiếu file: ${file_path}"
            ERRORS=$((ERRORS + 1))
        fi
    }

    check_content() {
        local file_path="$1"
        local pattern="$2"
        local desc="$3"
        if [[ -f "$file_path" ]] && grep -qiE "$pattern" "$file_path"; then
            echo -e "  ${GREEN}[✓]${NC} ${desc}: '${pattern}'"
        else
            echo -e "  ${RED}[✗]${NC} ${desc}: Lỗi thiếu biến '${pattern}' trong $(basename "$file_path")"
            ERRORS=$((ERRORS + 1))
        fi
    }

    UCTM=$(echo "$THEME_NAME" | tr '[:lower:]' '[:upper:]')
    PREFIX_T="${UCTM:0:4}"

    echo -e "\n${BLUE}[1] Kiểm tra Biến Môi Trường Joyful (.joyfuld)...${NC}"
    JOYFULD="${SCRIPT_DIR}/.joyfuld"
    
    echo "  >> General Configs:"
    check_content "$JOYFULD" "^${PREFIX_T}_GTK=" "GTK Theme"
    check_content "$JOYFULD" "^${PREFIX_T}_ICON=" "Icon Theme"
    check_content "$JOYFULD" "^${PREFIX_T}_OB_THEME_DIR=" "Openbox Theme Dir"
    
    for mode in "ART" "INT"; do
        echo "  >> Mode: ${mode} (Artistic/Interactive):"
        check_content "$JOYFULD" "^${PREFIX_T}_${mode}_OB_MENU_ITM=" "Openbox Menu Item Color"
        check_content "$JOYFULD" "^${PREFIX_T}_${mode}_OB_MENU_TTL=" "Openbox Menu Title Color"
        check_content "$JOYFULD" "^${PREFIX_T}_${mode}_ROFI_ACCNT1=" "Rofi Accent 1"
        check_content "$JOYFULD" "^${PREFIX_T}_${mode}_ROFI_ACCNT2=" "Rofi Accent 2"
        check_content "$JOYFULD" "^${PREFIX_T}_${mode}_DUNST_SMMRY=" "Dunst Summary Color"
        check_content "$JOYFULD" "^${PREFIX_T}_${mode}_DUNST_PRGBR=" "Dunst Progress Bar Color"
        if grep -qE "^${PREFIX_T}_${mode}_TINT2_GRAD" "$JOYFULD"; then
            echo -e "  ${GREEN}[✓]${NC} Tìm thấy biến TINT2 GRAD cho ${mode}"
        else
            echo -e "  ${YELLOW}[!]${NC} Thiếu biến TINT2_GRAD1/2 cho mode ${mode}. Script fallback?"
        fi
    done

    echo -e "\n${BLUE}[1.b] Kiểm tra Database config (db.theme.joy)...${NC}"
    DB_THEME="${SCRIPT_DIR}/.config/openbox/joyful-desktop/db.theme.joy"
    for mode in "artistic" "interactive"; do
        check_content "$DB_THEME" "^ob_button_style\.${THEME_NAME}\.${mode}" "OB Button Style ($mode)"
        check_content "$DB_THEME" "^ob_button_location\.${THEME_NAME}\.${mode}" "OB Button Location ($mode)"
        check_content "$DB_THEME" "^wallpaper\.${THEME_NAME}\.${mode}" "Wallpaper ($mode)"
    done

    echo -e "\n${BLUE}[2] Kiểm tra Rofi files...${NC}"
    check_file "${SCRIPT_DIR}/.config/rofi/themes/colorschemes/${THEME_NAME}.rasi" "Rofi Colorscheme"

    echo -e "\n${BLUE}[3] Kiểm tra Dunst files...${NC}"
    check_file "${SCRIPT_DIR}/.config/dunst/${THEME_NAME}.artistic.dunstrc" "Dunst Artistic"
    check_file "${SCRIPT_DIR}/.config/dunst/${THEME_NAME}.interactive.dunstrc" "Dunst Interactive"

    echo -e "\n${BLUE}[4] Kiểm tra Tint2 files...${NC}"
    check_file "${SCRIPT_DIR}/.config/tint2/${THEME_NAME}-top.interactive.tint2rc" "Tint2 Top Interactive"
    check_file "${SCRIPT_DIR}/.config/tint2/${THEME_NAME}-horizontal.artistic.tint2rc" "Tint2 Horizontal Artistic"
    check_file "${SCRIPT_DIR}/.config/tint2/${THEME_NAME}-vertical.artistic.tint2rc" "Tint2 Vertical Artistic"

    echo -e "\n${BLUE}[5] Kiểm tra Notification Icons...${NC}"
    check_file "${SCRIPT_DIR}/.icons/Gladient/${THEME_NAME}.artistic.png" "Icon Artistic Mode"
    check_file "${SCRIPT_DIR}/.icons/Gladient/${THEME_NAME}.interactive.png" "Icon Interactive Mode"

    echo -e "\n${BLUE}══════════════════════════════════════════════════${NC}"
    if [[ $ERRORS -eq 0 ]]; then
        echo -e "${GREEN}✓ Hoàn hảo! Theme chuẩn cấu trúc mã nguồn của script Joyful (Errors: 0)${NC}"
    else
        echo -e "${RED}✗ Thất bại! Tìm thấy ${ERRORS} lỗi thiếu biến/file (Điều này có thể làm crash script switch theme).${NC}"
        exit 1
    fi
}

dry_run_theme() {
    local THEME_NAME="$1"
    echo -e "${BLUE}══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}    JOYFUL DESKTOP ARCHITECTURE DRY-RUN TEST      ${NC}"
    echo -e "Theme Test: ${GREEN}${THEME_NAME}${NC}"
    echo -e "${BLUE}══════════════════════════════════════════════════${NC}"

    MOCK_DIR="${SCRIPT_DIR}/mock-joyful-test"
    echo "[*] Creating isolated mock environment at: mock-joyful-test/"
    rm -rf "$MOCK_DIR"
    mkdir -p "$MOCK_DIR/.config/openbox/joyful-desktop"
    mkdir -p "$MOCK_DIR/.config/openbox"
    
    if [[ -f "$SCRIPT_DIR/.config/openbox/rc.xml" ]]; then
        cp "$SCRIPT_DIR/.config/openbox/rc.xml" "$MOCK_DIR/.config/openbox/rc.xml"
    elif [[ -f "$SCRIPT_DIR/test-openbox-config/openbox/rc.xml" ]]; then
        cp "$SCRIPT_DIR/test-openbox-config/openbox/rc.xml" "$MOCK_DIR/.config/openbox/rc.xml"
    fi

    if [[ -f "$SCRIPT_DIR/.config/openbox/joyful-desktop/themerc" ]]; then
        cp "$SCRIPT_DIR/.config/openbox/joyful-desktop/themerc" "$MOCK_DIR/.config/openbox/joyful-desktop/themerc"
    elif [[ -f "$SCRIPT_DIR/test-openbox-config/openbox/themes/${THEME_NAME}/openbox/themerc" ]]; then
        cp "$SCRIPT_DIR/test-openbox-config/openbox/themes/${THEME_NAME}/openbox/themerc" "$MOCK_DIR/.config/openbox/joyful-desktop/themerc"
    fi
    
    echo "[*] Simulating Joyful Desktop Theme Switch Process..."

    echo -e "\n${YELLOW}--- Phase 1: theme-set.sh (Structure & Assets) ---${NC}"
    RC_XML_MOCK="$MOCK_DIR/.config/openbox/rc.xml"
    if [[ -f "$RC_XML_MOCK" ]]; then
        echo "[Test] Patching rc.xml <theme><name> bằng sed..."
        sed -i "s|<name>.*</name>|<name>${THEME_NAME}</name>|g" "$RC_XML_MOCK"
        if grep -q "<name>${THEME_NAME}</name>" "$RC_XML_MOCK"; then
            echo -e "${GREEN}[✓] rc.xml cấu trúc tương thích, đổi theme thành '${THEME_NAME}' thành công.${NC}"
        else
            echo -e "${RED}[✗] Lỗi: rc.xml cấu trúc thẻ <theme><name> không hợp lệ để sed patch.${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}[!] Không tìm thấy rc.xml để test mock.${NC}"
    fi

    echo -e "\n${YELLOW}--- Phase 2: user-interface-set.sh (Color Injection) ---${NC}"
    THEMERC_MOCK="$MOCK_DIR/.config/openbox/joyful-desktop/themerc"
    if [[ -f "$THEMERC_MOCK" ]]; then
        MOCK_BG_COLOR="#123456"
        echo "[Test] Ghi đè mã màu HEX ngẫu nhiên (${MOCK_BG_COLOR}) vào themerc..."
        sed -i "s|window.active.title.bg.color:.*|window.active.title.bg.color: ${MOCK_BG_COLOR}|g" "$THEMERC_MOCK"
        if grep -q "window.active.title.bg.color: ${MOCK_BG_COLOR}" "$THEMERC_MOCK"; then
            echo -e "${GREEN}[✓] themerc đã cập nhật màu nền bằng sed patch thành công.${NC}"
        else
            echo -e "${RED}[✗] Lỗi: themerc cấu trúc key 'window.active.title.bg.color:' không hợp lệ để sed patch.${NC}"
        fi
    else
        echo -e "${YELLOW}[!] Không tìm thấy themerc để test mock.${NC}"
    fi

    echo -e "\n${BLUE}══════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}MOCK TEST HOÀN TẤT.${NC} (Không có tiến trình thật nào bị tác động)"
    rm -rf "$MOCK_DIR"
}

if [[ $# -eq 0 ]]; then
    show_help
    exit 0
fi

COMMAND="$1"
shift

case "$COMMAND" in
    --help|-h)
        show_help
        ;;
    list)
        list_themes
        ;;
    check)
        if [[ $# -eq 0 ]]; then
            echo -e "${RED}[!] Missing theme name for check. Usage: $0 check <theme>${NC}"
            exit 1
        fi
        check_theme "$1"
        ;;
    dry-run)
        if [[ $# -eq 0 ]]; then
            echo -e "${RED}[!] Missing theme name for dry-run. Usage: $0 dry-run <theme>${NC}"
            exit 1
        fi
        dry_run_theme "$1"
        ;;
    scan-gtk)
        scan_gtk
        ;;
    scan-icons)
        scan_icons
        ;;
    scan-fonts)
        scan_fonts
        ;;
    *)
        echo -e "${RED}[✗] Unknown command: $COMMAND${NC}"
        show_help
        exit 1
        ;;
esac