import os
import subprocess
import threading
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib, Gdk

def run_script(script_dir, cmd, output_callback, finished_callback=None):
    def task():
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=script_dir
        )
        
        for line in process.stdout:
            GLib.idle_add(output_callback, line)
            
        process.wait()
        if finished_callback:
            GLib.idle_add(finished_callback, process.returncode)

    threading.Thread(target=task, daemon=True).start()

def create_scaled_image(path, width, height):
    if not os.path.exists(path):
        return Gtk.Label(label="[Image not found]")
    try:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, width, height, True)
        return Gtk.Image.new_from_pixbuf(pixbuf)
    except Exception:
        return Gtk.Label(label="[Error loading image]")

def add_color_chip_to_box(hex_color, box):
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
