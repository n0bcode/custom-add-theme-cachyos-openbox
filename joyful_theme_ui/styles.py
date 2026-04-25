import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

def apply_styles():
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
