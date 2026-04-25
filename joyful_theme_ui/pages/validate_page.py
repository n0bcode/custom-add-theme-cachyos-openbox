import gi
import re
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from ..utils import run_script

class ValidatePage(Gtk.Box):
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.app = app
        self.set_border_width(30)
        
        title_label = Gtk.Label(label="Step 2: Security & Integrity")
        title_label.get_style_context().add_class("main-title")
        self.pack_start(title_label, False, False, 0)

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
        
        self.pack_start(card, False, False, 0)

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
        self.pack_start(scrolled, True, True, 0)

    def append_output(self, text):
        clean_text = re.sub(r'\x1b\[[0-9;]*m', '', text)
        iter = self.output_buffer.get_end_iter()
        self.output_buffer.insert(iter, clean_text)
        
        adj = self.output_view.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())

    def on_check_clicked(self, widget):
        if not self.app.selected_theme_path:
            return
        self.output_buffer.set_text("")
        cmd = ["./joyful-tester.sh", "check", self.app.theme_name]
        run_script(self.app.script_dir, cmd, self.append_output)

    def on_dryrun_clicked(self, widget):
        if not self.app.selected_theme_path:
            return
        self.output_buffer.set_text("")
        cmd = ["./import-joyful-theme.sh", self.app.selected_theme_path]
        run_script(self.app.script_dir, cmd, self.append_output)
