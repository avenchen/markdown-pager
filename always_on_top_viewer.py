import json
import pathlib
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Dict, List, Optional


class MarkdownPager:
    CONFIG_FILE = pathlib.Path("config.json")
    PALETTE = {
        "background": "#0f1624",
        "panel": "#1b2335",
        "toolbar": "#222d43",
        "button": "#2f3d58",
        "button_hover": "#3c4d6e",
        "accent": "#5dd5ff",
        "text_primary": "#f4f7ff",
        "text_secondary": "#9fb4d9",
        "border": "#34425f",
        "close_bg": "#ff5f6d",
        "close_hover": "#ff7f84",
        "scrollbar": "#6fd4ff",
        "scrollbar_active": "#8be2ff",
    }
    FONT = ("Segoe UI", 11)

    def __init__(self, root: tk.Tk, pages_dir: pathlib.Path) -> None:
        self.root = root
        self.config = self._load_config()

        self.window_width = self.config.get("window_width", 420)
        self.window_height = self.config.get("window_height", 360)
        self.window_x = self.config.get("window_x")
        self.window_y = self.config.get("window_y")

        if self.window_x is not None and self.window_y is not None:
            self.root.geometry(f"{self.window_width}x{self.window_height}+{self.window_x}+{self.window_y}")
        else:
            self.root.geometry(f"{self.window_width}x{self.window_height}")

        self.root.attributes("-topmost", True)
        self.alpha_var = tk.DoubleVar(value=self.config.get("alpha", 0.85))
        self.root.attributes("-alpha", self.alpha_var.get())
        self.root.overrideredirect(True)
        self.root.configure(bg=self.PALETTE["background"])

        self.pages_dir = pages_dir
        self.font_size = self.config.get("font_size", 12)
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.settings_window: Optional[tk.Toplevel] = None
        self.settings_file_var: Optional[tk.StringVar] = None

        self.current_file: Optional[pathlib.Path] = None
        self.sections: List[Dict[str, str]] = []
        self.current_section_index = 0
        self.shortcuts = self.config.get(
            "shortcuts",
            {"home": "h", "previous": "p", "next": "n", "last": "l"},
        )

        self.root.bind("<Button-1>", self._start_drag)
        self.root.bind("<B1-Motion>", self._on_drag)
        self._bind_shortcuts()

        self._build_ui()
        self.root.resizable(True, True)
        self._load_initial_content()
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _build_ui(self) -> None:
        toolbar = tk.Frame(self.root, bg=self.PALETTE["toolbar"], bd=0)
        toolbar.pack(fill=tk.X, padx=10, pady=4)
        toolbar.configure(highlightbackground=self.PALETTE["border"], highlightthickness=1)

        self._create_button(toolbar, "首頁", self.go_home, width=6).pack(side=tk.LEFT, padx=(0, 4))
        self._create_button(toolbar, "上一頁", self.go_previous, width=6).pack(side=tk.LEFT, padx=4)
        self._create_button(toolbar, "下一頁", self.go_next, width=6).pack(side=tk.LEFT, padx=4)
        self._create_button(toolbar, "最後", self.go_last, width=6).pack(side=tk.LEFT, padx=4)
        self._create_button(toolbar, "設定", self.open_settings, width=6).pack(side=tk.LEFT, padx=8)
        self._create_button(toolbar, "關閉", self._on_closing, width=6).pack(side=tk.LEFT, padx=(10, 0))

        self.status_var = tk.StringVar(value="尚未載入內容")
        status_label = tk.Label(
            self.root,
            textvariable=self.status_var,
            bg=self.PALETTE["background"],
            fg=self.PALETTE["text_secondary"],
            font=self.FONT,
            anchor=tk.W,
        )
        status_label.pack(fill=tk.X, padx=12, pady=(0, 4))

        content_container = tk.Frame(
            self.root,
            bg=self.PALETTE["panel"],
            bd=0,
            highlightbackground=self.PALETTE["border"],
            highlightthickness=1,
        )
        content_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        text_frame = tk.Frame(content_container, bg=self.PALETTE["panel"])
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.viewer = tk.Text(
            text_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg=self.PALETTE["panel"],
            fg=self.PALETTE["text_primary"],
            insertbackground=self.PALETTE["accent"],
            font=("Microsoft YaHei", self.font_size),
            padx=14,
            pady=14,
            highlightthickness=0,
            relief=tk.FLAT,
        )
        self.viewer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(
            text_frame,
            orient=tk.VERTICAL,
            command=self.viewer.yview,
            bg=self.PALETTE["scrollbar"],
            troughcolor=self.PALETTE["panel"],
            activebackground=self.PALETTE["scrollbar_active"],
            highlightthickness=0,
            bd=0,
            relief=tk.FLAT,
        )
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.viewer.configure(yscrollcommand=self.scrollbar.set)

        self._setup_text_tags()

    def _setup_text_tags(self) -> None:
        """設定文字標籤樣式"""
        if self.viewer is None:
            return
        self.viewer.tag_configure("h1", font=("Microsoft YaHei", self.font_size + 8, "bold"), foreground=self.PALETTE["accent"])
        self.viewer.tag_configure("h2", font=("Microsoft YaHei", self.font_size + 6, "bold"), foreground="#a5c5ff")
        self.viewer.tag_configure("h3", font=("Microsoft YaHei", self.font_size + 4, "bold"), foreground="#cdd9ff")
        self.viewer.tag_configure("bold", font=("Microsoft YaHei", self.font_size, "bold"))
        self.viewer.tag_configure("italic", font=("Microsoft YaHei", self.font_size, "italic"))
        self.viewer.tag_configure("code", font=("Consolas", self.font_size),
                                  background="#26334d", foreground="#f7f7f2", relief=tk.FLAT, borderwidth=0, spacing3=4)

    def _start_drag(self, event: tk.Event) -> None:
        """開始拖動視窗"""
        # 排除按鈕和控制項的拖動
        widget = event.widget
        if isinstance(widget, (tk.Button, tk.Scale, tk.Spinbox)):
            return
        self.drag_start_x = event.x_root - self.root.winfo_x()
        self.drag_start_y = event.y_root - self.root.winfo_y()

    def _on_drag(self, event: tk.Event) -> None:
        """拖動視窗"""
        # 排除按鈕和控制項的拖動
        widget = event.widget
        if isinstance(widget, (tk.Button, tk.Scale, tk.Spinbox)):
            return
        x = event.x_root - self.drag_start_x
        y = event.y_root - self.drag_start_y
        self.root.geometry(f"+{x}+{y}")

    def increase_font(self) -> None:
        """放大字型"""
        self.font_size = min(self.font_size + 2, 24)
        self._update_font()

    def decrease_font(self) -> None:
        """縮小字型"""
        self.font_size = max(self.font_size - 2, 8)
        self._update_font()

    def _set_font_size(self, value: int) -> None:
        self.font_size = max(8, min(24, value))
        self._update_font()

    def _update_font(self) -> None:
        """更新字型大小"""
        self.viewer.config(font=("Microsoft YaHei", self.font_size))
        self._setup_text_tags()
        self._render_page()
    
    def _create_button(self, parent: tk.Widget, text: str, command, width: int = 8,
                       bg: Optional[str] = None, hover_bg: Optional[str] = None) -> tk.Button:
        base_bg = bg or self.PALETTE["button"]
        hover_color = hover_bg or self.PALETTE["button_hover"]
        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=self.FONT,
            fg=self.PALETTE["text_primary"],
            bg=base_bg,
            activebackground=hover_color,
            activeforeground=self.PALETTE["text_primary"],
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=2,
            width=width,
            cursor="hand2"
        )

        def on_enter(_):
            button.configure(bg=hover_color)

        def on_leave(_):
            button.configure(bg=base_bg)

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        return button

    def _load_config(self) -> Dict:
        """載入設定檔"""
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def _save_config(self) -> None:
        """保存設定檔"""
        config = {
            "window_width": self.window_width,
            "window_height": self.window_height,
            "window_x": self.root.winfo_x(),
            "window_y": self.root.winfo_y(),
            "alpha": self.alpha_var.get(),
            "font_size": self.font_size,
            "last_file": str(self.current_file) if self.current_file else None,
        }
        try:
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except IOError:
            pass

    def _on_closing(self) -> None:
        """視窗關閉時保存設定"""
        self._save_config()
        self.root.quit()

    def open_settings(self) -> None:
        """開啟設定視窗"""
        if self.settings_window is not None:
            self.settings_window.lift()
            return

        settings = tk.Toplevel(self.root)
        settings.title("設定")
        settings.geometry("520x680")
        settings.attributes("-topmost", True)
        settings.configure(bg=self.PALETTE["background"])
        settings.transient(self.root)
        settings.grab_set()

        self.settings_window = settings

        # 透明度設定
        alpha_frame = tk.Frame(settings, padx=20, pady=10, bg=self.PALETTE["background"])
        alpha_frame.pack(fill=tk.X)
        tk.Label(alpha_frame, text="透明度", fg=self.PALETTE["text_primary"], bg=self.PALETTE["background"],
                 font=self.FONT).pack(anchor=tk.W)
        alpha_value_label = tk.Label(alpha_frame, text=f"{self.alpha_var.get():.2f}",
                                     fg=self.PALETTE["accent"], bg=self.PALETTE["background"], font=self.FONT)
        alpha_value_label.pack(anchor=tk.W, pady=(2, 0))
        
        def update_alpha(_value: str = "") -> None:
            alpha_value_label.config(text=f"{self.alpha_var.get():.2f}")
            self._on_alpha_change()
        
        alpha_scale = tk.Scale(
            alpha_frame,
            from_=0.3,
            to=1.0,
            resolution=0.05,
            orient=tk.HORIZONTAL,
            variable=self.alpha_var,
            command=update_alpha,
            length=300,
            bg=self.PALETTE["background"],
            troughcolor=self.PALETTE["panel"],
            highlightthickness=0,
            fg=self.PALETTE["text_primary"],
            showvalue=False
        )
        alpha_scale.pack(fill=tk.X, pady=(5, 0))

        # 視窗大小設定
        size_frame = tk.Frame(settings, padx=20, pady=10, bg=self.PALETTE["background"])
        size_frame.pack(fill=tk.X)
        tk.Label(size_frame, text="視窗大小", fg=self.PALETTE["text_primary"], bg=self.PALETTE["background"],
                 font=self.FONT).pack(anchor=tk.W)
        
        size_input_frame = tk.Frame(size_frame, bg=self.PALETTE["background"])
        size_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.width_var = tk.IntVar(value=self.window_width)
        self.height_var = tk.IntVar(value=self.window_height)
        
        tk.Label(size_input_frame, text="寬度", fg=self.PALETTE["text_secondary"], bg=self.PALETTE["background"]).pack(side=tk.LEFT)
        tk.Spinbox(size_input_frame, from_=200, to=1600, textvariable=self.width_var, width=8,
                   font=self.FONT, bg=self.PALETTE["panel"], fg=self.PALETTE["text_primary"],
                   highlightbackground=self.PALETTE["border"], relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        tk.Label(size_input_frame, text="高度", fg=self.PALETTE["text_secondary"], bg=self.PALETTE["background"]).pack(side=tk.LEFT)
        tk.Spinbox(size_input_frame, from_=200, to=1200, textvariable=self.height_var, width=8,
                   font=self.FONT, bg=self.PALETTE["panel"], fg=self.PALETTE["text_primary"],
                   highlightbackground=self.PALETTE["border"], relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        self._create_button(size_input_frame, "套用", self.apply_window_size, width=6).pack(side=tk.LEFT, padx=(10, 0))

        font_frame = tk.Frame(settings, padx=20, pady=10, bg=self.PALETTE["background"])
        font_frame.pack(fill=tk.X)
        tk.Label(
            font_frame,
            text="顯示區字級 (預設 Ctrl +/-)",
            fg=self.PALETTE["text_primary"],
            bg=self.PALETTE["background"],
            font=self.FONT,
        ).pack(anchor=tk.W)
        font_scale = tk.Scale(
            font_frame,
            from_=8,
            to=24,
            resolution=1,
            orient=tk.HORIZONTAL,
            length=300,
            bg=self.PALETTE["background"],
            troughcolor=self.PALETTE["panel"],
            highlightthickness=0,
            fg=self.PALETTE["text_primary"],
            showvalue=True,
            command=lambda value: self._set_font_size(int(float(value))),
        )
        font_scale.set(self.font_size)
        font_scale.pack(fill=tk.X, pady=(5, 0))

        shortcut_frame = tk.Frame(settings, padx=20, pady=10, bg=self.PALETTE["background"])
        shortcut_frame.pack(fill=tk.X)
        tk.Label(
            shortcut_frame,
            text="快捷鍵 (Ctrl + 字母)",
            fg=self.PALETTE["text_primary"],
            bg=self.PALETTE["background"],
            font=self.FONT,
        ).pack(anchor=tk.W)
        self.shortcut_vars: Dict[str, tk.StringVar] = {}
        shortcut_grid = tk.Frame(shortcut_frame, bg=self.PALETTE["background"])
        shortcut_grid.pack(fill=tk.X, pady=(6, 0))
        shortcut_labels = [
            ("home", "首頁"),
            ("previous", "上一頁"),
            ("next", "下一頁"),
            ("last", "最後"),
        ]
        for idx, (key, label) in enumerate(shortcut_labels):
            row = tk.Frame(shortcut_grid, bg=self.PALETTE["background"])
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=label, width=8, anchor=tk.W,
                     fg=self.PALETTE["text_secondary"], bg=self.PALETTE["background"]).pack(side=tk.LEFT)
            var = tk.StringVar(value=self.shortcuts.get(key, "")[:1].upper())
            entry = tk.Entry(
                row,
                textvariable=var,
                width=3,
                font=self.FONT,
                justify="center",
                bg=self.PALETTE["panel"],
                fg=self.PALETTE["text_primary"],
                insertbackground=self.PALETTE["text_primary"],
                relief=tk.FLAT,
            )
            entry.pack(side=tk.LEFT, padx=4)
            self.shortcut_vars[key] = var
        self._create_button(shortcut_frame, "儲存快捷鍵", self._apply_shortcuts, width=12).pack(anchor=tk.W, pady=(6, 0))

        source_frame = tk.Frame(settings, padx=20, pady=10, bg=self.PALETTE["background"])
        source_frame.pack(fill=tk.X)
        tk.Label(
            source_frame,
            text="內容來源",
            fg=self.PALETTE["text_primary"],
            bg=self.PALETTE["background"],
            font=self.FONT,
        ).pack(anchor=tk.W)
        self.settings_file_var = tk.StringVar(value=self._display_file_name())
        tk.Label(
            source_frame,
            textvariable=self.settings_file_var,
            fg=self.PALETTE["text_secondary"],
            bg=self.PALETTE["background"],
            wraplength=360,
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=(2, 6))
        self._create_button(source_frame, "選擇 Markdown 檔", self.choose_markdown_file, width=18).pack(anchor=tk.W)

        # 按鈕區
        button_frame = tk.Frame(settings, padx=20, pady=20, bg=self.PALETTE["background"])
        button_frame.pack(fill=tk.X)
        self._create_button(button_frame, "確定", self._close_settings, width=8).pack(side=tk.RIGHT, padx=5)
        self._create_button(button_frame, "取消", self._close_settings, width=8,
                            bg=self.PALETTE["panel"]).pack(side=tk.RIGHT)

        settings.protocol("WM_DELETE_WINDOW", self._close_settings)

    def _close_settings(self) -> None:
        """關閉設定視窗"""
        if self.settings_window:
            self._save_config()
            self.settings_window.destroy()
            self.settings_window = None
            self.settings_file_var = None

    def _on_alpha_change(self, _value: str = "") -> None:
        """調整透明度"""
        alpha = self.alpha_var.get()
        alpha = max(0.3, min(1.0, alpha))
        self.root.attributes("-alpha", alpha)

    def apply_window_size(self) -> None:
        """套用視窗尺寸"""
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
        except (ValueError, tk.TclError):
            return

        width = max(200, min(1600, width))
        height = max(200, min(1200, height))
        self.window_width = width
        self.window_height = height
        self.width_var.set(width)
        self.height_var.set(height)
        
        # 保持視窗位置
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _load_initial_content(self) -> None:
        last_file = self.config.get("last_file")
        candidate: Optional[pathlib.Path] = None

        if last_file:
            path = pathlib.Path(last_file)
            if path.exists():
                candidate = path

        if candidate is None:
            candidate = self._get_default_file()

        if candidate:
            self._load_file(candidate)
        else:
            self.status_var.set("尚未選擇 Markdown 檔案")
            self._render_page()

    def _get_default_file(self) -> Optional[pathlib.Path]:
        if not self.pages_dir.exists():
            return None
        files = sorted(self.pages_dir.glob("*.md"))
        return files[0] if files else None

    def _load_file(self, file_path: pathlib.Path) -> None:
        try:
            content = file_path.read_text(encoding="utf-8")
        except OSError as exc:
            messagebox.showerror("讀取失敗", f"無法讀取檔案：{file_path}\n{exc}")
            return

        sections = self._parse_sections(content)
        if not sections:
            sections = [{"title": "全文", "text": content}]

        self.current_file = file_path
        self.sections = sections
        self.current_section_index = 0
        self._save_config()
        self._render_page()
        if self.settings_file_var:
            self.settings_file_var.set(self._display_file_name())

    def _parse_sections(self, content: str) -> List[Dict[str, str]]:
        sections: List[Dict[str, str]] = []
        current_title: Optional[str] = None
        current_lines: List[str] = []

        for line in content.splitlines():
            if line.startswith("# "):
                if current_lines:
                    sections.append({"title": current_title or "章節", "text": "\n".join(current_lines).strip()})
                current_title = line.lstrip("# ").strip() or "章節"
                current_lines = [line]
            else:
                if current_lines:
                    current_lines.append(line)
                else:
                    current_title = "內容"
                    current_lines = [line]

        if current_lines:
            sections.append({"title": current_title or "章節", "text": "\n".join(current_lines).strip()})

        if not sections and content.strip():
            sections.append({"title": "全文", "text": content})

        return sections

    def _display_file_name(self) -> str:
        if self.current_file:
            return str(self.current_file)
        return "尚未選擇檔案"

    def _render_page(self) -> None:
        if not self.sections:
            self.viewer.config(state=tk.NORMAL)
            self.viewer.delete("1.0", tk.END)
            self.viewer.insert(tk.END, "尚未載入章節")
            self.viewer.config(state=tk.DISABLED)
            self.status_var.set("0/0")
            return

        section = self.sections[self.current_section_index]
        total = len(self.sections)
        file_name = self.current_file.name if self.current_file else "未命名"
        self.status_var.set(f"{file_name}｜章節 {self.current_section_index + 1}/{total} - {section['title']}")

        self.viewer.config(state=tk.NORMAL)
        self.viewer.delete("1.0", tk.END)
        self._render_markdown_text(section["text"])
        self.viewer.config(state=tk.DISABLED)

    def _render_markdown_text(self, content: str) -> None:
        """簡單的 markdown 文字渲染"""
        if self.viewer is None:
            return

        lines = content.split('\n')
        in_code_block = False
        code_lines = []

        for line in lines:
            # 處理程式碼區塊
            if line.strip().startswith('```'):
                if in_code_block:
                    # 結束程式碼區塊
                    code_text = '\n'.join(code_lines)
                    start = self.viewer.index(tk.INSERT)
                    self.viewer.insert(tk.END, code_text + '\n')
                    end = self.viewer.index(tk.INSERT)
                    self.viewer.tag_add("code", start, end)
                    code_lines = []
                    in_code_block = False
                else:
                    in_code_block = True
                continue

            if in_code_block:
                code_lines.append(line)
                continue

            # 處理標題
            if line.startswith('# '):
                start = self.viewer.index(tk.INSERT)
                self.viewer.insert(tk.END, line[2:] + '\n')
                end = self.viewer.index(tk.INSERT)
                self.viewer.tag_add("h1", start, end)
            elif line.startswith('## '):
                start = self.viewer.index(tk.INSERT)
                self.viewer.insert(tk.END, line[3:] + '\n')
                end = self.viewer.index(tk.INSERT)
                self.viewer.tag_add("h2", start, end)
            elif line.startswith('### '):
                start = self.viewer.index(tk.INSERT)
                self.viewer.insert(tk.END, line[4:] + '\n')
                end = self.viewer.index(tk.INSERT)
                self.viewer.tag_add("h3", start, end)
            else:
                # 處理粗體和斜體
                self._insert_formatted_line(line)

    def _insert_formatted_line(self, line: str) -> None:
        """插入格式化文字行"""
        if self.viewer is None:
            return

        # 簡單處理粗體 **text** 和斜體 *text*
        parts = re.split(r'(\*\*.*?\*\*|\*.*?\*)', line)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                text = part[2:-2]
                start = self.viewer.index(tk.INSERT)
                self.viewer.insert(tk.END, text)
                end = self.viewer.index(tk.INSERT)
                self.viewer.tag_add("bold", start, end)
            elif part.startswith('*') and part.endswith('*') and len(part) > 2:
                text = part[1:-1]
                start = self.viewer.index(tk.INSERT)
                self.viewer.insert(tk.END, text)
                end = self.viewer.index(tk.INSERT)
                self.viewer.tag_add("italic", start, end)
            else:
                self.viewer.insert(tk.END, part)
        self.viewer.insert(tk.END, '\n')

    def go_home(self) -> None:
        if self.sections:
            self.current_section_index = 0
            self._render_page()

    def go_previous(self) -> None:
        if self.sections:
            self.current_section_index = (self.current_section_index - 1) % len(self.sections)
            self._render_page()

    def go_next(self) -> None:
        if self.sections:
            self.current_section_index = (self.current_section_index + 1) % len(self.sections)
            self._render_page()

    def go_last(self) -> None:
        if self.sections:
            self.current_section_index = len(self.sections) - 1
            self._render_page()

    def choose_markdown_file(self) -> None:
        initial_dir = self.current_file.parent if self.current_file else self.pages_dir
        file_path = filedialog.askopenfilename(
            initialdir=initial_dir,
            filetypes=[("Markdown", "*.md"), ("所有檔案", "*.*")],
        )
        if file_path:
            self._load_file(pathlib.Path(file_path))

    def _bind_shortcuts(self) -> None:
        # remove previous bindings by unbinding wildcard (tkinter lacks direct). rebind using new keys
        for key in list(self.shortcuts.values()):
            if key:
                key = key.lower()
                self.root.unbind(f"<Control-{key}>")
        bindings = {
            "home": self.go_home,
            "previous": self.go_previous,
            "next": self.go_next,
            "last": self.go_last,
        }
        for action, func in bindings.items():
            key = self.shortcuts.get(action, "")
            if key:
                normalized = key.lower()
                self.root.bind(f"<Control-{normalized}>", lambda _e, fn=func: fn())
                self.root.bind(f"<Control-{normalized.upper()}>", lambda _e, fn=func: fn())
        self.root.bind("<Control-=>", lambda _e: self.increase_font())
        self.root.bind("<Control-minus>", lambda _e: self.decrease_font())
        
        # 方向鍵快捷鍵
        self.root.bind("<Up>", lambda _e: self.go_previous())
        self.root.bind("<Down>", lambda _e: self.go_next())
        self.root.bind("<Left>", lambda _e: self.go_home())
        self.root.bind("<Right>", lambda _e: self.go_last())

    def _apply_shortcuts(self) -> None:
        updated = {}
        for key, var in self.shortcut_vars.items():
            value = (var.get() or "").strip().lower()
            if not value:
                messagebox.showwarning("快捷鍵", f"{key} 的快捷鍵不可為空")
                return
            if len(value) != 1 or not value.isalpha():
                messagebox.showwarning("快捷鍵", "僅接受單一英文字母")
                return
            updated[key] = value
        self.shortcuts = updated
        self._bind_shortcuts()
        self._save_config()
        messagebox.showinfo("快捷鍵", "快捷鍵已更新，可使用 Ctrl + 字母 操作。")


def main() -> None:
    root = tk.Tk()
    default_dir = pathlib.Path("content/pages").resolve()
    MarkdownPager(root, default_dir)
    root.mainloop()


if __name__ == "__main__":
    main()

