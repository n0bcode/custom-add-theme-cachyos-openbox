#!/usr/bin/env sh

# Desc:   Show a Rofi popup to pick and apply a Joyful Desktop theme.
# Usage:  theme-select.sh
# Author: Joyful Desktop (CachyOS fork)

# SPDX-License-Identifier: ISC

# shellcheck disable=SC3044

SYSTEM_LANG="$LANG"
export LANG='POSIX'
exec >/dev/null 2>&1
. "${HOME}/.joyfuld"

# https://gnu.org/software/bash/manual/html_node/The-Shopt-Builtin.html#:~:text=expand_aliases
[ -z "$BASH" ] || shopt -s expand_aliases

# Build a newline-separated list of available themes from Rofi colorschemes.
# Each .rasi file in the colorschemes dir represents one registered theme.
THEME_LIST="$(for F in "${ROFI_COLORSCHEMES_DIR}"/*.rasi; do
    [ -f "$F" ] || continue
    echo "${F##*/}" | sed 's/\.rasi$//'
done)"

[ -n "$THEME_LIST" ] || exit 1

# Show Rofi picker — highlight the currently active theme via -mesg.
SELECTED="$(printf '%s\n' "$THEME_LIST" \
    | rofi -theme-str '@import "action.rasi"' \
           -no-show-icons \
           -no-lazy-grab \
           -no-plugins \
           -dmenu \
           -mesg "Current theme: ${CHK_THEME}  |  Mode: ${CHK_MODE}" \
           -p 'Select Theme')"

# Bail out if the user cancelled (empty selection or same theme).
[ -n "$SELECTED" ]            || exit 0
[ "$SELECTED" != "$CHK_THEME" ] || exit 0

killall tint2 dunst -q &

sed -e "/^current_theme[ ]*/s|\"[a-zA-Z0-9_-]*\"$|\"${SELECTED}\"|" \
    -i "$MODE_FILE"

joyd_theme_set

JOYD_TERMINAL_SET_ARGS="${CHK_MODE%%_*}" LANG="$SYSTEM_LANG" \
joyd_user_interface_set

# Compose notification body — use friendly names for built-in themes,
# capitalize first letter for custom ones.
case "$SELECTED" in
    mech*) BODY='Mechanical Theme' ;;
    eyec*) BODY='EyeCandy Theme'   ;;
    nord*) BODY='Nordic Theme'     ;;
    *)     BODY="$(printf '%s' "$SELECTED" | sed 's/^./\u&/') Theme" ;;
esac

case "$CHK_MODE" in
    art*) SUMMARY='Artistic Mode'     ;;
    int*) SUMMARY='Interactive Mode'  ;;
    *)    SUMMARY="$CHK_MODE"         ;;
esac

dunstify "$SUMMARY" "$BODY" \
         -h string:synchronous:toggle-mode \
         -a joyful_desktop \
         -i "${GLADIENT_ICON_DIR}/${SELECTED}.${CHK_MODE}.png" \
         -u low

LANG="$SYSTEM_LANG" joyd_tray_programs exec

exit ${?}
