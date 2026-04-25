import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from ..utils import run_script

class ImportPage(Gtk.Box):
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.app = app
        self.set_border_width(30)
        
        title_label = Gtk.Label(label="Step 3: Deploy Theme")
        title_label.get_style_context().add_class("main-title")
        self.pack_start(title_label, False, False, 0)

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        card.get_style_context().add_class("card")

        msg = Gtk.Label(label="Ready to integrate the theme into Joyful Desktop?\nThis action will update your configuration files.")
        msg.set_justify(Gtk.Justification.CENTER)
        msg.set_line_wrap(True)
        card.pack_start(msg, False, False, 0)

        # Target Directory Selector
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        target_label = Gtk.Label(label="Install Location:")
        target_label.get_style_context().add_class("form-label")
        
        self.target_entry = Gtk.Entry()
        self.target_entry.set_text(os.path.expanduser("~"))
        self.target_entry.set_hexpand(True)
        
        browse_btn = Gtk.Button(label="Browse")
        browse_btn.connect("clicked", self.on_browse_target_clicked)
        
        hbox.pack_start(target_label, False, False, 0)
        hbox.pack_start(self.target_entry, True, True, 0)
        hbox.pack_start(browse_btn, False, False, 0)
        card.pack_start(hbox, False, False, 10)

        import_btn = Gtk.Button(label="DEPLOY THEME")
        import_btn.get_style_context().add_class("suggested-action")
        import_btn.set_size_request(-1, 60)
        import_btn.connect("clicked", self.on_import_clicked)
        card.pack_start(import_btn, False, False, 10)

        self.import_status = Gtk.Label(label="")
        card.pack_start(self.import_status, False, False, 0)
        
        self.pack_start(card, False, False, 0)

    def on_import_clicked(self, widget):
        if not self.app.selected_theme_path:
            return
            
        dialog = Gtk.MessageDialog(
            parent=self.app,
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
            target_dir = self.target_entry.get_text().strip()
            cmd = ["./import-joyful-theme.sh", self.app.selected_theme_path, "--apply"]
            if target_dir:
                cmd.extend(["--target", target_dir])
            run_script(self.app.script_dir, cmd, lambda text: None, self.on_import_finished)

    def on_browse_target_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Select Target Installation Directory",
            parent=self.app,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK
        )
        dialog.set_current_folder(os.path.expanduser("~"))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.target_entry.set_text(dialog.get_filename())
        
        dialog.destroy()

    def on_import_finished(self, returncode):
        if returncode == 0:
            self.import_status.set_markup("<span color='#a6e3a1'><b>SUCCESS:</b> Theme imported successfully!</span>")
            self.app.refresh_library()
        else:
            self.import_status.set_markup("<span color='#f38ba8'><b>ERROR:</b> Import failed. Check logs.</span>")
