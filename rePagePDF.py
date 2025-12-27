import customtkinter as ctk
from tkinter import filedialog, messagebox
import fitz
from PIL import Image
import io
import os
import configparser

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class ConfigManager:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.lang_file = os.path.join(base_dir, "languages.ini")
        
        app_data = os.getenv('APPDATA')
        self.save_dir = os.path.join(app_data, "rePagePDF")
        
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

        self.config_file = os.path.join(self.save_dir, "settings.ini")
        
        self.config = configparser.ConfigParser()
        self.lang_config = configparser.ConfigParser()
        
        self.load_settings()
        
        self.current_lang_data = {}
        self.available_languages = ["English"]
        self.load_languages()

    def load_settings(self):
        if os.path.exists(self.config_file):
            try:
                self.config.read(self.config_file, encoding='utf-8')
            except:
                self.create_default_config()
        else:
            self.create_default_config()

    def create_default_config(self):
        self.config['General'] = {
            'language': 'English',
            'last_dir': '',
            'zoom': '0.2'
        }
        self.save_settings()

    def save_settings(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)

    def get_setting(self, key, default=None):
        return self.config.get('General', key, fallback=default)

    def set_setting(self, key, value):
        if 'General' not in self.config:
            self.config['General'] = {}
        self.config['General'][key] = str(value)
        self.save_settings()

    def load_languages(self):
        self.fallback_lang = {
            "window_title": "rePagePDF",
            "settings_title": "Settings",
            "menu_language": "Language",
            "menu_license": "About / License",
            "license_title": "License Information",
            "license_text": "This application uses PyMuPDF (AGPL/GPL license).\nThis software is free to use and modify.",
            "btn_open": "📂 Open Files",
            "btn_add": "➕ Add Files",
            "btn_save": "💾 Save PDF",
            "btn_cancel": "Cancel",
            "btn_create": "Create",
            "btn_apply": "Apply and Save",
            "btn_select_all": "✅ Select All",
            "btn_booklet": "📖 Create Booklet",
            "btn_delete": "❌ Delete (Del)",
            "lbl_save_settings": "Save Settings:",
            "lbl_zoom": "Zoom:",
            "lbl_actions": "Actions:",
            "lbl_rotate": "Rotate:",
            "lbl_hint": "Ctrl+Wheel: Zoom | Ctrl+A: Select All | Ctrl/Shift+Click: Select",
            "lbl_wait": "Please wait...",
            "lbl_saving": "Saving...",
            "lbl_preview": "Preview: {}/{}",
            "status_ready": "Ready",
            "status_loaded": "Loaded: {} pages",
            "status_error": "Error",
            "msg_success": "Success",
            "msg_saved": "File saved!",
            "msg_done": "Done!",
            "msg_restart_title": "Restart Required",
            "msg_restart_text": "Language changed to {}. Please restart the application.",
            "msg_pages_sheets": "Pages: {} | Sheets: {}",
            "settings_compression_title": "Compression Settings",
            "opt_params": "Optimization Parameters",
            "presets": "Presets:",
            "quality_jpeg": "JPEG Quality:",
            "max_side": "Max Side (px):",
            "preset_web": "Web (72dpi)",
            "preset_print": "Print (300dpi)",
            "preset_custom": "Custom",
            "comp_mode_lossless": "Lossless",
            "comp_mode_compressed": "Compressed",
            "booklet_title": "Booklet Settings",
            "print_params": "Print Parameters",
            "paper_format": "Paper Format:",
            "reading_dir": "Reading Direction:",
            "dir_ltr": "LTR (Left-Right)",
            "dir_rtl": "RTL (Right-Left)",
            "binding": "Binding (Signatures)",
            "split_parts": "Split into parts",
            "sheets_per_part": "Sheets per part:",
            "warn_sheets": "⚠ >20 sheets. Splitting recommended.",
            "printer_hint": "ℹ Print: Double-sided, flip on short edge",
            "file_supported": "Supported Files",
            "file_pdf": "PDF Files",
            "file_img": "Images"
        }

        if os.path.exists(self.lang_file):
            try:
                self.lang_config.read(self.lang_file, encoding='utf-8')
                self.available_languages = self.lang_config.sections()
                if not self.available_languages:
                    self.available_languages = ["English"]
            except Exception as e:
                print(f"Error loading languages: {e}")
        
        current = self.get_setting('language', 'English')
        if current not in self.available_languages:
            current = "English"
            if self.available_languages:
                current = self.available_languages[0]
        
        self.set_language(current)

    def set_language(self, lang_name):
        self.current_lang_name = lang_name
        if lang_name in self.lang_config:
            self.current_lang_data = dict(self.lang_config[lang_name])
        else:
            self.current_lang_data = self.fallback_lang
        self.set_setting('language', lang_name)

    def get_text(self, key):
        return self.current_lang_data.get(key, self.fallback_lang.get(key, key))

cfg = ConfigManager()

class MainSettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(cfg.get_text("settings_title"))
        self.geometry("300x200")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.parent_app = parent

        ctk.CTkLabel(self, text=cfg.get_text("menu_language"), font=("Arial", 14, "bold")).pack(pady=(20, 5))
        
        self.cmb_lang = ctk.CTkOptionMenu(self, values=cfg.available_languages, command=self.on_lang_change)
        self.cmb_lang.set(cfg.current_lang_name)
        self.cmb_lang.pack(pady=10)
        
        ctk.CTkFrame(self, height=2, fg_color="gray80").pack(fill="x", padx=20, pady=10)

        self.btn_about = ctk.CTkButton(self, text=cfg.get_text("menu_license"), command=self.show_license)
        self.btn_about.pack(pady=10)

    def on_lang_change(self, choice):
        cfg.set_language(choice)
        self.parent_app.refresh_ui_text()

    def show_license(self):
        msg = f"{cfg.get_text('license_title')}\n\n{cfg.get_text('license_text')}"
        messagebox.showinfo("License", msg)

class CompressionSettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(cfg.get_text("settings_compression_title"))
        self.geometry("420x350")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.settings = None 
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)

        self.txt_web = cfg.get_text("preset_web")
        self.txt_print = cfg.get_text("preset_print")
        self.txt_custom = cfg.get_text("preset_custom")

        ctk.CTkLabel(self, text=cfg.get_text("opt_params"), font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=15)

        ctk.CTkLabel(self, text=cfg.get_text("presets")).grid(row=1, column=0, padx=20, sticky="e")
        self.cmb_presets = ctk.CTkOptionMenu(self, values=[self.txt_web, self.txt_print, self.txt_custom], 
                                             command=self.on_preset_change)
        self.cmb_presets.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
        self.cmb_presets.set(self.txt_web)

        ctk.CTkLabel(self, text=cfg.get_text("quality_jpeg")).grid(row=2, column=0, padx=20, sticky="e")
        self.lbl_quality_val = ctk.CTkLabel(self, text="70")
        self.lbl_quality_val.grid(row=2, column=1, padx=(20, 10), sticky="w")
        
        self.slider_quality = ctk.CTkSlider(self, from_=10, to=100, number_of_steps=90, command=self.update_labels)
        self.slider_quality.grid(row=3, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")

        ctk.CTkLabel(self, text=cfg.get_text("max_side")).grid(row=4, column=0, padx=20, sticky="e")
        self.lbl_res_val = ctk.CTkLabel(self, text="1200 px")
        self.lbl_res_val.grid(row=4, column=1, padx=(20, 10), sticky="w")

        self.slider_res = ctk.CTkSlider(self, from_=600, to=3000, number_of_steps=24, command=self.update_labels)
        self.slider_res.grid(row=5, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")

        self.btn_ok = ctk.CTkButton(self, text=cfg.get_text("btn_apply"), command=self.on_ok)
        self.btn_ok.grid(row=6, column=0, columnspan=2, padx=50, pady=20, sticky="ew")

        self.on_preset_change(self.txt_web)

    def update_labels(self, value=None):
        q = int(self.slider_quality.get())
        r = int(self.slider_res.get())
        self.lbl_quality_val.configure(text=str(q))
        self.lbl_res_val.configure(text=f"{r} px")

    def on_preset_change(self, choice):
        if choice == self.txt_web:
            self.slider_quality.set(70)
            self.slider_res.set(1200)
        elif choice == self.txt_print:
            self.slider_quality.set(85)
            self.slider_res.set(2400)
        self.update_labels()

    def on_ok(self):
        self.settings = {
            "quality": int(self.slider_quality.get()),
            "max_res": int(self.slider_res.get())
        }
        self.destroy()

class BookletOptionsDialog(ctk.CTkToplevel):
    def __init__(self, parent, page_count):
        super().__init__(parent)
        self.title(cfg.get_text("booklet_title"))
        self.geometry("380x460")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.result = None
        self.page_count = page_count
        self.estimated_sheets = (page_count + 3) // 4 

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text=cfg.get_text("print_params"), font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(15, 5))
        
        info_text = cfg.get_text("msg_pages_sheets").format(page_count, self.estimated_sheets)
        ctk.CTkLabel(self, text=info_text, text_color="gray", font=("Arial", 11)).grid(row=1, column=0, columnspan=2, pady=(0, 10))

        ctk.CTkLabel(self, text=cfg.get_text("paper_format")).grid(row=2, column=0, padx=20, sticky="w")
        self.cmb_format = ctk.CTkOptionMenu(self, values=["A4", "Letter"], height=28, width=150)
        self.cmb_format.grid(row=2, column=1, padx=20, pady=5, sticky="e")
        self.cmb_format.set("A4")

        self.ltr_txt = cfg.get_text("dir_ltr")
        self.rtl_txt = cfg.get_text("dir_rtl")
        self.dir_map = {self.ltr_txt: "LTR", self.rtl_txt: "RTL"}

        ctk.CTkLabel(self, text=cfg.get_text("reading_dir")).grid(row=3, column=0, padx=20, sticky="w")
        self.cmb_direction = ctk.CTkOptionMenu(self, values=[self.ltr_txt, self.rtl_txt], height=28, width=150)
        self.cmb_direction.grid(row=3, column=1, padx=20, pady=5, sticky="e")
        self.cmb_direction.set(self.ltr_txt)

        ctk.CTkFrame(self, height=2, fg_color="gray80").grid(row=4, column=0, columnspan=2, sticky="ew", padx=20, pady=10)

        ctk.CTkLabel(self, text=cfg.get_text("binding"), font=("Arial", 12, "bold")).grid(row=5, column=0, columnspan=2, pady=(0, 5))

        self.use_signatures_var = ctk.BooleanVar(value=False)
        self.chk_signatures = ctk.CTkSwitch(self, text=cfg.get_text("split_parts"), font=("Arial", 12),
                                            variable=self.use_signatures_var, 
                                            command=self.toggle_signatures)
        self.chk_signatures.grid(row=6, column=0, columnspan=2, pady=5)

        self.frame_slider = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_slider.grid(row=7, column=0, columnspan=2, sticky="ew", padx=10, pady=0)
        self.frame_slider.grid_columnconfigure(1, weight=1)

        self.lbl_sheets_title = ctk.CTkLabel(self.frame_slider, text=cfg.get_text("sheets_per_part"), text_color="gray", font=("Arial", 11))
        self.lbl_sheets_title.grid(row=0, column=0, padx=10, sticky="w")
        
        self.lbl_sheets_val = ctk.CTkLabel(self.frame_slider, text="12", font=("Arial", 12, "bold"), text_color="gray")
        self.lbl_sheets_val.grid(row=0, column=2, padx=10, sticky="e")

        self.slider_sheets = ctk.CTkSlider(self.frame_slider, from_=4, to=40, number_of_steps=36, height=16, command=self.update_sheet_label)
        self.slider_sheets.set(12) 
        self.slider_sheets.grid(row=1, column=0, columnspan=3, padx=10, pady=(5, 0), sticky="ew")

        self.lbl_warning = ctk.CTkLabel(self, text="", font=("Arial", 10), text_color="#E0a800")
        self.lbl_warning.grid(row=8, column=0, columnspan=2, pady=(5, 0))

        if self.estimated_sheets > 20:
            self.use_signatures_var.set(True)
            self.lbl_warning.configure(text=cfg.get_text("warn_sheets"))
        
        ctk.CTkLabel(self, text=cfg.get_text("printer_hint"), font=("Arial", 10), text_color="gray40").grid(row=9, column=0, columnspan=2, pady=(15, 0))

        self.btn_cancel = ctk.CTkButton(self, text=cfg.get_text("btn_cancel"), fg_color="transparent", border_width=1, command=self.destroy, height=32)
        self.btn_cancel.grid(row=10, column=0, padx=20, pady=15, sticky="ew")

        self.btn_ok = ctk.CTkButton(self, text=cfg.get_text("btn_create"), command=self.on_ok, height=32)
        self.btn_ok.grid(row=10, column=1, padx=20, pady=15, sticky="ew")
        
        self.toggle_signatures()

    def update_sheet_label(self, val):
        self.lbl_sheets_val.configure(text=str(int(val)))

    def toggle_signatures(self):
        is_active = self.use_signatures_var.get()
        state = "normal" if is_active else "disabled"
        color = ("black", "white") if is_active else "gray"
        self.slider_sheets.configure(state=state)
        self.lbl_sheets_title.configure(text_color=color)
        self.lbl_sheets_val.configure(text_color=color)

    def on_ok(self):
        self.result = {
            "format": self.cmb_format.get(),
            "direction": self.dir_map.get(self.cmb_direction.get(), "LTR"),
            "use_signatures": self.use_signatures_var.get(),
            "sheets_per_sig": int(self.slider_sheets.get())
        }
        self.destroy()

class PrinterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(cfg.get_text("window_title"))
        self.geometry("1200x850")
        self.after(0, lambda: self.state("zoomed"))
        
        self.doc = None
        self.pages_order = []
        self.page_rotations = {}
        self.selected_indices = set() 
        self.last_selected_index = None 
        self.zoom_scale = float(cfg.get_setting("zoom", 0.2))
        self.min_zoom, self.max_zoom = 0.05, 0.8
        self.buttons_list = []
        self.drag_data = {"active": False, "start_x": 0, "start_y": 0, "target_index": None, "pending_select": None}
        self.autoscroll_active = False
        self.compression_mode_index = 0
        
        self._setup_layout()
        self._setup_bindings()
        
        self.refresh_ui_text()
        
    def _setup_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkScrollableFrame(self, width=260, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.logo_frame.grid(row=0, column=0, padx=10, pady=(20, 20), sticky="ew")
        
        self.logo = ctk.CTkLabel(self.logo_frame, text="rePagePDF", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo.grid(row=0, column=0, sticky="w", padx=5)

        self.btn_settings = ctk.CTkButton(self.logo_frame, text="⚙", width=35, height=35, 
                                          command=self.open_settings, 
                                          fg_color="#3B8ED0", text_color="white")
        self.btn_settings.grid(row=0, column=1, padx=(10, 0))

        self.btn_open = ctk.CTkButton(self.sidebar, text=cfg.get_text("btn_open"), command=self.open_file, fg_color="green")
        self.btn_open.grid(row=1, column=0, padx=10, pady=10)

        self.btn_add = ctk.CTkButton(self.sidebar, text=cfg.get_text("btn_add"), command=self.add_file, fg_color="#3B8ED0", state="disabled")
        self.btn_add.grid(row=2, column=0, padx=10, pady=10)

        self.lbl_save_set = ctk.CTkLabel(self.sidebar, text=cfg.get_text("lbl_save_settings"), text_color="gray")
        self.lbl_save_set.grid(row=3, column=0, pady=(20, 5))

        self.compression_var = ctk.StringVar(value=cfg.get_text("comp_mode_lossless"))
        self.cmb_compression = ctk.CTkOptionMenu(self.sidebar, 
                                                 values=[cfg.get_text("comp_mode_lossless"), cfg.get_text("comp_mode_compressed")], 
                                                 variable=self.compression_var,
                                                 command=self.on_compression_change)
        self.cmb_compression.grid(row=4, column=0, padx=10, pady=5)

        self.btn_save = ctk.CTkButton(self.sidebar, text=cfg.get_text("btn_save"), command=self.save_file, state="disabled")
        self.btn_save.grid(row=5, column=0, padx=10, pady=10)
        
        self.lbl_zoom = ctk.CTkLabel(self.sidebar, text=cfg.get_text("lbl_zoom"), text_color="gray")
        self.lbl_zoom.grid(row=6, column=0, pady=(20, 5))
        
        self.zoom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.zoom_frame.grid(row=7, column=0, padx=10, pady=5)
        
        ctk.CTkButton(self.zoom_frame, text="-", width=30, command=self.zoom_out).pack(side="left", padx=5)
        self.slider_zoom = ctk.CTkSlider(self.zoom_frame, from_=self.min_zoom, to=self.max_zoom, width=100, command=self.slider_event)
        self.slider_zoom.set(self.zoom_scale)
        self.slider_zoom.pack(side="left", padx=5)
        ctk.CTkButton(self.zoom_frame, text="+", width=30, command=self.zoom_in).pack(side="left", padx=5)

        self.lbl_actions = ctk.CTkLabel(self.sidebar, text=cfg.get_text("lbl_actions"), text_color="gray")
        self.lbl_actions.grid(row=8, column=0, pady=(20, 5))

        self.btn_select_all_ui = ctk.CTkButton(self.sidebar, text=cfg.get_text("btn_select_all"), command=self.select_all, state="disabled")
        self.btn_select_all_ui.grid(row=9, column=0, padx=10, pady=5)
        
        self.btn_booklet = ctk.CTkButton(self.sidebar, text=cfg.get_text("btn_booklet"), command=self.create_booklet, state="disabled", fg_color="#E0a800", text_color="black")
        self.btn_booklet.grid(row=10, column=0, padx=10, pady=5)

        self.nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.nav_frame.grid(row=11, column=0, padx=10, pady=5)
        
        self.btn_up = ctk.CTkButton(self.nav_frame, text="⬆", width=60, command=lambda: self.move_pages_btn(-1), state="disabled")
        self.btn_up.pack(side="left", padx=5)

        self.btn_down = ctk.CTkButton(self.nav_frame, text="⬇", width=60, command=lambda: self.move_pages_btn(1), state="disabled")
        self.btn_down.pack(side="left", padx=5)

        self.lbl_rotate = ctk.CTkLabel(self.sidebar, text=cfg.get_text("lbl_rotate"), font=("Arial", 11), text_color="gray")
        self.lbl_rotate.grid(row=13, column=0, pady=(10, 0))
        
        self.rotate_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.rotate_frame.grid(row=14, column=0, padx=10, pady=5)

        self.btn_rot_ccw = ctk.CTkButton(self.rotate_frame, text="⟲", width=40, command=lambda: self.rotate_pages(-90), state="disabled")
        self.btn_rot_ccw.pack(side="left", padx=5)
        self.btn_rot_180 = ctk.CTkButton(self.rotate_frame, text="180°", width=40, command=lambda: self.rotate_pages(180), state="disabled")
        self.btn_rot_180.pack(side="left", padx=5)
        self.btn_rot_cw = ctk.CTkButton(self.rotate_frame, text="⟳", width=40, command=lambda: self.rotate_pages(90), state="disabled")
        self.btn_rot_cw.pack(side="left", padx=5)

        self.btn_delete = ctk.CTkButton(self.sidebar, text=cfg.get_text("btn_delete"), fg_color="red", command=self.delete_pages, state="disabled")
        self.btn_delete.grid(row=15, column=0, padx=10, pady=20)

        self.lbl_hint = ctk.CTkLabel(self.sidebar, text=cfg.get_text("lbl_hint"), font=("Arial", 10), text_color="gray")
        self.lbl_hint.grid(row=16, column=0, pady=5)

        self.lbl_status = ctk.CTkLabel(self.sidebar, text=cfg.get_text("status_ready"), font=("Arial", 12))
        self.lbl_status.grid(row=17, column=0, pady=20, sticky="s")

        self.right_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.right_panel.grid_rowconfigure(1, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)

        self.scroll_sensor_top = ctk.CTkFrame(self.right_panel, height=25, corner_radius=5, fg_color=("gray85", "gray25"))
        self.scroll_sensor_top.grid(row=0, column=0, sticky="ew", pady=(0, 2))

        self.grid_area = ctk.CTkScrollableFrame(self.right_panel)
        self.grid_area.grid(row=1, column=0, sticky="nsew")

        self.scroll_sensor_bottom = ctk.CTkFrame(self.right_panel, height=25, corner_radius=5, fg_color=("gray85", "gray25"))
        self.scroll_sensor_bottom.grid(row=2, column=0, sticky="ew", pady=(2, 0))

    def _setup_bindings(self):
        self.bind("<Delete>", lambda event: self.delete_pages())
        self.bind("<Control-MouseWheel>", self.on_mouse_zoom)
        self.bind("<Control-Button-4>", self.on_mouse_zoom)
        self.bind("<Control-Button-5>", self.on_mouse_zoom)
        self.bind("<Control-a>", self.select_all)
        self.bind("<Control-A>", self.select_all)

    def open_settings(self):
        MainSettingsDialog(self)

    def on_compression_change(self, choice):
        vals = [cfg.get_text("comp_mode_lossless"), cfg.get_text("comp_mode_compressed")]
        try:
            self.compression_mode_index = vals.index(choice)
        except:
            self.compression_mode_index = 0

    def refresh_ui_text(self):
        self.title(cfg.get_text("window_title"))
        self.btn_open.configure(text=cfg.get_text("btn_open"))
        self.btn_add.configure(text=cfg.get_text("btn_add"))
        self.btn_save.configure(text=cfg.get_text("btn_save"))
        self.btn_booklet.configure(text=cfg.get_text("btn_booklet"))
        self.btn_delete.configure(text=cfg.get_text("btn_delete"))
        self.btn_select_all_ui.configure(text=cfg.get_text("btn_select_all"))
        self.lbl_save_set.configure(text=cfg.get_text("lbl_save_settings"))
        self.lbl_zoom.configure(text=cfg.get_text("lbl_zoom"))
        self.lbl_actions.configure(text=cfg.get_text("lbl_actions"))
        self.lbl_rotate.configure(text=cfg.get_text("lbl_rotate"))
        self.lbl_hint.configure(text=cfg.get_text("lbl_hint"))
        
        if not self.pages_order:
            self.lbl_status.configure(text=cfg.get_text("status_ready"))
        else:
            self.lbl_status.configure(text=cfg.get_text("status_loaded").format(len(self.pages_order)))
        
        vals = [cfg.get_text("comp_mode_lossless"), cfg.get_text("comp_mode_compressed")]
        self.cmb_compression.configure(values=vals)
        self.compression_var.set(vals[self.compression_mode_index])

    def _get_file_types(self):
        img_exts = "*.jpg *.jpeg *.png *.bmp *.tiff *.tif *.gif"
        return [
            (cfg.get_text("file_supported"), f"*.pdf {img_exts} *.cbz *.cbr"), 
            (cfg.get_text("file_pdf"), "*.pdf"), 
            (cfg.get_text("file_img"), img_exts)
        ]

    def _load_doc_safely(self, path):
        try:
            doc = fitz.open(path)
            if doc.is_pdf: return doc
            pdf_bytes = doc.convert_to_pdf()
            pdf_doc = fitz.open("pdf", pdf_bytes)
            doc.close()
            return pdf_doc
        except Exception as e:
            raise Exception(f"Error {path}: {e}")

    def update_zoom_ui(self):
        self.slider_zoom.set(self.zoom_scale)
        cfg.set_setting("zoom", self.zoom_scale)
        self.refresh_grid()

    def slider_event(self, value):
        self.zoom_scale = float(value)
        cfg.set_setting("zoom", self.zoom_scale)
        self.refresh_grid()

    def zoom_in(self):
        if self.zoom_scale < self.max_zoom:
            self.zoom_scale = min(self.max_zoom, self.zoom_scale + 0.05)
            self.update_zoom_ui()

    def zoom_out(self):
        if self.zoom_scale > self.min_zoom:
            self.zoom_scale = max(self.min_zoom, self.zoom_scale - 0.05)
            self.update_zoom_ui()

    def on_mouse_zoom(self, event):
        if event.num == 5 or event.delta < 0: self.zoom_out()
        elif event.num == 4 or event.delta > 0: self.zoom_in()

    def open_file(self):
        initial_dir = cfg.get_setting("last_dir", "")
        paths = filedialog.askopenfilenames(filetypes=self._get_file_types(), initialdir=initial_dir)
        if not paths: return
        
        cfg.set_setting("last_dir", os.path.dirname(paths[0]))
        
        p_window, p_bar, p_lbl, p_perc = self.create_progress_window(cfg.get_text("window_title"))
        self.update()
        
        try:
            if self.doc: self.doc.close()
            self.doc = fitz.open()
            
            for i, path in enumerate(paths):
                sub_doc = self._load_doc_safely(path)
                self.doc.insert_pdf(sub_doc)
                sub_doc.close()
                p_bar.set((i + 1) / len(paths) * 0.2)
                self.update()
            
            self.pages_order = list(range(len(self.doc)))
            self.page_rotations = {i: 0 for i in range(len(self.doc))}
            self.selected_indices.clear()
            self.last_selected_index = None
            
            self.btn_save.configure(state="normal")
            self.btn_add.configure(state="normal")
            if self.pages_order:
                self.btn_select_all_ui.configure(state="normal")
                self.btn_booklet.configure(state="normal")
            
            self.refresh_grid(lambda c, t: self.update_prog(p_bar, p_lbl, p_perc, c, t))
            self.lbl_status.configure(text=cfg.get_text("status_loaded").format(len(self.pages_order)))
            
        except Exception as e:
            messagebox.showerror(cfg.get_text("status_error"), str(e))
        finally:
            p_window.destroy()

    def update_prog(self, bar, lbl, perc, curr, total):
        prog = 0.2 + (curr / total) * 0.8
        bar.set(prog)
        lbl.configure(text=cfg.get_text("lbl_preview").format(curr, total))
        perc.configure(text=f"{int(prog * 100)}%")
        self.update()

    def add_file(self):
        if self.doc is None: return self.open_file()
        paths = filedialog.askopenfilenames(filetypes=self._get_file_types(), initialdir=cfg.get_setting("last_dir"))
        if not paths: return

        p_window, p_bar, p_lbl, p_perc = self.create_progress_window(cfg.get_text("btn_add"))
        try:
            start_idx = len(self.doc)
            for i, path in enumerate(paths):
                sub = self._load_doc_safely(path)
                self.doc.insert_pdf(sub)
                sub.close()
                p_bar.set((i+1)/len(paths)*0.2)
                self.update()
            
            new_indices = list(range(start_idx, len(self.doc)))
            self.pages_order.extend(new_indices)
            for i in new_indices: self.page_rotations[i] = 0
            
            self.refresh_grid(lambda c, t: self.update_prog(p_bar, p_lbl, p_perc, c, t))
            self.lbl_status.configure(text=cfg.get_text("status_loaded").format(len(self.pages_order)))
        except Exception as e:
            messagebox.showerror(cfg.get_text("status_error"), str(e))
        finally:
            p_window.destroy()

    def refresh_grid(self, progress_callback=None):
        for btn in self.buttons_list: btn.destroy()
        self.buttons_list = []

        if not self.pages_order: return

        area_width = self.grid_area.winfo_width()
        if area_width < 100: area_width = 800
        
        try:
            p0 = self.doc.load_page(self.pages_order[0])
            w0 = p0.rect.width if self.page_rotations.get(self.pages_order[0],0)%180==0 else p0.rect.height
        except: w0 = 595
        
        scaled_w = w0 * self.zoom_scale
        cols = max(1, int((area_width-30) // (scaled_w+30)))
        
        self.grid_area.grid_columnconfigure(list(range(cols)), weight=1)
        self.grid_area.grid_columnconfigure(list(range(cols, 20)), weight=0)

        matrix = fitz.Matrix(self.zoom_scale, self.zoom_scale)
        total = len(self.pages_order)

        for idx, original_idx in enumerate(self.pages_order):
            if progress_callback: progress_callback(idx + 1, total)

            try:
                page = self.doc.load_page(original_idx)
                page.set_rotation(self.page_rotations.get(original_idx, 0))
                pix = page.get_pixmap(matrix=matrix)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(pix.width, pix.height))

                btn = ctk.CTkButton(self.grid_area, image=ctk_img, text=f"{idx+1}", compound="top",
                                    fg_color="transparent", border_width=0, border_color="orange",
                                    width=pix.width, height=pix.height + 30)
                
                btn.bind("<Button-1>", lambda e, i=idx: self.on_press(e, i))
                btn.bind("<B1-Motion>", self.on_drag_motion)
                btn.bind("<ButtonRelease-1>", self.on_release)
                
                btn.grid(row=idx//cols, column=idx%cols, padx=10, pady=10)
                self.buttons_list.append(btn)
            except Exception as e: print(f"Err pg {idx}: {e}")

        self.update_visuals()

    def update_visuals(self):
        for i, btn in enumerate(self.buttons_list):
            if self.drag_data["active"] and i == self.drag_data["target_index"]:
                btn.configure(border_color="#1F6AA5", border_width=4)
            elif i in self.selected_indices:
                btn.configure(fg_color="orange", border_color="orange", border_width=3)
            else:
                btn.configure(fg_color="transparent", border_color="orange", border_width=0)
        
        state = "normal" if self.selected_indices else "disabled"
        self.btn_up.configure(state=state)
        self.btn_down.configure(state=state)
        self.btn_delete.configure(state=state)
        self.btn_rot_ccw.configure(state=state)
        self.btn_rot_cw.configure(state=state)
        self.btn_rot_180.configure(state=state)

    def select_all(self, event=None):
        if not self.pages_order: return
        self.selected_indices = set(range(len(self.pages_order)))
        self.update_visuals()

    def on_press(self, event, index):
        self.drag_data.update({"start_x": event.x, "start_y": event.y, "active": False, "pending_select": None})
        is_ctrl = (event.state & 0x0004) or (event.state & 0x20000)
        is_shift = (event.state & 0x0001)

        if index in self.selected_indices and not (is_ctrl or is_shift):
            self.drag_data["pending_select"] = index
            return
        self.handle_selection(index, is_ctrl, is_shift)

    def handle_selection(self, index, is_ctrl, is_shift):
        if is_shift and self.last_selected_index is not None:
            s, e = min(self.last_selected_index, index), max(self.last_selected_index, index)
            if not is_ctrl: self.selected_indices.clear()
            self.selected_indices.update(range(s, e + 1))
        elif is_ctrl:
            if index in self.selected_indices: self.selected_indices.remove(index)
            else: 
                self.selected_indices.add(index)
                self.last_selected_index = index
        else:
            self.selected_indices = {index}
            self.last_selected_index = index
        self.update_visuals()

    def on_drag_motion(self, event):
        if not self.drag_data["active"]:
            if max(abs(event.x - self.drag_data["start_x"]), abs(event.y - self.drag_data["start_y"])) > 5:
                self.drag_data["active"] = True
        
        if self.drag_data["active"]:
            widget = self.winfo_containing(*self.winfo_pointerxy())
            target = None
            curr = widget
            while curr:
                if curr in self.buttons_list:
                    target = self.buttons_list.index(curr)
                    break
                curr = curr.master
            
            if target is not None and target != self.drag_data["target_index"]:
                self.drag_data["target_index"] = target
                self.update_visuals()
            
            y_root = self.winfo_pointery()
            if y_root < self.scroll_sensor_top.winfo_rooty() + 25: self._do_autoscroll(-0.005)
            elif y_root > self.scroll_sensor_bottom.winfo_rooty(): self._do_autoscroll(0.005)
            else: self.autoscroll_active = False

    def _do_autoscroll(self, speed):
        if not self.autoscroll_active:
            self.autoscroll_active = True
            def scroll():
                if not self.autoscroll_active: return
                self.grid_area._parent_canvas.yview_scroll(int(speed*100), "units")
                self.after(20, scroll)
            scroll()

    def on_release(self, event):
        self.autoscroll_active = False
        if self.drag_data["active"] and self.drag_data["target_index"] is not None:
            self.execute_drag_move(self.drag_data["target_index"])
        elif self.drag_data["pending_select"] is not None:
            self.selected_indices = {self.drag_data["pending_select"]}
            self.last_selected_index = self.drag_data["pending_select"]
        
        self.drag_data["active"] = False
        self.drag_data["target_index"] = None
        self.update_visuals()

    def execute_drag_move(self, target):
        moving = sorted(list(self.selected_indices))
        data_to_move = [self.pages_order[i] for i in moving]
        
        for i in sorted(moving, reverse=True): del self.pages_order[i]
        
        shift = sum(1 for x in moving if x < target)
        new_pos = max(0, min(len(self.pages_order), target - shift + (1 if target > moving[0] else 0)))
        
        for item in reversed(data_to_move): self.pages_order.insert(new_pos, item)
        self.selected_indices = set(range(new_pos, new_pos + len(data_to_move)))
        self.refresh_grid()

    def move_pages_btn(self, direction):
        if not self.selected_indices: return
        indices = sorted(list(self.selected_indices), reverse=(direction > 0))
        if (direction == -1 and indices[-1] == 0) or (direction == 1 and indices[0] == len(self.pages_order)-1): return

        new_sel = set()
        for idx in indices:
            tgt = idx + direction
            self.pages_order[idx], self.pages_order[tgt] = self.pages_order[tgt], self.pages_order[idx]
            new_sel.add(tgt)
        self.selected_indices = new_sel
        self.refresh_grid()

    def delete_pages(self):
        for i in sorted(list(self.selected_indices), reverse=True): del self.pages_order[i]
        self.selected_indices.clear()
        self.refresh_grid()
        self.lbl_status.configure(text=cfg.get_text("status_loaded").format(len(self.pages_order)))

    def rotate_pages(self, angle):
        for idx in self.selected_indices:
            real_pg = self.pages_order[idx]
            self.page_rotations[real_pg] = (self.page_rotations[real_pg] + angle) % 360
        self.refresh_grid()

    def create_booklet(self):
        if not self.pages_order: return
        dialog = BookletOptionsDialog(self, len(self.pages_order))
        self.wait_window(dialog)
        if not dialog.result: return
        
        sets = dialog.result
        save_path = None
        if sets['use_signatures']:
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[(cfg.get_text("file_pdf"), "*.pdf")])
            if not save_path: return

        p_window, p_bar, p_lbl, p_perc = self.create_progress_window(cfg.get_text("btn_booklet"))
        try:
            temp = fitz.open()
            for idx in self.pages_order:
                temp.insert_pdf(self.doc, from_page=idx, to_page=idx)
                if self.page_rotations[idx] != 0: temp[-1].set_rotation(self.page_rotations[idx])
            
            sheet_w, sheet_h = (841.89, 595.28) if sets['format'] == "A4" else (792.0, 612.0)
            is_rtl = (sets['direction'] == "RTL")
            total_pg = len(temp)
            chunk = sets['sheets_per_sig'] * 4 if sets['use_signatures'] else (total_pg + (4 - total_pg % 4) if total_pg % 4 else total_pg)
            if chunk == 0: chunk = 4
            
            final_doc = fitz.open()
            
            for start in range(0, total_pg, chunk):
                end = min(start + chunk, total_pg)
                sig_doc = fitz.open()
                sub = list(range(start, end))
                while len(sub) % 4 != 0: sub.append(None)
                
                queue = sub.copy()
                while queue:
                    pg = sig_doc.new_page(width=sheet_w, height=sheet_h)
                    r_left = fitz.Rect(0, 0, sheet_w/2, sheet_h)
                    r_right = fitz.Rect(sheet_w/2, 0, sheet_w, sheet_h)
                    
                    p1, p4 = queue.pop(0), queue.pop(-1)
                    if is_rtl: p1, p4 = p4, p1 

                    if p4 is not None: pg.show_pdf_page(r_left, temp, p4, keep_proportion=True)
                    if p1 is not None: pg.show_pdf_page(r_right, temp, p1, keep_proportion=True)
                    
                    if not queue: break
                    
                    pg_back = sig_doc.new_page(width=sheet_w, height=sheet_h)
                    p2, p3 = queue.pop(0), queue.pop(-1)
                    if is_rtl: p2, p3 = p3, p2
                    
                    if p2 is not None: pg_back.show_pdf_page(r_left, temp, p2, keep_proportion=True)
                    if p3 is not None: pg_back.show_pdf_page(r_right, temp, p3, keep_proportion=True)

                if sets['use_signatures'] and save_path:
                    rt, ex = os.path.splitext(save_path)
                    sig_doc.save(f"{rt}_part_{(start//chunk)+1}{ex}")
                
                final_doc.insert_pdf(sig_doc)
                sig_doc.close()
                p_bar.set(end/total_pg)
                self.update()

            temp.close()
            if self.doc: self.doc.close()
            self.doc = final_doc
            self.pages_order = list(range(len(self.doc)))
            self.page_rotations = {i: 0 for i in range(len(self.doc))}
            self.selected_indices.clear()
            self.refresh_grid()
            messagebox.showinfo(cfg.get_text("msg_success"), cfg.get_text("msg_done"))

        except Exception as e:
            messagebox.showerror(cfg.get_text("status_error"), str(e))
        finally:
            p_window.destroy()

    def save_file(self):
        if not self.pages_order: return
        comp_sets = {"quality": 70, "max_res": 1200}
        if self.compression_mode_index == 1:
            dlg = CompressionSettingsDialog(self)
            self.wait_window(dlg)
            if dlg.settings: comp_sets = dlg.settings
            else: return

        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[(cfg.get_text("file_pdf"), "*.pdf")])
        if not path: return

        p_window, p_bar, p_lbl, p_perc = self.create_progress_window(cfg.get_text("btn_save"))
        try:
            out = fitz.open()
            for i, idx in enumerate(self.pages_order):
                out.insert_pdf(self.doc, from_page=idx, to_page=idx)
                if self.page_rotations[idx]: out[-1].set_rotation(self.page_rotations[idx])
                p_bar.set((i+1)/len(self.pages_order)*0.5)
                self.update()

            if self.compression_mode_index == 1:
                processed = set()
                for pg in out:
                    for img in pg.get_images():
                        xref = img[0]
                        if xref in processed: continue
                        processed.add(xref)
                        try:
                            pix = fitz.Pixmap(out, xref)
                            if pix.width > comp_sets['max_res'] or pix.height > comp_sets['max_res']:
                                if pix.n > 3: pix = fitz.Pixmap(fitz.csRGB, pix)
                                ratio = comp_sets['max_res'] / max(pix.width, pix.height)
                                new_w, new_h = int(pix.width*ratio), int(pix.height*ratio)
                                pil = Image.open(io.BytesIO(pix.tobytes("png"))).resize((new_w, new_h), Image.LANCZOS)
                                buf = io.BytesIO()
                                pil.save(buf, format="JPEG", quality=comp_sets['quality'])
                                pg.replace_image(xref, stream=buf.getvalue())
                        except: pass
            
            p_lbl.configure(text=cfg.get_text("lbl_saving"))
            out.save(path, garbage=4, deflate=True)
            out.close()
            messagebox.showinfo(cfg.get_text("msg_success"), cfg.get_text("msg_saved"))
            
        except Exception as e:
            messagebox.showerror(cfg.get_text("status_error"), str(e))
        finally:
            p_window.destroy()

    def create_progress_window(self, title):
        w = ctk.CTkToplevel(self)
        w.title(title)
        w.geometry("300x150")
        w.transient(self)
        w.grab_set()
        ctk.CTkLabel(w, text=cfg.get_text("lbl_wait"), font=("Arial", 14)).pack(pady=(20, 10))
        bar = ctk.CTkProgressBar(w, width=250)
        bar.pack(pady=10)
        bar.set(0)
        perc = ctk.CTkLabel(w, text="0%", text_color="gray")
        perc.pack(pady=5)
        return w, bar, w.winfo_children()[0], perc

if __name__ == "__main__":
    app = PrinterApp()
    app.mainloop()
