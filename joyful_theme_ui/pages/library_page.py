import os
import re
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from joyful_theme_lib import JoyfulThemeLib
from ..utils import create_scaled_image, add_color_chip_to_box

class LibraryPage(Gtk.Box):
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.app = app
        
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        sidebar.get_style_context().add_class("card")
        sidebar.set_size_request(250, -1)
        sidebar.set_margin_top(10)
        sidebar.set_margin_bottom(10)
        sidebar.set_margin_start(10)
        sidebar.set_margin_end(10)
        
        sidebar_label = Gtk.Label(label="System Themes")
        sidebar_label.get_style_context().add_class("h3")
        sidebar.pack_start(sidebar_label, False, False, 0)
        
        scrolled_list = Gtk.ScrolledWindow()
        self.theme_listbox = Gtk.ListBox()
        self.theme_listbox.connect("row-selected", self.on_theme_selected)
        scrolled_list.add(self.theme_listbox)
        sidebar.pack_start(scrolled_list, True, True, 0)
        
        refresh_btn = Gtk.Button(label="Refresh List")
        refresh_btn.connect("clicked", lambda x: self.load_system_themes())
        sidebar.pack_start(refresh_btn, False, False, 0)
        
        self.pack_start(sidebar, False, False, 0)
        
        self.detail_view = Gtk.ScrolledWindow()
        self.detail_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.detail_box.set_border_width(20)
        self.detail_view.add(self.detail_box)
        
        placeholder = Gtk.Label()
        placeholder.set_markup("<span size='large' color='#89b4fa'><b>Select a theme</b></span>\n\nChoose a theme from the sidebar to view its details and health status.")
        placeholder.set_justify(Gtk.Justification.CENTER)
        placeholder.set_margin_top(100)
        self.detail_box.pack_start(placeholder, True, True, 0)
        
        self.pack_start(self.detail_view, True, True, 0)
        
        self.load_system_themes()

    def load_system_themes(self):
        for child in self.theme_listbox.get_children():
            self.theme_listbox.remove(child)
            
        themes_path = os.path.join(self.app.script_dir, ".config/rofi/themes/colorschemes")
        if os.path.exists(themes_path):
            files = sorted(os.listdir(themes_path))
            for f in files:
                if f.endswith(".rasi"):
                    name = f.replace(".rasi", "")
                    row = Gtk.ListBoxRow()
                    row.get_style_context().add_class("list-row")
                    label = Gtk.Label(label=name, xalign=0)
                    row.add(label)
                    self.theme_listbox.add(row)
        
        self.theme_listbox.show_all()

    def on_theme_selected(self, listbox, row):
        if not row:
            return
        theme_name = row.get_child().get_text()
        self.show_theme_details(theme_name)

    def show_theme_details(self, theme_name):
        for child in self.detail_box.get_children():
            self.detail_box.remove(child)

        db_config = JoyfulThemeLib.get_db_config(self.app.script_dir, theme_name)
        art_wall_file = db_config['artistic_wallpaper']
        int_wall_file = db_config['interactive_wallpaper']
            
        title = Gtk.Label(label=f"Theme: {theme_name}")
        title.get_style_context().add_class("main-title")
        self.detail_box.pack_start(title, False, False, 0)
        
        health_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        health_box.get_style_context().add_class("card")
        health_box.set_margin_bottom(10)
        
        health_title = Gtk.Label(label="System Health Status")
        health_title.set_halign(Gtk.Align.START)
        health_title.get_style_context().add_class("preview-title")
        health_box.pack_start(health_title, False, False, 5)
        
        files_to_check = {
            "Rofi (.rasi)": os.path.join(self.app.script_dir, f".config/rofi/themes/colorschemes/{theme_name}.rasi"),
            "Dunst (.dunstrc)": os.path.join(self.app.script_dir, f".config/dunst/{theme_name}.artistic.dunstrc"),
            "Tint2 (.tint2rc)": os.path.join(self.app.script_dir, f".config/tint2/{theme_name}-top.interactive.tint2rc"),
            "Wallpaper (.jpg)": os.path.join(self.app.script_dir, f".wallpapers/{theme_name}/{art_wall_file}"),
        }
        
        for desc, path in files_to_check.items():
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            exists = os.path.exists(path)
            icon_name = "emblem-ok-symbolic" if exists else "dialog-error-symbolic"
            color = "#a6e3a1" if exists else "#f38ba8"
            
            icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU)
            lbl = Gtk.Label(label=desc)
            lbl_status = Gtk.Label()
            lbl_status.set_markup(f"<span color='{color}'>{'OK' if exists else 'Missing'}</span>")
            
            row.pack_start(icon, False, False, 0)
            row.pack_start(lbl, False, False, 0)
            row.pack_end(lbl_status, False, False, 0)
            health_box.pack_start(row, False, False, 2)
            
        self.detail_box.pack_start(health_box, False, False, 0)        
        
        img_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        
        art_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        art_box.pack_start(Gtk.Label(label="Artistic Mode"), False, False, 0)
        art_wall = os.path.join(self.app.script_dir, f".wallpapers/{theme_name}/{art_wall_file}")
        art_img = create_scaled_image(art_wall, 250, 150)
        art_box.pack_start(art_img, False, False, 0)
        
        art_icon_path = os.path.join(self.app.script_dir, f".icons/Gladient/{theme_name}.artistic.png")
        art_icon = create_scaled_image(art_icon_path, 48, 48)
        art_box.pack_start(art_icon, False, False, 0)
        
        img_hbox.pack_start(art_box, True, True, 0)
        
        int_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        int_box.pack_start(Gtk.Label(label="Interactive Mode"), False, False, 0)
        int_wall = os.path.join(self.app.script_dir, f".wallpapers/{theme_name}/{int_wall_file}")
        int_img = create_scaled_image(int_wall, 250, 150)
        int_box.pack_start(int_img, False, False, 0)
        
        int_icon_path = os.path.join(self.app.script_dir, f".icons/Gladient/{theme_name}.interactive.png")
        int_icon = create_scaled_image(int_icon_path, 48, 48)
        int_box.pack_start(int_icon, False, False, 0)
        
        img_hbox.pack_start(int_box, True, True, 0)
        
        self.detail_box.pack_start(img_hbox, False, False, 0)
        
        palette_label = Gtk.Label(label="System Palette (.joyfuld):")
        palette_label.set_halign(Gtk.Align.START)
        self.detail_box.pack_start(palette_label, False, False, 0)
        
        p_flow = Gtk.FlowBox()
        p_flow.set_max_children_per_line(10)
        p_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        
        self.extract_system_colors(theme_name, p_flow)
        self.detail_box.pack_start(p_flow, False, False, 0)
        
        config_btn = Gtk.Button(label="Show Raw Config Snippet")
        config_btn.get_style_context().add_class("secondary")
        config_btn.connect("clicked", lambda x: self.show_raw_config(theme_name))
        self.detail_box.pack_start(config_btn, False, False, 0)
        
        self.detail_box.show_all()

    def extract_system_colors(self, theme_name, flowbox):
        prefix = JoyfulThemeLib.get_prefix(theme_name)
        joyfuld_path = os.path.join(self.app.script_dir, ".joyfuld")
        colors = JoyfulThemeLib.extract_colors_from_snippet(joyfuld_path, prefix)
        
        if not colors:
            rofi_path = os.path.join(self.app.script_dir, f".config/rofi/themes/colorschemes/{theme_name}.rasi")
            colors = JoyfulThemeLib.extract_colors_from_snippet(rofi_path)
            
        for color in colors:
            add_color_chip_to_box(color, flowbox)

    def show_raw_config(self, theme_name):
        prefix = JoyfulThemeLib.get_prefix(theme_name)
        joyfuld_path = os.path.join(self.app.script_dir, ".joyfuld")
        db_path = os.path.join(self.app.script_dir, ".config/openbox/joyful-desktop/db.theme.joy")
        
        config_text = f"# --- [1] Environment Variables (.joyfuld) --- #\n"
        config_text += f"# Prefix: {prefix}\n\n"
        
        if os.path.exists(joyfuld_path):
            with open(joyfuld_path, 'r') as f:
                for line in f:
                    if re.match(rf"^{prefix}_", line):
                        config_text += line
        
        config_text += f"\n# --- [2] Database Settings (db.theme.joy) --- #\n"
        config_text += f"# Theme: {theme_name}\n\n"
        
        if os.path.exists(db_path):
            with open(db_path, 'r') as f:
                for line in f:
                    if f".{theme_name}." in line:
                        config_text += line
        
        dialog = Gtk.Dialog(title=f"Config Snippet: {theme_name}", parent=self.app)
        dialog.set_default_size(900, 600)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        text_view = Gtk.TextView()
        text_view.set_editable(False)
        text_view.set_cursor_visible(False)
        text_view.set_wrap_mode(Gtk.WrapMode.NONE)
        
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"textview { font-family: monospace; font-size: 10pt; }")
        text_view.get_style_context().add_provider(
            css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        text_view.set_left_margin(15)
        text_view.set_right_margin(15)
        text_view.set_top_margin(15)
        text_view.set_bottom_margin(15)
        
        text_view.get_buffer().set_text(config_text)
        scrolled.add(text_view)
        
        dialog.get_content_area().add(scrolled)
        dialog.add_button("Close", Gtk.ResponseType.CLOSE)
        dialog.show_all()
        dialog.run()
        dialog.destroy()
