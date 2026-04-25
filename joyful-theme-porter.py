#!/usr/bin/env python3
import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from joyful_theme_ui.main_window import JoyfulThemePorter

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.realpath(__file__))
    app = JoyfulThemePorter(script_dir)
    app.connect("destroy", Gtk.main_quit)
    Gtk.main()
