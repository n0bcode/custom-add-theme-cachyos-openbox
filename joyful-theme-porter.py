#!/usr/bin/env python3
import os
import sys
import subprocess
import threading
import re
import json
from joyful_theme_lib import JoyfulThemeLib, ThemeGenerator
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango

class JoyfulThemePorter(Gtk.Window):
    def __init__(self):
        super().__init__(title="Joyful Theme Porter")
        self.set_default_size(1100, 800)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Path configuration
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        self.selected_theme_path = None
        self.theme_name = ""
        self.theme_prefix = ""

        # Header Bar
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Joyful Theme Porter"
        hb.props.subtitle = "CachyOS Openbox Theme Importer"
        self.set_titlebar(hb)

        # Main Layout
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(self.main_box)

        # Stack for navigation
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(500)

        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(self.stack)
        stack_switcher.set_halign(Gtk.Align.CENTER)
        
        self.main_box.pack_start(stack_switcher, False, False, 10)
        self.main_box.pack_start(self.stack, True, True, 0)

        # Create Pages
        self.create_info_page()
        self.create_validate_page()
        self.create_import_page()
        self.create_library_page()
        self.create_creator_page()

        # Apply CSS
        self.apply_styles()
        
        self.show_all()

    def apply_styles(self):
        style_provider = Gtk.CssProvider()
        css = """
            window {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            .main-title {
                font-size: 26px;
                font-weight: 800;
                margin-bottom: 20px;
                color: #89b4fa;
            }
            .card {
                background-color: #313244;
                border-radius: 12px;
                padding: 24px;
                margin: 10px;
                border: 1px solid #45475a;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            }
            .info-label {
                font-size: 14px;
            }
            button {
                border-radius: 8px;
                padding: 8px 16px;
                transition: all 0.2s ease;
                font-weight: 600;
            }
            button.suggested-action {
                background: linear-gradient(135deg, #a6e3a1 0%, #94e2d5 100%);
                color: #11111b;
                border: none;
            }
            button.destructive-action {
                background: linear-gradient(135deg, #f38ba8 0%, #eba0ac 100%);
                color: #11111b;
                border: none;
            }
            button.secondary {
                background-color: #45475a;
                color: #cdd6f4;
                border: none;
            }
            textview text {
                font-family: 'JetBrains Mono', 'Fira Code', monospace;
                background-color: #181825;
                color: #a6e3a1;
                padding: 10px;
            }
            .color-chip {
                border: 2px solid #45475a;
                border-radius: 6px;
            }
            .color-label {
                font-size: 10px;
                color: #bac2de;
            }
            .list-row {
                padding: 10px;
                border-bottom: 1px solid #45475a;
            }
            .list-row:selected {
                background-color: #45475a;
            }
            .preview-title {
                font-weight: bold;
                color: #f5e0dc;
                margin-bottom: 5px;
            }
            .form-label {
                font-weight: bold;
                color: #89dceb;
            }
        """
        style_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def create_info_page(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        vbox.set_border_width(30)
        
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        title_label = Gtk.Label(label="Joyful Theme Studio")
        title_label.get_style_context().add_class("main-title")
        header_box.pack_start(title_label, False, False, 0)
        vbox.pack_start(header_box, False, False, 0)

        # Theme Selection Card
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        card.get_style_context().add_class("card")
        
        step1_label = Gtk.Label(label="Step 1: Configuration")
        step1_label.set_halign(Gtk.Align.START)
        step1_label.get_style_context().add_class("h3")
        card.pack_start(step1_label, False, False, 0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.path_entry = Gtk.Entry()
        self.path_entry.set_placeholder_text("Path to theme folder...")
        self.path_entry.set_hexpand(True)
        
        browse_btn = Gtk.Button(label="Browse Folder")
        browse_btn.get_style_context().add_class("suggested-action")
        browse_btn.connect("clicked", self.on_browse_clicked)
        
        hbox.pack_start(self.path_entry, True, True, 0)
        hbox.pack_start(browse_btn, False, False, 0)
        card.pack_start(hbox, False, False, 0)

        self.info_label = Gtk.Label(label="Please select a theme directory to begin.")
        self.info_label.set_halign(Gtk.Align.START)
        self.info_label.get_style_context().add_class("info-label")
        card.pack_start(self.info_label, False, False, 10)

        vbox.pack_start(card, False, False, 0)

        # Asset Preview Card
        self.asset_preview_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.asset_preview_box.get_style_context().add_class("card")
        self.asset_preview_box.set_visible(False)
        
        asset_title = Gtk.Label(label="Theme Assets Preview")
        asset_title.get_style_context().add_class("h3")
        self.asset_preview_box.pack_start(asset_title, False, False, 0)
        
        # Grid for images
        self.image_grid = Gtk.Grid(column_spacing=20, row_spacing=10)
        self.image_grid.set_column_homogeneous(True)
        self.asset_preview_box.pack_start(self.image_grid, True, True, 0)
        
        vbox.pack_start(self.asset_preview_box, False, False, 0)
        
        # Color Preview Section
        palette_label = Gtk.Label(label="Detected Color Palette:")
        palette_label.set_halign(Gtk.Align.START)
        palette_label.get_style_context().add_class("h3")
        vbox.pack_start(palette_label, False, False, 0)

        scroll_palette = Gtk.ScrolledWindow()
        scroll_palette.set_min_content_height(100)
        self.palette_box = Gtk.FlowBox()
        self.palette_box.set_valign(Gtk.Align.START)
        self.palette_box.set_max_children_per_line(12)
        self.palette_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.palette_box.set_homogeneous(True)
        self.palette_box.set_min_children_per_line(4)
        
        scroll_palette.add(self.palette_box)
        vbox.pack_start(scroll_palette, True, True, 0)

        self.stack.add_titled(vbox, "info", "1. Setup")

    def create_validate_page(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        vbox.set_border_width(30)
        
        title_label = Gtk.Label(label="Step 2: Security & Integrity")
        title_label.get_style_context().add_class("main-title")
        vbox.pack_start(title_label, False, False, 0)

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        card.get_style_context().add_class("card")

        desc = Gtk.Label(label="Verify that all required variables and files are present before importing.")
        desc.set_halign(Gtk.Align.START)
        card.pack_start(desc, False, False, 0)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        check_btn = Gtk.Button(label="Check Integrity")
        check_btn.get_style_context().add_class("secondary")
        check_btn.connect("clicked", self.on_check_clicked)
        
        dryrun_btn = Gtk.Button(label="Dry-run Simulation")
        dryrun_btn.get_style_context().add_class("secondary")
        dryrun_btn.connect("clicked", self.on_dryrun_clicked)
        
        btn_box.pack_start(check_btn, True, True, 0)
        btn_box.pack_start(dryrun_btn, True, True, 0)
        card.pack_start(btn_box, False, False, 0)
        
        vbox.pack_start(card, False, False, 0)

        # Terminal-like output
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)
        self.output_view = Gtk.TextView()
        self.output_view.set_editable(False)
        self.output_view.set_cursor_visible(False)
        self.output_view.set_left_margin(10)
        self.output_view.set_right_margin(10)
        self.output_view.set_top_margin(10)
        self.output_view.set_bottom_margin(10)
        self.output_buffer = self.output_view.get_buffer()
        scrolled.add(self.output_view)
        vbox.pack_start(scrolled, True, True, 0)

        self.stack.add_titled(vbox, "validate", "2. Validation")

    def create_import_page(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        vbox.set_border_width(30)
        
        title_label = Gtk.Label(label="Step 3: Deploy Theme")
        title_label.get_style_context().add_class("main-title")
        vbox.pack_start(title_label, False, False, 0)

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        card.get_style_context().add_class("card")

        msg = Gtk.Label(label="Ready to integrate the theme into Joyful Desktop?\nThis action will update your configuration files.")
        msg.set_justify(Gtk.Justification.CENTER)
        msg.set_line_wrap(True)
        card.pack_start(msg, False, False, 0)

        import_btn = Gtk.Button(label="DEPLOY THEME")
        import_btn.get_style_context().add_class("suggested-action")
        import_btn.set_size_request(-1, 60)
        import_btn.connect("clicked", self.on_import_clicked)
        card.pack_start(import_btn, False, False, 10)

        self.import_status = Gtk.Label(label="")
        card.pack_start(self.import_status, False, False, 0)
        
        vbox.pack_start(card, False, False, 0)

        self.stack.add_titled(vbox, "import", "3. Finish")

    def create_library_page(self):
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        
        # Left Side: Theme List
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
        
        hbox.pack_start(sidebar, False, False, 0)
        
        # Right Side: Detail View
        self.detail_view = Gtk.ScrolledWindow()
        self.detail_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.detail_box.set_border_width(20)
        self.detail_view.add(self.detail_box)
        
        # Initial Placeholder
        placeholder = Gtk.Label()
        placeholder.set_markup("<span size='large' color='#89b4fa'><b>Select a theme</b></span>\n\nChoose a theme from the sidebar to view its details and health status.")
        placeholder.set_justify(Gtk.Justification.CENTER)
        placeholder.set_margin_top(100)
        self.detail_box.pack_start(placeholder, True, True, 0)
        
        hbox.pack_start(self.detail_view, True, True, 0)
        
        self.stack.add_titled(hbox, "library", "Hệ thống")
        self.load_system_themes()

    def on_get_ai_template_clicked(self, widget):
        gtk_list = JoyfulThemeLib.scan_gtk_themes(self.script_dir)
        icon_list = JoyfulThemeLib.scan_icons(self.script_dir)
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
                "instructions": "Copy this JSON and ask an AI to fill the 'theme_config' section. Ensure GTK, Icons, and Fonts match the lists above. Follow ASSET_REQUIREMENTS for generated images."
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
                    "THEM_ART_DUNST_SMMRY": "#f5e0dc",
                    "THEM_ART_OB_MENU_TTL": "#f5e0dc",
                    "THEM_ART_OB_MENU_ITM": "#89b4fa"
                },
                "colors_int": None # Or a dictionary like colors_art
            }
        }
        
        json_str = json.dumps(template, indent=2)
        self.show_config_dialog("AI Prompt Template", json_str, readonly=True)

    def on_import_ai_config_clicked(self, widget):
        dialog = Gtk.Dialog(title="Import AI Configuration", parent=self, flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_APPLY, Gtk.ResponseType.OK)
        dialog.set_default_size(600, 500)
        
        box = dialog.get_content_area()
        label = Gtk.Label(label="Paste your AI-generated JSON below:")
        label.set_margin_top(10)
        box.pack_start(label, False, False, 5)
        
        scrolled = Gtk.ScrolledWindow()
        textview = Gtk.TextView()
        textview.set_wrap_mode(Gtk.WrapMode.NONE)
        scrolled.add(textview)
        box.pack_start(scrolled, True, True, 10)
        
        dialog.show_all()
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            buffer = textview.get_buffer()
            text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
            try:
                data = json.loads(text)
                if "theme_config" in data:
                    self.apply_config_data(data["theme_config"])
                else:
                    self.apply_config_data(data)
                self.show_info_dialog("Configuration applied successfully!")
            except Exception as e:
                self.show_error_dialog(f"Failed to parse JSON: {e}")
        
        dialog.destroy()

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
        
        # Artistic Colors
        if "colors_art" in config:
            for var, hex_val in config["colors_art"].items():
                if var in self.color_pickers_art:
                    rgba = Gdk.RGBA()
                    if rgba.parse(hex_val):
                        self.color_pickers_art[var].set_rgba(rgba)
        
        # Interactive Colors
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
            # Sync Artistic colors to Interactive pickers as a starting point
            mapping = {
                "THEM_ART_TINT2_GRAD1": ["THEM_INT_ROFI_ACCNT1", "THEM_INT_DUNST_PRGBR"],
                "THEM_ART_TINT2_GRAD2": ["THEM_INT_ROFI_ACCNT2"],
                "THEM_ART_DUNST_SMMRY": ["THEM_INT_DUNST_SMMRY"],
                "THEM_ART_OB_MENU_TTL": ["THEM_INT_OB_MENU_TTL"],
                "THEM_ART_OB_MENU_ITM": ["THEM_INT_OB_MENU_ITM"],
            }
            for art_var, int_vars in mapping.items():
                rgba = self.color_pickers_art[art_var].get_rgba()
                for iv in int_vars:
                    self.color_pickers_int[iv].set_rgba(rgba)

    def create_creator_page(self):
        scrolled = Gtk.ScrolledWindow()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        vbox.set_border_width(10)
        scrolled.add(vbox)
        
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
        btn_import_config.connect("clicked", self.on_import_ai_config_clicked)
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
            ("THEM_ART_DUNST_SMMRY", "Dunst Summary"),
            ("THEM_ART_OB_MENU_TTL", "OB Menu Title"),
            ("THEM_ART_OB_MENU_ITM", "OB Menu Items"),
        ]
        
        for var, label in vars_art:
            picker = Gtk.ColorButton()
            # Set default
            rgba = Gdk.RGBA()
            if "GRAD1" in var: rgba.parse("#89b4fa")
            elif "GRAD2" in var: rgba.parse("#b4befe")
            else: rgba.parse("#f5e0dc")
            picker.set_rgba(rgba)
            self.color_pickers_art[var] = picker
            self.create_form_row(card_colors_art, label, picker)
            
        vbox.pack_start(card_colors_art, False, False, 0)

        # 4. Interactive Palette Card (Advanced)
        self.int_colors_check = Gtk.CheckButton(label="Separate Colors for Interactive Mode")
        vbox.pack_start(self.int_colors_check, False, False, 0)
        
        self.card_colors_int = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.card_colors_int.get_style_context().add_class("card")
        self.card_colors_int.set_no_show_all(True) # Hidden by default
        
        int_title = Gtk.Label(label="Theme Palette (Interactive Mode Overrides)")
        int_title.get_style_context().add_class("h3")
        self.card_colors_int.pack_start(int_title, False, False, 5)
        
        self.color_pickers_int = {}
        vars_int = [
            ("THEM_INT_ROFI_ACCNT1", "Main Accent (Interactive)"),
            ("THEM_INT_ROFI_ACCNT2", "Secondary Accent (Interactive)"),
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

        self.stack.add_titled(scrolled, "creator", "Thiết kế")

    def populate_creator_combos(self):
        # GTK Themes
        gtk_themes = JoyfulThemeLib.scan_gtk_themes(self.script_dir)
        for t in gtk_themes: self.new_gtk_combo.append_text(t)
        if gtk_themes: self.new_gtk_combo.set_active(0)

        # Icons
        icons = JoyfulThemeLib.scan_icons(self.script_dir)
        for i in icons: self.new_icon_combo.append_text(i)
        if icons: self.new_icon_combo.set_active(0)

        # Fonts
        fonts = JoyfulThemeLib.scan_fonts()
        for f in fonts: self.new_font_combo.append_text(f)
        
        # Find a good default
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

    def on_build_theme_clicked(self, widget):
        name = self.new_theme_name_entry.get_text().strip()
        if not name:
            self.show_error_dialog("Theme name cannot be empty!")
            return
            
        name = re.sub(r'[^a-zA-Z0-9_-]', '', name).lower()
        target_dir = os.path.join(self.script_dir, "custom-themes", name)
        
        if os.path.exists(target_dir):
            self.show_error_dialog(f"Theme folder '{name}' already exists!")
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
            
            # Colors - Artistic
            for var, picker in self.color_pickers_art.items():
                rgba = picker.get_rgba()
                hex_val = "#{:02x}{:02x}{:02x}".format(
                    int(rgba.red * 255), int(rgba.green * 255), int(rgba.blue * 255)
                )
                config_data['colors_art'][var] = hex_val
                
            # Colors - Interactive (if enabled)
            if self.int_colors_check.get_active():
                config_data['colors_int'] = {}
                for var, picker in self.color_pickers_int.items():
                    rgba = picker.get_rgba()
                    hex_val = "#{:02x}{:02x}{:02x}".format(
                        int(rgba.red * 255), int(rgba.green * 255), int(rgba.blue * 255)
                    )
                    config_data['colors_int'][var] = hex_val
            
            # Assets
            for filename, picker in self.asset_pickers.items():
                src = picker.get_filename()
                if src:
                    config_data['assets'][filename] = src

            generator = ThemeGenerator(self.script_dir)
            generator.generate(name, config_data)

            # --- Validation Integration ---
            valid, missing = JoyfulThemeLib.validate_theme_structure(target_dir)
            
            if valid:
                self.show_info_dialog(f"Theme '{name}' created successfully in:\n{target_dir}\n\nYou can now go to '1. Setup' and browse this folder.")
            else:
                missing_str = "\n".join([f"  - {m}" for m in missing])
                self.show_info_dialog(f"Theme '{name}' created with WARNINGS.\n\nSome mandatory assets are missing (you may need to add them manually):\n{missing_str}\n\nLocation: {target_dir}")

            self.path_entry.set_text(target_dir)
            self.update_theme_info(target_dir)
            self.stack.set_visible_child_name("info")

        except Exception as e:
            self.show_error_dialog(f"Error creating theme: {e}")

    def show_error_dialog(self, msg):
        dialog = Gtk.MessageDialog(parent=self, flags=0, message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK, text="Error")
        dialog.format_secondary_text(msg)
        dialog.run()
        dialog.destroy()

    def show_info_dialog(self, msg):
        dialog = Gtk.MessageDialog(parent=self, flags=0, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, text="Success")
        dialog.format_secondary_text(msg)
        dialog.run()
        dialog.destroy()

    def show_config_dialog(self, title, text, readonly=True):
        dialog = Gtk.Dialog(title=title, parent=self, flags=0)
        dialog.set_default_size(700, 600)
        
        box = dialog.get_content_area()
        box.set_spacing(10)
        box.set_border_width(10)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)
        
        text_view = Gtk.TextView()
        text_view.set_editable(not readonly)
        text_view.set_wrap_mode(Gtk.WrapMode.NONE)
        text_view.set_monospace(True)
        
        # Simple CSS for padding
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"textview { padding: 10px; }")
        text_view.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        
        text_view.get_buffer().set_text(text)
        scrolled.add(text_view)
        box.add(scrolled)
        
        dialog.add_button("Close", Gtk.ResponseType.CLOSE)
        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def load_system_themes(self):
        # Clear list
        for child in self.theme_listbox.get_children():
            self.theme_listbox.remove(child)
            
        themes_path = os.path.join(self.script_dir, ".config/rofi/themes/colorschemes")
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
        # Clear detail box
        for child in self.detail_box.get_children():
            self.detail_box.remove(child)

        # Get dynamic config from db.theme.joy
        db_config = JoyfulThemeLib.get_db_config(self.script_dir, theme_name)
        art_wall_file = db_config['artistic_wallpaper']
        int_wall_file = db_config['interactive_wallpaper']
            
        title = Gtk.Label(label=f"Theme: {theme_name}")
        title.get_style_context().add_class("main-title")
        self.detail_box.pack_start(title, False, False, 0)
        
        # --- System Health Section ---
        health_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        health_box.get_style_context().add_class("card")
        health_box.set_margin_bottom(10)
        
        health_title = Gtk.Label(label="System Health Status")
        health_title.set_halign(Gtk.Align.START)
        health_title.get_style_context().add_class("preview-title")
        health_box.pack_start(health_title, False, False, 5)
        
        files_to_check = {
            "Rofi (.rasi)": os.path.join(self.script_dir, f".config/rofi/themes/colorschemes/{theme_name}.rasi"),
            "Dunst (.dunstrc)": os.path.join(self.script_dir, f".config/dunst/{theme_name}.artistic.dunstrc"),
            "Tint2 (.tint2rc)": os.path.join(self.script_dir, f".config/tint2/{theme_name}-top.interactive.tint2rc"),
            "Wallpaper (.jpg)": os.path.join(self.script_dir, f".wallpapers/{theme_name}/{art_wall_file}"),
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
        # Images Row
        img_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        
        # Artistic Preview
        art_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        art_box.pack_start(Gtk.Label(label="Artistic Mode"), False, False, 0)
        art_wall = os.path.join(self.script_dir, f".wallpapers/{theme_name}/{art_wall_file}")
        art_img = self.create_scaled_image(art_wall, 250, 150)
        art_box.pack_start(art_img, False, False, 0)
        
        art_icon_path = os.path.join(self.script_dir, f".icons/Gladient/{theme_name}.artistic.png")
        art_icon = self.create_scaled_image(art_icon_path, 48, 48)
        art_box.pack_start(art_icon, False, False, 0)
        
        img_hbox.pack_start(art_box, True, True, 0)
        
        # Interactive Preview
        int_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        int_box.pack_start(Gtk.Label(label="Interactive Mode"), False, False, 0)
        int_wall = os.path.join(self.script_dir, f".wallpapers/{theme_name}/{int_wall_file}")
        int_img = self.create_scaled_image(int_wall, 250, 150)
        int_box.pack_start(int_img, False, False, 0)
        
        int_icon_path = os.path.join(self.script_dir, f".icons/Gladient/{theme_name}.interactive.png")
        int_icon = self.create_scaled_image(int_icon_path, 48, 48)
        int_box.pack_start(int_icon, False, False, 0)
        
        img_hbox.pack_start(int_box, True, True, 0)
        
        self.detail_box.pack_start(img_hbox, False, False, 0)
        
        # Colors Palette from .joyfuld
        palette_label = Gtk.Label(label="System Palette (.joyfuld):")
        palette_label.set_halign(Gtk.Align.START)
        self.detail_box.pack_start(palette_label, False, False, 0)
        
        p_flow = Gtk.FlowBox()
        p_flow.set_max_children_per_line(10)
        p_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        
        self.extract_system_colors(theme_name, p_flow)
        self.detail_box.pack_start(p_flow, False, False, 0)
        
        # Config Viewer
        config_btn = Gtk.Button(label="Show Raw Config Snippet")
        config_btn.get_style_context().add_class("secondary")
        config_btn.connect("clicked", lambda x: self.show_raw_config(theme_name))
        self.detail_box.pack_start(config_btn, False, False, 0)
        
        self.detail_box.show_all()

    def create_scaled_image(self, path, width, height):
        if not os.path.exists(path):
            # Placeholder or empty
            label = Gtk.Label(label="[Image not found]")
            return label
        try:
            from gi.repository import GdkPixbuf
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, width, height, True)
            image = Gtk.Image.new_from_pixbuf(pixbuf)
            return image
        except Exception:
            return Gtk.Label(label="[Error loading image]")

    def extract_system_colors(self, theme_name, flowbox):
        prefix = JoyfulThemeLib.get_prefix(theme_name)
        joyfuld_path = os.path.join(self.script_dir, ".joyfuld")
        colors = JoyfulThemeLib.extract_colors_from_snippet(joyfuld_path, prefix)
        
        # Fallback to Rofi file if no colors found in .joyfuld
        if not colors:
            rofi_path = os.path.join(self.script_dir, f".config/rofi/themes/colorschemes/{theme_name}.rasi")
            colors = JoyfulThemeLib.extract_colors_from_snippet(rofi_path)
            
        for color in colors:
            self.add_color_chip_to_box(color, flowbox)

    def add_color_chip_to_box(self, hex_color, box):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        vbox.set_margin_top(5)
        vbox.set_margin_bottom(5)
        vbox.set_margin_start(5)
        vbox.set_margin_end(5)
        
        drawing_area = Gtk.DrawingArea()
        drawing_area.set_size_request(40, 40)
        drawing_area.get_style_context().add_class("color-chip")
        
        def on_draw(widget, cr):
            rgba = Gdk.RGBA()
            if rgba.parse(hex_color):
                cr.set_source_rgba(rgba.red, rgba.green, rgba.blue, rgba.alpha)
                cr.rectangle(0, 0, 40, 40)
                cr.fill()
        drawing_area.connect("draw", on_draw)
        
        label = Gtk.Label(label=hex_color)
        label.get_style_context().add_class("color-label")
        
        vbox.pack_start(drawing_area, False, False, 0)
        vbox.pack_start(label, False, False, 0)
        box.add(vbox)

    def show_raw_config(self, theme_name):
        prefix = JoyfulThemeLib.get_prefix(theme_name)
        joyfuld_path = os.path.join(self.script_dir, ".joyfuld")
        db_path = os.path.join(self.script_dir, ".config/openbox/joyful-desktop/db.theme.joy")
        
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
        
        # Display in a dialog
        dialog = Gtk.Dialog(title=f"Config Snippet: {theme_name}", parent=self)
        dialog.set_default_size(900, 600)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        text_view = Gtk.TextView()
        text_view.set_editable(False)
        text_view.set_cursor_visible(False)
        text_view.set_wrap_mode(Gtk.WrapMode.NONE)
        
        # Use CSS to set font - the modern, non-deprecated way for GTK3
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

    def on_browse_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Select Theme Folder",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK
        )

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            path = dialog.get_filename()
            self.path_entry.set_text(path)
            self.update_theme_info(path)
        
        dialog.destroy()

    def update_theme_info(self, path):
        self.selected_theme_path = path
        self.theme_name = os.path.basename(path)
        self.theme_prefix = JoyfulThemeLib.get_prefix(self.theme_name)
        
        # 1. Parse Metadata from snippet
        snippet_path = os.path.join(path, "env.joyfuld.snippet")
        meta = JoyfulThemeLib.extract_metadata_from_snippet(snippet_path)
        
        info_text = f"<b>Theme Folder:</b> <span color='#fab387'>{self.theme_name}</span>\n"
        info_text += f"<b>System Prefix:</b> <span color='#f9e2af'>{self.theme_prefix}</span>\n"
        if meta.get('gtk'): info_text += f"<b>GTK Theme:</b> <span color='#94e2d5'>{meta['gtk']}</span>\n"
        if meta.get('icons'): info_text += f"<b>Icon Theme:</b> <span color='#cba6f7'>{meta['icons']}</span>\n"
        if meta.get('font'): info_text += f"<b>Main Font:</b> <span color='#89b4fa'>{meta['font']}</span>\n"
        info_text += f"<b>Target Path:</b> {path}"
        self.info_label.set_markup(info_text)
        
        # 2. Update Image Previews
        for child in self.image_grid.get_children():
            self.image_grid.remove(child)
            
        assets = [
            ("Wallpapers", "wallpapers/artistic.jpg", "wallpapers/interactive.jpg", 180, 100),
            ("Icons", "icons/artistic.png", "icons/interactive.png", 64, 64)
        ]
        
        self.asset_preview_box.set_visible(True)
        for row_idx, (label, art_p, int_p, w, h) in enumerate(assets):
            title = Gtk.Label(label=f"<b>{label}</b>")
            title.set_use_markup(True)
            title.set_halign(Gtk.Align.START)
            self.image_grid.attach(title, 0, row_idx*2, 2, 1)
            
            # Artistic slot
            art_path = os.path.join(path, art_p)
            art_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            art_vbox.pack_start(Gtk.Label(label="Artistic"), False, False, 0)
            if os.path.exists(art_path):
                try:
                    art_img = self.create_scaled_image(art_path, w, h)
                    art_vbox.pack_start(art_img, False, False, 0)
                except:
                    art_vbox.pack_start(Gtk.Label(label="(Load Error)"), False, False, 0)
            else:
                art_vbox.pack_start(Gtk.Label(label="(Missing)"), False, False, 0)
            self.image_grid.attach(art_vbox, 0, row_idx*2+1, 1, 1)
            
            # Interactive slot
            int_path = os.path.join(path, int_p)
            int_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            int_vbox.pack_start(Gtk.Label(label="Interactive"), False, False, 0)
            if os.path.exists(int_path):
                try:
                    int_img = self.create_scaled_image(int_path, w, h)
                    int_vbox.pack_start(int_img, False, False, 0)
                except:
                    int_vbox.pack_start(Gtk.Label(label="(Load Error)"), False, False, 0)
            else:
                int_vbox.pack_start(Gtk.Label(label="(Missing)"), False, False, 0)
            self.image_grid.attach(int_vbox, 1, row_idx*2+1, 1, 1)
            
        self.asset_preview_box.show_all()
        
        # 3. Update Colors
        self.update_palette(path)

    def update_palette(self, path):
        # Clear existing
        for child in self.palette_box.get_children():
            self.palette_box.remove(child)
            
        snippet_path = os.path.join(path, "env.joyfuld.snippet")
        colors = JoyfulThemeLib.extract_colors_from_snippet(snippet_path)
        for color in colors:
            self.add_color_chip_to_box(color, self.palette_box)
        
        self.palette_box.show_all()

    def run_script(self, cmd, callback=None):
        def task():
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=self.script_dir
            )
            
            for line in process.stdout:
                GLib.idle_add(self.append_output, line)
                
            process.wait()
            if callback:
                GLib.idle_add(callback, process.returncode)

        threading.Thread(target=task, daemon=True).start()

    def append_output(self, text):
        # Remove ANSI color codes
        clean_text = re.sub(r'\x1b\[[0-9;]*m', '', text)
        iter = self.output_buffer.get_end_iter()
        self.output_buffer.insert(iter, clean_text)
        
        # Scroll to bottom
        adj = self.output_view.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())

    def on_check_clicked(self, widget):
        if not self.selected_theme_path:
            return
        self.output_buffer.set_text("")
        cmd = ["./joyful-tester.sh", "check", self.theme_name]
        self.run_script(cmd)

    def on_dryrun_clicked(self, widget):
        if not self.selected_theme_path:
            return
        self.output_buffer.set_text("")
        # We need to make sure import-joyful-theme is called with the path
        cmd = ["./import-joyful-theme.sh", self.selected_theme_path]
        self.run_script(cmd)

    def on_import_clicked(self, widget):
        if not self.selected_theme_path:
            return
            
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="Proceed with Import?",
        )
        dialog.format_secondary_text(
            "This will modify your system configuration files. Are you sure?"
        )
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.OK:
            self.import_status.set_text("Importing...")
            cmd = ["./import-joyful-theme.sh", self.selected_theme_path, "--apply"]
            self.run_script(cmd, self.on_import_finished)

    def on_import_finished(self, returncode):
        if returncode == 0:
            self.import_status.set_markup("<span color='#a6e3a1'><b>SUCCESS:</b> Theme imported successfully!</span>")
            self.load_system_themes() # Refresh library
        else:
            self.import_status.set_markup("<span color='#f38ba8'><b>ERROR:</b> Import failed. Check logs.</span>")

if __name__ == "__main__":
    app = JoyfulThemePorter()
    app.connect("destroy", Gtk.main_quit)
    Gtk.main()
