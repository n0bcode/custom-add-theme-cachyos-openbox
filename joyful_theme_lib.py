import os
import re
import subprocess
import glob
import shutil

class JoyfulThemeLib:
    """Shared logic for Joyful Desktop theming."""
    
    @staticmethod
    def get_prefix(theme_name):
        """Calculate the 4-character uppercase prefix for a theme."""
        if not theme_name:
            return ""
        return theme_name.upper()[:4]

    @staticmethod
    def scan_fonts():
        """List UI and Nerd Fonts installed on the system."""
        fonts = []
        try:
            output = subprocess.check_output(["fc-list", ":", "family"], text=True)
            # Filter for common UI and Nerd fonts to keep list manageable
            pattern = re.compile(r"nerd|jetbrains|fira|hack|cantarell|comfortaa|awesome", re.IGNORECASE)
            for line in output.splitlines():
                family = line.split(":")[0].strip()
                if family and pattern.search(family):
                    fonts.append(family)
            return sorted(list(set(fonts)))
        except Exception as e:
            print(f"Error scanning fonts: {e}")
            return ["Sans", "Serif", "Monospace"]

    @staticmethod
    def scan_icons(script_dir):
        """Scan available Icon themes from local and system paths."""
        icons = set()
        # Prioritize local staging folders
        search_paths = [
            os.path.join(script_dir, ".icons"),
            os.path.join(os.path.expanduser("~"), ".icons"),
            "/usr/share/icons"
        ]
        for dir_path in search_paths:
            if os.path.exists(dir_path):
                try:
                    for item in os.listdir(dir_path):
                        if os.path.isdir(os.path.join(dir_path, item)):
                            if os.path.exists(os.path.join(dir_path, item, "index.theme")):
                                icons.add(item)
                except: pass
        return sorted(list(icons))

    @staticmethod
    def scan_gtk_themes(script_dir):
        """Scan available GTK themes from local and system paths."""
        themes = set()
        search_paths = [
            os.path.join(script_dir, ".themes"),
            os.path.join(os.path.expanduser("~"), ".themes"),
            "/usr/share/themes"
        ]
        for dir_path in search_paths:
            if os.path.exists(dir_path):
                try:
                    for item in os.listdir(dir_path):
                        full_path = os.path.join(dir_path, item)
                        if os.path.isdir(full_path):
                            if os.path.exists(os.path.join(full_path, "gtk-3.0")) or \
                               os.path.exists(os.path.join(full_path, "gtk-2.0")):
                                themes.add(item)
                except: pass
        return sorted(list(themes))

    @staticmethod
    def extract_colors_from_snippet(snippet_path, prefix=None):
        """Extract hex colors from a snippet file, optionally filtering by prefix."""
        colors = set()
        if os.path.exists(snippet_path):
            try:
                with open(snippet_path, 'r') as f:
                    content = f.read()
                    
                    if prefix:
                        # Match variables starting with prefix
                        pattern = rf"^{prefix}_.*=(#[0-9a-fA-F]{6})"
                        matches = re.findall(pattern, content, re.MULTILINE)
                        matches += re.findall(rf"^{prefix}_.*=['\"](#[0-9a-fA-F]{6})['\"]", content, re.MULTILINE)
                    else:
                        # Match any colors
                        matches = re.findall(r"=['\"](#[0-9a-fA-F]{6})['\"]", content)
                        matches += re.findall(r"=(#[0-9a-fA-F]{6})(?:\s|$)", content)
                        
                    for c in matches:
                        colors.add(c.lower())
            except Exception as e:
                print(f"Error reading snippet {snippet_path}: {e}")
        return sorted(list(colors))

    @staticmethod
    def extract_metadata_from_snippet(snippet_path):
        """Extract variables like GTK, ICON, FONT from env.joyfuld.snippet"""
        metadata = {}
        if os.path.exists(snippet_path):
            try:
                with open(snippet_path, 'r') as f:
                    content = f.read()
                    # Match pattern like PREFIX_GTK='name'
                    match_gtk = re.search(r"_[A-Z0-9]+_GTK=['\"]([^'\"]+)['\"]", content)
                    match_icon = re.search(r"_[A-Z0-9]+_ICON=['\"]([^'\"]+)['\"]", content)
                    match_font = re.search(r"_[A-Z0-9]+_FONT_FACE=['\"]([^'\"]+)['\"]", content)
                    
                    if match_gtk: metadata['gtk'] = match_gtk.group(1)
                    if match_icon: metadata['icons'] = match_icon.group(1)
                    if match_font: metadata['font'] = match_font.group(1)
            except Exception as e:
                print(f"Error reading metadata from snippet: {e}")
        return metadata

    @staticmethod
    def validate_theme_structure(path):
        """
        Check if a theme directory has the required structure and files.
        Returns (is_valid, list_of_missing_items)
        """
        required_files = [
            "env.joyfuld.snippet",
            "db.theme.joy.snippet",
            "rofi/colorscheme.rasi",
            "dunst/artistic.dunstrc",
            "dunst/interactive.dunstrc",
            "openbox/themerc",
            "tint2/top.interactive.tint2rc",
            "tint2/horizontal.artistic.tint2rc",
            "tint2/vertical.artistic.tint2rc",
            "icons/artistic.png",
            "icons/interactive.png",
            "wallpapers/artistic.jpg",
            "wallpapers/interactive.jpg"
        ]
        missing = []
        if not os.path.isdir(path):
            return False, ["Directory does not exist"]
            
        for f in required_files:
            if not os.path.exists(os.path.join(path, f)):
                missing.append(f)
                
        return len(missing) == 0, missing

    @staticmethod
    def get_db_config(script_dir, theme_name):
        """
        Parse db.theme.joy for a specific theme's settings.
        Returns a dictionary with wallpaper and button style filenames.
        """
        config = {
            'artistic_wallpaper': f"{theme_name}.artistic.jpg",
            'interactive_wallpaper': f"{theme_name}.interactive.jpg",
            'artistic_button_style': 'circles-filled',
            'interactive_button_style': 'circles-outline'
        }
        db_path = os.path.join(script_dir, ".config/openbox/joyful-desktop/db.theme.joy")
        if os.path.exists(db_path):
            try:
                with open(db_path, 'r') as f:
                    content = f.read()
                    # Match patterns like: wallpaper.theme.artistic  "filename.jpg"
                    patterns = {
                        'artistic_wallpaper': rf"^wallpaper\.{theme_name}\.artistic\s+['\"]?([^'\"\s]+)['\"]?",
                        'interactive_wallpaper': rf"^wallpaper\.{theme_name}\.interactive\s+['\"]?([^'\"\s]+)['\"]?",
                        'artistic_button_style': rf"^ob_button_style\.{theme_name}\.artistic\s+['\"]?([^'\"\s]+)['\"]?",
                        'interactive_button_style': rf"^ob_button_style\.{theme_name}\.interactive\s+['\"]?([^'\"\s]+)['\"]?",
                    }
                    for key, pattern in patterns.items():
                        match = re.search(pattern, content, re.MULTILINE)
                        if match:
                            config[key] = match.group(1)
            except Exception as e:
                print(f"Error reading db.theme.joy: {e}")
        return config

