import json
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def show_error_dialog(parent, msg):
    dialog = Gtk.MessageDialog(parent=parent, flags=0, message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK, text="Error")
    dialog.format_secondary_text(msg)
    dialog.run()
    dialog.destroy()

def show_info_dialog(parent, msg):
    dialog = Gtk.MessageDialog(parent=parent, flags=0, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, text="Success")
    dialog.format_secondary_text(msg)
    dialog.run()
    dialog.destroy()

def show_config_dialog(parent, title, text, readonly=True):
    dialog = Gtk.Dialog(title=title, parent=parent, flags=0)
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

def import_ai_config_dialog(parent, apply_callback):
    dialog = Gtk.Dialog(title="Import AI Configuration", parent=parent, flags=0)
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
                apply_callback(data["theme_config"])
            else:
                apply_callback(data)
            show_info_dialog(parent, "Configuration applied successfully!")
        except Exception as e:
            show_error_dialog(parent, f"Failed to parse JSON: {e}")
    dialog.destroy()

def edit_text_dialog(parent, title, initial_text, apply_callback):
    dialog = Gtk.Dialog(title=title, parent=parent, flags=0)
    dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
    dialog.set_default_size(700, 600)
    
    box = dialog.get_content_area()
    label = Gtk.Label(label="Edit configuration below:")
    label.set_margin_top(10)
    box.pack_start(label, False, False, 5)
    
    scrolled = Gtk.ScrolledWindow()
    textview = Gtk.TextView()
    textview.set_wrap_mode(Gtk.WrapMode.NONE)
    textview.set_monospace(True)
    textview.get_buffer().set_text(initial_text)
    scrolled.add(textview)
    box.pack_start(scrolled, True, True, 10)
    
    dialog.show_all()
    response = dialog.run()
    
    if response == Gtk.ResponseType.OK:
        buffer = textview.get_buffer()
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
        apply_callback(text)
    
    dialog.destroy()

