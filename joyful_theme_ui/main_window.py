import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from .styles import apply_styles
from .pages.info_page import InfoPage
from .pages.validate_page import ValidatePage
from .pages.import_page import ImportPage
from .pages.library_page import LibraryPage
from .pages.creator_page import CreatorPage

class JoyfulThemePorter(Gtk.Window):
    def __init__(self, script_dir):
        super().__init__(title="Joyful Theme Porter")
        self.set_default_size(1100, 800)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Path configuration
        self.script_dir = script_dir
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
        self.info_page = InfoPage(self)
        self.stack.add_titled(self.info_page, "info", "1. Setup")
        
        self.validate_page = ValidatePage(self)
        self.stack.add_titled(self.validate_page, "validate", "2. Validation")
        
        self.import_page = ImportPage(self)
        self.stack.add_titled(self.import_page, "import", "3. Finish")
        
        self.library_page = LibraryPage(self)
        self.stack.add_titled(self.library_page, "library", "Hệ thống")
        
        self.creator_page = CreatorPage(self)
        self.stack.add_titled(self.creator_page, "creator", "Thiết kế")

        # Apply CSS
        apply_styles()
        
        self.show_all()

    def update_info_page(self, path):
        self.info_page.path_entry.set_text(path)
        self.info_page.update_theme_info(path)
        
    def refresh_library(self):
        self.library_page.load_system_themes()
        
    def go_to_info_page(self):
        self.stack.set_visible_child_name("info")