class ThemeGenerator:
    """Logic for generating a theme folder from templates."""
    
    def __init__(self, script_dir):
        self.script_dir = script_dir

    def generate(self, name, config_data):
        """
        config_data = {
            'gtk': '...', 'icons': '...', 'font': '...',
            'tint2_glyph': '...',
            'button_style_art': '...', 'button_style_int': '...',
            'button_loc_art': '...', 'button_loc_int': '...',
            'colors_art': {'VAR_NAME': '#HEX'},
            'colors_int': {'VAR_NAME': '#HEX'},  # Optional override
            'assets': {'filename.jpg': 'source_path'}
        }
        }
        """
        prefix = JoyfulThemeLib.get_prefix(name)
        custom_themes_dir = os.path.join(self.script_dir, "custom-themes")
        target_dir = os.path.join(custom_themes_dir, name)
        
        os.makedirs(target_dir, exist_ok=True)
        
        # 1. Create env.joyfuld.snippet
        snippet_path = os.path.join(target_dir, "env.joyfuld.snippet")
        with open(snippet_path, "w") as f:
            f.write(f"# >~~~~~~~~~~~~~~~~~~~~~~~~~< {name} >~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~< Artistic Mode >~~~~~< #\n")
            
            colors_art = config_data.get('colors_art', {})
            # Cache values for inheritance if colors_int is not provided
            art_grad1 = colors_art.get("THEM_ART_TINT2_GRAD1", "#89b4fa")
            art_grad2 = colors_art.get("THEM_ART_TINT2_GRAD2", "#b4befe")
            art_dunst = colors_art.get("THEM_ART_DUNST_SMMRY", "#f5e0dc")
            art_menu_ttl = colors_art.get("THEM_ART_OB_MENU_TTL", "#f5e0dc")
            art_menu_itm = colors_art.get("THEM_ART_OB_MENU_ITM", "#89b4fa")

            for var, color in colors_art.items():
                var_name = var.replace("THEM_", f"{prefix}_")
                f.write(f"{var_name}='{color}'\n")
                
                if var == "THEM_ART_TINT2_GRAD1":
                    f.write(f"{prefix}_ART_ROFI_ACCNT1='{color}'\n")
                    f.write(f"{prefix}_ART_DUNST_PRGBR='{color}'\n")
                if var == "THEM_ART_TINT2_GRAD2":
                    f.write(f"{prefix}_ART_ROFI_ACCNT2='{color}'\n")

            f.write(f"{prefix}_ART_TINT2_GLYPH='{config_data.get('tint2_glyph', '')}'\n")

            # Interactive mode logic
            f.write(f"\n# >~~~~~~~~~~~~~~~~~~~~~~~~~< {name} >~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~< Interactive Mode >~~< #\n")
            colors_int = config_data.get('colors_int')
            
            if colors_int:
                # Use provided overrides
                for var, color in colors_int.items():
                    var_name = var.replace("THEM_", f"{prefix}_")
                    f.write(f"{var_name}='{color}'\n")
            else:
                # Inherit from Artistic
                f.write(f"{prefix}_INT_ROFI_ACCNT1='{art_grad1}'\n")
                f.write(f"{prefix}_INT_ROFI_ACCNT2='{art_grad2}'\n")
                f.write(f"{prefix}_INT_DUNST_SMMRY='{art_dunst}'\n")
                f.write(f"{prefix}_INT_DUNST_PRGBR='{art_grad1}'\n")
                f.write(f"{prefix}_INT_OB_MENU_TTL='{art_menu_ttl}'\n")
                f.write(f"{prefix}_INT_OB_MENU_ITM='{art_menu_itm}'\n")
            
            f.write(f"\n{prefix}_GTK='{config_data['gtk']}'\n")
            f.write(f"{prefix}_ICON='{config_data['icons']}'\n")
            f.write(f"{prefix}_FONT='{config_data['font']}'\n")
            f.write(f"{prefix}_OB_THEME_DIR='/usr/share/themes/{config_data['gtk']}/openbox-3'\n")

        # 2. Create db.theme.joy.snippet
        db_path = os.path.join(target_dir, "db.theme.joy.snippet")
        with open(db_path, "w") as f:
            f.write(f"ob_button_style.{name}.artistic='{config_data.get('button_style_art', 'circles-filled')}'\n")
            f.write(f"ob_button_style.{name}.interactive='{config_data.get('button_style_int', 'circles-outline')}'\n")
            f.write(f"ob_button_location.{name}.artistic='{config_data.get('button_loc_art', 'left')}'\n")
            f.write(f"ob_button_location.{name}.interactive='{config_data.get('button_loc_int', 'right')}'\n")
            f.write(f"wallpaper.{name}.artistic='{name}.artistic.jpg'\n")
            f.write(f"wallpaper.{name}.interactive='{name}.interactive.jpg'\n")

        # 3. Copy Assets
        os.makedirs(os.path.join(target_dir, "wallpapers"), exist_ok=True)
        os.makedirs(os.path.join(target_dir, "icons"), exist_ok=True)
        
        for filename, src in config_data['assets'].items():
            if src and os.path.exists(src):
                dest_subdir = "wallpapers" if filename.endswith(".jpg") else "icons"
                # Keep original standard names (artistic.jpg, etc) for the importer to handle
                shutil.copy2(src, os.path.join(target_dir, dest_subdir, filename))

        # 4. Copy Template configs
        template_path = os.path.join(self.script_dir, "joyful-theme-template")
        if os.path.exists(template_path):
            for sub in ["openbox", "rofi", "dunst", "tint2"]:
                src_sub = os.path.join(template_path, sub)
                dest_sub = os.path.join(target_dir, sub)
                if os.path.exists(src_sub):
                    if os.path.exists(dest_sub):
                        shutil.rmtree(dest_sub)
                    shutil.copytree(src_sub, dest_sub)
        else:
            print(f"Warning: Template path {template_path} not found. Skipping config copy.")
        
        return target_dir
