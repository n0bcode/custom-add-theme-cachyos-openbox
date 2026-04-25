import os
import re
import json
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from joyful_theme_lib import JoyfulThemeLib, ThemeGenerator
from ..dialogs import show_error_dialog, show_info_dialog, show_config_dialog, import_ai_config_dialog

class CreatorPage(Gtk.ScrolledWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        vbox.set_border_width(10)
        self.add(vbox)
        
        title_label = Gtk.Label(label="Joyful Theme Creator")
        title_label.get_style_context().add_class("main-title")
        vbox.pack_start(title_label, False, False, 0)

        # 0. AI Integration Bridge Card
        card_ai = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        card_ai.get_style_context().add_class("card")
        
        ai_title = Gtk.Label(label="AI Integration Bridge")
        ai_title.get_style_context().add_class("h3")
        card_ai.pack_start(ai_title, False, False, 5)
        
        ai_desc = Gtk.Label(label="Use AI to generate your theme configuration. Export a system-aware template and import the result.")
        ai_desc.set_line_wrap(True)
        ai_desc.set_xalign(0)
        card_ai.pack_start(ai_desc, False, False, 0)
        
        ai_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        btn_get_template = Gtk.Button(label="Get AI Prompt Template")
        btn_get_template.connect("clicked", self.on_get_ai_template_clicked)
        ai_hbox.pack_start(btn_get_template, True, True, 0)
        
        btn_import_config = Gtk.Button(label="Import Configuration (JSON)")
        btn_import_config.connect("clicked", lambda w: import_ai_config_dialog(self.app, self.apply_config_data))
        ai_hbox.pack_start(btn_import_config, True, True, 0)
        
        card_ai.pack_start(ai_hbox, False, False, 0)
        vbox.pack_start(card_ai, False, False, 0)

        # 1. Identity & Misc Card
        card_identity = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        card_identity.get_style_context().add_class("card")
        
        self.new_theme_name_entry = Gtk.Entry()
        self.new_theme_name_entry.set_placeholder_text("e.g. catppuccin-dream")
        self.create_form_row(card_identity, "Theme Name:", self.new_theme_name_entry)
        
        self.new_gtk_combo = Gtk.ComboBoxText.new_with_entry()
        self.create_form_row(card_identity, "GTK Theme:", self.new_gtk_combo)
        
        self.new_icon_combo = Gtk.ComboBoxText.new_with_entry()
        self.create_form_row(card_identity, "Icon Theme:", self.new_icon_combo)
        
        self.new_font_combo = Gtk.ComboBoxText.new_with_entry()
        self.create_form_row(card_identity, "System Font:", self.new_font_combo)
        
        self.new_tint2_glyph = Gtk.Entry()
        self.new_tint2_glyph.set_text("")
        self.create_form_row(card_identity, "Menu Glyph:", self.new_tint2_glyph)
        
        vbox.pack_start(card_identity, False, False, 0)

        # 2. Window Decoration Card
        card_decor = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        card_decor.get_style_context().add_class("card")
        
        decor_title = Gtk.Label(label="Window Decoration (Openbox)")
        decor_title.get_style_context().add_class("h3")
        card_decor.pack_start(decor_title, False, False, 5)
        
        self.new_btn_style_art = Gtk.ComboBoxText.new_with_entry()
        for s in ["circles-filled", "circles-outline", "dots", "lines", "nav", "lovely", "backslash"]:
            self.new_btn_style_art.append_text(s)
        self.new_btn_style_art.set_active(0)
        self.create_form_row(card_decor, "Artistic Button Style:", self.new_btn_style_art)
        
        self.new_btn_loc_art = Gtk.Entry()
        self.new_btn_loc_art.set_text("left")
        self.create_form_row(card_decor, "Artistic Location:", self.new_btn_loc_art)
        
        self.new_btn_style_int = Gtk.ComboBoxText.new_with_entry()
        for s in ["circles-filled", "circles-outline", "dots", "lines", "nav", "lovely", "backslash"]:
            self.new_btn_style_int.append_text(s)
        self.new_btn_style_int.set_active(1)
        self.create_form_row(card_decor, "Interactive Button Style:", self.new_btn_style_int)
        
        self.new_btn_loc_int = Gtk.Entry()
        self.new_btn_loc_int.set_text("right")
        self.create_form_row(card_decor, "Interactive Location:", self.new_btn_loc_int)
        
        vbox.pack_start(card_decor, False, False, 0)

        # Populate Combos
        self.populate_creator_combos()

        # 3. Artistic Palette Card
        card_colors_art = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        card_colors_art.get_style_context().add_class("card")
        
        colors_title = Gtk.Label(label="Theme Palette (Artistic Mode)")
        colors_title.get_style_context().add_class("h3")
        card_colors_art.pack_start(colors_title, False, False, 5)
        
        self.color_pickers_art = {}
        vars_art = [
            ("THEM_ART_TINT2_GRAD1", "Main Accent (Tint2/Rofi)"),
            ("THEM_ART_TINT2_GRAD2", "Secondary Accent"),
            ("THEM_ART_TINT2_BG", "Tint2 Panel Background"),
            ("THEM_ART_TINT2_FG", "Tint2 Foreground (Text)"),
            ("THEM_ART_DUNST_SMMRY", "Dunst Summary"),
            ("THEM_ART_OB_MENU_TTL", "OB Menu Title"),
            ("THEM_ART_OB_MENU_ITM", "OB Menu Items"),
        ]
        
        for var, label in vars_art:
            picker = Gtk.ColorButton()
            rgba = Gdk.RGBA()
            if "GRAD1" in var: rgba.parse("#89b4fa")
            elif "GRAD2" in var: rgba.parse("#b4befe")
            elif "BG" in var: rgba.parse("#3b4252")
            elif "FG" in var: rgba.parse("#f9f9f9")
            else: rgba.parse("#f5e0dc")
            picker.set_rgba(rgba)
            self.color_pickers_art[var] = picker
            self.create_form_row(card_colors_art, label, picker)
            
        vbox.pack_start(card_colors_art, False, False, 0)

        # 4. Interactive Palette Card
        self.int_colors_check = Gtk.CheckButton(label="Separate Colors for Interactive Mode")
        vbox.pack_start(self.int_colors_check, False, False, 0)
        
        self.card_colors_int = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.card_colors_int.get_style_context().add_class("card")
        self.card_colors_int.set_no_show_all(True)
        
        int_title = Gtk.Label(label="Theme Palette (Interactive Mode Overrides)")
        int_title.get_style_context().add_class("h3")
        self.card_colors_int.pack_start(int_title, False, False, 5)
        
        self.color_pickers_int = {}
        vars_int = [
            ("THEM_INT_ROFI_ACCNT1", "Main Accent (Interactive)"),
            ("THEM_INT_ROFI_ACCNT2", "Secondary Accent (Interactive)"),
            ("THEM_INT_TINT2_BG", "Tint2 Panel BG (Interactive)"),
            ("THEM_INT_TINT2_BG2", "Tint2 Active Task (Interactive)"),
            ("THEM_INT_TINT2_FG", "Tint2 Foreground (Interactive)"),
            ("THEM_INT_DUNST_SMMRY", "Dunst Summary (Interactive)"),
            ("THEM_INT_DUNST_PRGBR", "Dunst Progress (Interactive)"),
            ("THEM_INT_OB_MENU_TTL", "OB Menu Title (Interactive)"),
            ("THEM_INT_OB_MENU_ITM", "OB Menu Items (Interactive)"),
        ]
        
        for var, label in vars_int:
            picker = Gtk.ColorButton()
            self.color_pickers_int[var] = picker
            self.create_form_row(self.card_colors_int, label, picker)
            
        self.int_colors_check.connect("toggled", self.on_int_colors_toggled)
        vbox.pack_start(self.card_colors_int, False, False, 0)

        # 5. Assets Section
        assets_title = Gtk.Label(label="Theme Assets (Wallpapers & Icons)")
        assets_title.get_style_context().add_class("h3")
        vbox.pack_start(assets_title, False, False, 0)
        
        card_assets = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        card_assets.get_style_context().add_class("card")
        
        self.asset_pickers = {}
        assets = [
            ("artistic.jpg", "Artistic Wallpaper"),
            ("interactive.jpg", "Interactive Wallpaper"),
            ("artistic.png", "Artistic Icon (PNG)"),
            ("interactive.png", "Interactive Icon (PNG)"),
        ]
        for key, label in assets:
            btn = Gtk.FileChooserButton(title=f"Select {label}", action=Gtk.FileChooserAction.OPEN)
            filter_ext = "*.jpg" if ".jpg" in key else "*.png"
            f = Gtk.FileFilter()
            f.set_name(filter_ext)
            f.add_pattern(filter_ext)
            btn.add_filter(f)
            self.asset_pickers[key] = btn
            self.create_form_row(card_assets, label, btn)
            
        vbox.pack_start(card_assets, False, False, 0)

        # Build Button
        build_btn = Gtk.Button(label="GENERATE THEME FOLDER")
        build_btn.get_style_context().add_class("suggested-action")
        build_btn.set_size_request(-1, 60)
        build_btn.connect("clicked", self.on_build_theme_clicked)
        vbox.pack_start(build_btn, False, False, 20)

    def populate_creator_combos(self):
        gtk_themes = JoyfulThemeLib.scan_gtk_themes(self.app.script_dir)
        for t in gtk_themes: self.new_gtk_combo.append_text(t)
        if gtk_themes: self.new_gtk_combo.set_active(0)

        icons = JoyfulThemeLib.scan_icons(self.app.script_dir)
        for i in icons: self.new_icon_combo.append_text(i)
        if icons: self.new_icon_combo.set_active(0)

        fonts = JoyfulThemeLib.scan_fonts()
        for f in fonts: self.new_font_combo.append_text(f)
        
        idx = 0
        for i, f in enumerate(fonts):
            if any(x in f for x in ["JetBrains", "Inter", "Sans"]):
                idx = i
                break
        self.new_font_combo.set_active(idx)

    def create_form_row(self, parent, label_text, widget):
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        label = Gtk.Label(label=label_text)
        label.get_style_context().add_class("form-label")
        label.set_size_request(150, -1)
        label.set_xalign(0)
        
        hbox.pack_start(label, False, False, 0)
        hbox.pack_start(widget, True, True, 0)
        parent.pack_start(hbox, False, False, 0)

    def on_get_ai_template_clicked(self, widget):
        gtk_list = JoyfulThemeLib.scan_gtk_themes(self.app.script_dir)
        icon_list = JoyfulThemeLib.scan_icons(self.app.script_dir)
        font_list = JoyfulThemeLib.scan_fonts()
        
        template = {
            "SYSTEM_REFERENCE": {
                "available_gtk_themes": gtk_list,
                "available_icons": icon_list,
                "available_fonts": font_list,
                "ASSET_REQUIREMENTS": {
                    "wallpapers": "1920x1080 or higher (.jpg)",
                    "icons": "64x64 or 128x128 (.png with transparency)",
                    "openbox_buttons": "8x8 or 12x12 (.xbm)"
                },
                "instructions": "Copy this JSON and ask an AI to fill the 'theme_config' section. Choose a cohesive color palette (e.g. pastel, cyberpunk, minimal) and ensure GTK, Icons, and Fonts match the lists above. Follow ASSET_REQUIREMENTS for generated images. Colors MUST be valid HEX."
            },
            "theme_config": {
                "name": "ai-theme",
                "gtk": "Nordic",
                "icons": "Papirus-Dark-Custom",
                "font": "JetBrainsMono Nerd Font",
                "tint2_glyph": "",
                "button_style_art": "circles-filled",
                "button_style_int": "circles-outline",
                "button_loc_art": "left",
                "button_loc_int": "right",
                "colors_art": {
                    "THEM_ART_TINT2_GRAD1": "#89b4fa",
                    "THEM_ART_TINT2_GRAD2": "#b4befe",
                    "THEM_ART_TINT2_BG": "#3b4252",
                    "THEM_ART_TINT2_FG": "#f9f9f9",
                    "THEM_ART_DUNST_SMMRY": "#f5e0dc",
                    "THEM_ART_OB_MENU_TTL": "#f5e0dc",
                    "THEM_ART_OB_MENU_ITM": "#89b4fa"
                },
                "colors_int": {
                    "THEM_INT_ROFI_ACCNT1": "#89b4fa",
                    "THEM_INT_ROFI_ACCNT2": "#b4befe",
                    "THEM_INT_TINT2_BG": "#3b4252",
                    "THEM_INT_TINT2_BG2": "#434c5e",
                    "THEM_INT_TINT2_FG": "#f9f9f9",
                    "THEM_INT_DUNST_SMMRY": "#f5e0dc",
                    "THEM_INT_DUNST_PRGBR": "#89b4fa",
                    "THEM_INT_OB_MENU_TTL": "#f5e0dc",
                    "THEM_INT_OB_MENU_ITM": "#89b4fa"
                }
            }
        }
        
        json_str = json.dumps(template, indent=2)
        show_config_dialog(self.app, "AI Prompt Template", json_str, readonly=True)

    def apply_config_data(self, config):
        if "name" in config: self.new_theme_name_entry.set_text(config["name"])
        
        def set_combo(combo, val):
            if not val: return
            model = combo.get_model()
            if not model:
                 combo.get_child().set_text(val)
                 return
            for i, row in enumerate(model):
                if row[0] == val:
                    combo.set_active(i)
                    return
            combo.get_child().set_text(val)

        if "gtk" in config: set_combo(self.new_gtk_combo, config["gtk"])
        if "icons" in config: set_combo(self.new_icon_combo, config["icons"])
        if "font" in config: set_combo(self.new_font_combo, config["font"])
        if "tint2_glyph" in config: self.new_tint2_glyph.set_text(config["tint2_glyph"])
        
        if "button_style_art" in config: set_combo(self.new_btn_style_art, config["button_style_art"])
        if "button_style_int" in config: set_combo(self.new_btn_style_int, config["button_style_int"])
        if "button_loc_art" in config: self.new_btn_loc_art.set_text(config["button_loc_art"])
        if "button_loc_int" in config: self.new_btn_loc_int.set_text(config["button_loc_int"])
        
        if "colors_art" in config:
            for var, hex_val in config["colors_art"].items():
                if var in self.color_pickers_art:
                    rgba = Gdk.RGBA()
                    if rgba.parse(hex_val):
                        self.color_pickers_art[var].set_rgba(rgba)
        
        if config.get("colors_int"):
            self.int_colors_check.set_active(True)
            for var, hex_val in config["colors_int"].items():
                if var in self.color_pickers_int:
                    rgba = Gdk.RGBA()
                    if rgba.parse(hex_val):
                        self.color_pickers_int[var].set_rgba(rgba)
        else:
            self.int_colors_check.set_active(False)

    def on_int_colors_toggled(self, widget):
        active = widget.get_active()
        self.card_colors_int.set_visible(active)
        if active:
            mapping = {
                "THEM_ART_TINT2_GRAD1": ["THEM_INT_ROFI_ACCNT1", "THEM_INT_DUNST_PRGBR"],
                "THEM_ART_TINT2_GRAD2": ["THEM_INT_ROFI_ACCNT2"],
                "THEM_ART_TINT2_BG": ["THEM_INT_TINT2_BG", "THEM_INT_TINT2_BG2"],
                "THEM_ART_TINT2_FG": ["THEM_INT_TINT2_FG"],
                "THEM_ART_DUNST_SMMRY": ["THEM_INT_DUNST_SMMRY"],
                "THEM_ART_OB_MENU_TTL": ["THEM_INT_OB_MENU_TTL"],
                "THEM_ART_OB_MENU_ITM": ["THEM_INT_OB_MENU_ITM"],
            }
            for art_var, int_vars in mapping.items():
                rgba = self.color_pickers_art[art_var].get_rgba()
                for iv in int_vars:
                    self.color_pickers_int[iv].set_rgba(rgba)

    def on_build_theme_clicked(self, widget):
        name = self.new_theme_name_entry.get_text().strip()
        if not name:
            show_error_dialog(self.app, "Theme name cannot be empty!")
            return
            
        name = re.sub(r'[^a-zA-Z0-9_-]', '', name).lower()
        target_dir = os.path.join(self.app.script_dir, "custom-themes", name)
        
        if os.path.exists(target_dir):
            show_error_dialog(self.app, f"Theme folder '{name}' already exists!")
            return

        try:
            def get_combo_val(combo, default):
                active_text = combo.get_active_text()
                if active_text: return active_text
                return combo.get_child().get_text() or default

            config_data = {
                'gtk': get_combo_val(self.new_gtk_combo, "Nordic"),
                'icons': get_combo_val(self.new_icon_combo, "Papirus-Dark-Custom"),
                'font': get_combo_val(self.new_font_combo, "Sans"),
                'tint2_glyph': self.new_tint2_glyph.get_text() or "",
                'button_style_art': get_combo_val(self.new_btn_style_art, "circles-filled"),
                'button_style_int': get_combo_val(self.new_btn_style_int, "circles-outline"),
                'button_loc_art': self.new_btn_loc_art.get_text() or "left",
                'button_loc_int': self.new_btn_loc_int.get_text() or "right",
                'colors_art': {},
                'colors_int': None,
                'assets': {}
            }
            
            for var, picker in self.color_pickers_art.items():
                rgba = picker.get_rgba()
                hex_val = "#{:02x}{:02x}{:02x}".format(
                    int(rgba.red * 255), int(rgba.green * 255), int(rgba.blue * 255)
                )
                config_data['colors_art'][var] = hex_val
                
            if self.int_colors_check.get_active():
                config_data['colors_int'] = {}
                for var, picker in self.color_pickers_int.items():
                    rgba = picker.get_rgba()
                    hex_val = "#{:02x}{:02x}{:02x}".format(
                        int(rgba.red * 255), int(rgba.green * 255), int(rgba.blue * 255)
                    )
                    config_data['colors_int'][var] = hex_val
            
            for filename, picker in self.asset_pickers.items():
                src = picker.get_filename()
                if src:
                    config_data['assets'][filename] = src

            generator = ThemeGenerator(self.app.script_dir)
            generator.generate(name, config_data)

            valid, missing = JoyfulThemeLib.validate_theme_structure(target_dir)
            
            if valid:
                show_info_dialog(self.app, f"Theme '{name}' created successfully in:\n{target_dir}\n\nYou can now go to '1. Setup' and browse this folder.")
            else:
                missing_str = "\n".join([f"  - {m}" for m in missing])
                show_info_dialog(self.app, f"Theme '{name}' created with WARNINGS.\n\nSome mandatory assets are missing (you may need to add them manually):\n{missing_str}\n\nLocation: {target_dir}")

            self.app.update_info_page(target_dir)
            self.app.go_to_info_page()

        except Exception as e:
            show_error_dialog(self.app, f"Error creating theme: {e}")
