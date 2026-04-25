import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from joyful_theme_lib import JoyfulThemeLib
from ..utils import create_scaled_image, add_color_chip_to_box

class InfoPage(Gtk.Box):
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.app = app
        self.set_border_width(30)
        
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        title_label = Gtk.Label(label="Joyful Theme Studio")
        title_label.get_style_context().add_class("main-title")
        header_box.pack_start(title_label, False, False, 0)
        self.pack_start(header_box, False, False, 0)

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

        self.pack_start(card, False, False, 0)

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
        
        self.pack_start(self.asset_preview_box, False, False, 0)
        
        # Color Preview Section
        palette_label = Gtk.Label(label="Detected Color Palette:")
        palette_label.set_halign(Gtk.Align.START)
        palette_label.get_style_context().add_class("h3")
        self.pack_start(palette_label, False, False, 0)

        scroll_palette = Gtk.ScrolledWindow()
        scroll_palette.set_min_content_height(100)
        self.palette_box = Gtk.FlowBox()
        self.palette_box.set_valign(Gtk.Align.START)
        self.palette_box.set_max_children_per_line(12)
        self.palette_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.palette_box.set_homogeneous(True)
        self.palette_box.set_min_children_per_line(4)
        
        scroll_palette.add(self.palette_box)
        self.pack_start(scroll_palette, True, True, 0)

    def on_browse_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Select Theme Folder",
            parent=self.app,
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
        self.app.selected_theme_path = path
        self.app.theme_name = os.path.basename(path)
        self.app.theme_prefix = JoyfulThemeLib.get_prefix(self.app.theme_name)
        
        # 1. Parse Metadata from snippet
        snippet_path = os.path.join(path, "env.joyfuld.snippet")
        meta = JoyfulThemeLib.extract_metadata_from_snippet(snippet_path)
        
        info_text = f"<b>Theme Folder:</b> <span color='#fab387'>{self.app.theme_name}</span>\n"
        info_text += f"<b>System Prefix:</b> <span color='#f9e2af'>{self.app.theme_prefix}</span>\n"
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
                art_img = create_scaled_image(art_path, w, h)
                art_vbox.pack_start(art_img, False, False, 0)
            else:
                art_vbox.pack_start(Gtk.Label(label="(Missing)"), False, False, 0)
            self.image_grid.attach(art_vbox, 0, row_idx*2+1, 1, 1)
            
            # Interactive slot
            int_path = os.path.join(path, int_p)
            int_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            int_vbox.pack_start(Gtk.Label(label="Interactive"), False, False, 0)
            if os.path.exists(int_path):
                int_img = create_scaled_image(int_path, w, h)
                int_vbox.pack_start(int_img, False, False, 0)
            else:
                int_vbox.pack_start(Gtk.Label(label="(Missing)"), False, False, 0)
            self.image_grid.attach(int_vbox, 1, row_idx*2+1, 1, 1)
            
        self.asset_preview_box.show_all()
        
        # 3. Update Colors
        self.update_palette(path)

    def update_palette(self, path):
        for child in self.palette_box.get_children():
            self.palette_box.remove(child)
            
        snippet_path = os.path.join(path, "env.joyfuld.snippet")
        colors = JoyfulThemeLib.extract_colors_from_snippet(snippet_path)
        for color in colors:
            add_color_chip_to_box(color, self.palette_box)
        
        self.palette_box.show_all()
