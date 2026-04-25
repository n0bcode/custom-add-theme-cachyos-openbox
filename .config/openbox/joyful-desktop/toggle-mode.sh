#!/usr/bin/env sh

# Desc:   Toggle or apply theme and/or mode.
# Author: Harry Kurn <alternate-se7en@pm.me>
# URL:    https://github.com/owl4ce/dotfiles/tree/ng/.config/openbox/joyful-desktop/toggle-mode.sh

# SPDX-License-Identifier: ISC

# shellcheck disable=SC3044

SYSTEM_LANG="$LANG"
export LANG='POSIX'
exec >/dev/null 2>&1
. "${HOME}/.joyfuld"

killall tint2 dunst -q &

# https://gnu.org/software/bash/manual/html_node/The-Shopt-Builtin.html#:~:text=expand_aliases
[ -z "$BASH" ] || shopt -s expand_aliases

setup_ui()
{
    sed -e "/^current_theme[ ]*/s|\"[a-zA-Z0-9_-]*\"$|\"${1}\"|" \
        -e "/^current_mode[ ]*/s|\"[a-zA-Z0-9_-]*\"$|\"${2}\"|" \
        -i "$MODE_FILE"

    joyd_theme_set

    JOYD_TERMINAL_SET_ARGS="${3%%_*}" LANG="$SYSTEM_LANG" \
    joyd_user_interface_set

    case "${1}" in
        mech*) BODY='Mechanical Theme'
        ;;
        eyec*) BODY='EyeCandy Theme'
        ;;
        nord*) BODY='Nordic Theme'
        ;;
        *)     # Capitalize first letter of custom theme
               BODY="$(echo "${1}" | sed 's/./\u&/') Theme"
        ;;
    esac

    case "${2}" in
        art*) SUMMARY='Artistic Mode'
        ;;
        int*) SUMMARY='Interactive Mode'
        ;;
    esac

    dunstify "$SUMMARY" "$BODY" -h string:synchronous:toggle-mode \
                                -a joyful_desktop \
                                -i "${GLADIENT_ICON_DIR}/${1}.${2}.png" \
                                -u low
}

case "${1}" in
    '') joyd_tray_programs kill

        # Dynamic theme list from rofi colorschemes
        THEMES_DIR="${HOME}/.config/rofi/themes/colorschemes"
        THEME_LIST="$(ls "$THEMES_DIR" | sed 's/\.rasi//g' | tr '\n' ' ')"
        
        # Determine next theme in the sequence
        NEXT_THEME=$(echo "$THEME_LIST" | awk -v current="$CHK_THEME" '{
            for (i=1; i<=NF; i++) {
                if ($i == current) {
                    print (i==NF ? $1 : $(i+1));
                    exit;
                }
            }
            print $1;
        }')
        
        setup_ui "$NEXT_THEME" "$CHK_MODE" reverse_terminal_bg_fg

        LANG="$SYSTEM_LANG" joyd_tray_programs exec
    ;;
    m*) for M in artistic interactive; do
            [ "$CHK_MODE" != "$M" ] || continue
            setup_ui "$CHK_THEME" "$M"
            break
        done
    ;;
    a*) LANG="$SYSTEM_LANG" joyd_user_interface_set
    ;;
esac

exit ${?}
