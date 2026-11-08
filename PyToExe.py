"""
PyInstaller GUI Wrapper - pytoexe
A tkinter-based GUI for PyInstaller with Windows 11 style
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import shutil
import pathlib
from PyInstaller import __main__ as pyinstaller_main
import ctypes
import sys


# Windows 11 Dark Theme Style
def apply_win11_style(root):
    """Apply Windows 11 style using ctypes"""
    try:
        # Set window attributes for dark mode on Windows 11
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        # 设置DPI感知 - 优先使用Windows 10/11的Per Monitor V2模式
        try:
            # Windows 10 1703+ (Per Monitor V2)
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except (AttributeError, OSError):
            try:
                # Windows 8.1 - 10 1607 (Per Monitor)
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except (AttributeError, OSError):
                try:
                    # Windows Vista - 8 (System DPI Aware)
                    ctypes.windll.user32.SetProcessDPIAware()
                except (AttributeError, OSError):
                    pass  # 旧版本Windows，无需设置
        
        # Use DWMWA_USE_IMMERSIVE_DARK_MODE for Windows 11
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        value = ctypes.c_int(1)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(value),
            ctypes.sizeof(value)
        )
        
        # Enable rounded corners (Windows 11)
        DWMWA_WINDOW_CORNER_PREFERENCE = 33
        corner_preference = ctypes.c_int(2)  # DWMWCP_ROUND
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_WINDOW_CORNER_PREFERENCE,
            ctypes.byref(corner_preference),
            ctypes.sizeof(corner_preference)
        )
    except Exception:
        pass  # Fallback silently on older Windows versions


class PyToExeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PyToExe")
        self.root.resizable(False, False)

        # Apply Windows 11 style
        apply_win11_style(self.root)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Custom styles
        #self.style.configure('TFrame', background='#1e1e1e')
        #self.style.configure('TLabel', background='#1e1e1e', foreground='#ffffff', font=('Segoe UI', 10))
        #self.style.configure('TButton', font=('Segoe UI', 10), padding=10)
        #self.style.configure('TCheckbutton', background='#1e1e1e', foreground='#ffffff', font=('Segoe UI', 10))
        #self.style.configure('TEntry', font=('Segoe UI', 10), padding=5)
        
        self.root.configure(bg='#1e1e1e')
        
        # Variables
        self.source_file = tk.StringVar()
        self.add_data_files = tk.StringVar()
        self.icon_file = tk.StringVar()
        self.windowed_var = tk.BooleanVar()
        self.icon_var = tk.BooleanVar()
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="PyToExe - Python to Executable", 
                                font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Source Python File
        source_frame = ttk.Frame(main_frame)
        source_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(source_frame, text="源Python文件:").pack(anchor=tk.W)
        
        source_entry_frame = ttk.Frame(source_frame)
        source_entry_frame.pack(fill=tk.X, pady=5)
        
        ttk.Entry(source_entry_frame, textvariable=self.source_file, 
                  width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(source_entry_frame, text="浏览...", 
                   command=self.browse_source).pack(side=tk.LEFT, padx=(10, 0))
        
        # Add Data Files
        add_data_frame = ttk.Frame(main_frame)
        add_data_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(add_data_frame, text="--add-data (多个文件用分号分隔):").pack(anchor=tk.W)
        
        add_data_entry_frame = ttk.Frame(add_data_frame)
        add_data_entry_frame.pack(fill=tk.X, pady=5)
        
        ttk.Entry(add_data_entry_frame, textvariable=self.add_data_files, 
                  width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(add_data_entry_frame, text="浏览...", 
                   command=self.browse_add_data).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(add_data_entry_frame, text="清空", 
                   command=lambda: self.add_data_files.set("")).pack(side=tk.LEFT, padx=(10, 0))
        
        # Options Frame
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=15)
        
        ttk.Label(options_frame, text="选项:").pack(anchor=tk.W)
        
        checkboxes_frame = ttk.Frame(options_frame)
        checkboxes_frame.pack(fill=tk.X, pady=10)
        
        # -w checkbox
        tk.Checkbutton(checkboxes_frame, text="-w (窗口模式，无控制台)", 
                        variable=self.windowed_var).pack(anchor=tk.W)
        
        # -i checkbox and icon selection
        icon_frame = ttk.Frame(checkboxes_frame)
        icon_frame.pack(fill=tk.X, pady=5)
        
        tk.Checkbutton(icon_frame, text="-i (自定义图标)", 
                        variable=self.icon_var,
                        command=self.toggle_icon_selection).pack(side=tk.LEFT)
        
        self.icon_entry = ttk.Entry(icon_frame, textvariable=self.icon_file, 
                                     width=30, state=tk.DISABLED)
        self.icon_entry.pack(side=tk.LEFT, padx=(10, 5))
        
        self.icon_btn = ttk.Button(icon_frame, text="浏览...", 
                                    command=self.browse_icon, state=tk.DISABLED)
        self.icon_btn.pack(side=tk.LEFT)
        
        # Build Button
        build_btn = ttk.Button(main_frame, text="开始打包", 
                               command=self.build_exe)
        build_btn.pack(pady=20)
        
        # Status
        self.status_var = tk.StringVar(value="准备就绪")
        status_label = ttk.Label(main_frame, textvariable=self.status_var,
                                  font=('Segoe UI', 9))
        status_label.pack(pady=10)
    
    def toggle_icon_selection(self):
        """Enable/disable icon file selection based on checkbox"""
        if self.icon_var.get():
            self.icon_entry.configure(state=tk.NORMAL)
            self.icon_btn.configure(state=tk.NORMAL)
        else:
            self.icon_entry.configure(state=tk.DISABLED)
            self.icon_btn.configure(state=tk.DISABLED)
            self.icon_file.set("")
    
    def browse_source(self):
        """Browse for source Python file"""
        file_path = filedialog.askopenfilename(
            title="选择Python源文件",
            filetypes=[("Python脚本文件", "*.py")]
        )
        if file_path:
            self.source_file.set(file_path)
    
    def browse_add_data(self):
        """Browse for additional data files"""
        file_paths = filedialog.askopenfilenames(
            title="选择数据文件"
        )
        if file_paths:
            # Add to existing files
            existing = self.add_data_files.get()
            new_files = ";".join(file_paths)
            if existing:
                self.add_data_files.set(f"{existing};{new_files}")
            else:
                self.add_data_files.set(new_files)
    
    def browse_icon(self):
        """Browse for icon file"""
        file_path = filedialog.askopenfilename(
            title="选择图标文件",
            filetypes=[("图标文件", "*.ico")]
        )
        if file_path:
            self.icon_file.set(file_path)
    
    def build_exe(self):
        """Build executable using PyInstaller"""
        # Validate input
        source = self.source_file.get()
        if not source:
            messagebox.showerror("错误", "请选择源Python文件")
            return
        
        if not pathlib.Path(source).exists():
            messagebox.showerror("错误", "源文件不存在")
            return
        
        # Build PyInstaller arguments
        args = ['pyinstaller']
        
        # Add source file
        args.append(source)
        
        # Add -w flag
        if self.windowed_var.get():
            args.append('-w')
            args.append('--noconsole')
        
        # Add icon
        if self.icon_var.get():
            icon = self.icon_file.get()
            if icon and pathlib.Path(icon).exists():
                args.extend(['-i', icon])
            elif icon:
                messagebox.showwarning("警告", "图标文件不存在，将使用默认图标")
        
        # Add data files
        add_data = self.add_data_files.get()
        if add_data:
            files = add_data.split(';')
            for f in files:
                f = f.strip()
                if f and pathlib.Path(f).exists():
                    # Format: source;dest (use same directory structure)
                    args.extend(['--add-data', f'{f};.'])
        
        # Add one-file mode
        args.append('--onefile')
        
        # Clean before build
        self.status_var.set("正在打包...")
        self.root.update()
        
        try:
            # Run PyInstaller programmatically (no os.system!)
            sys.argv = args
            pyinstaller_main.run()
            
            # Get the output exe name
            source_path = pathlib.Path(source)
            exe_name = source_path.stem + '.exe'
            parent_dir = source_path.parent
            
            # Clean up build artifacts
            self.status_var.set("正在清理临时文件...")
            self.root.update()
            
            # Delete build folder
            build_dir = parent_dir / 'build'
            if build_dir.exists():
                shutil.rmtree(build_dir)
            
            # Delete spec file
            spec_file = parent_dir / (source_path.stem + '.spec')
            if spec_file.exists():
                spec_file.unlink()
            
            # Move exe from dist to parent directory
            dist_dir = parent_dir / 'dist'
            exe_in_dist = dist_dir / exe_name
            exe_final = parent_dir / exe_name
            
            if exe_in_dist.exists():
                # Remove existing exe if present
                if exe_final.exists():
                    exe_final.unlink()
                shutil.move(str(exe_in_dist), str(exe_final))
            
            # Delete dist folder
            if dist_dir.exists():
                shutil.rmtree(dist_dir)
            
            self.status_var.set("打包完成！")
            messagebox.showinfo("成功", f"打包完成！\n输出文件: {exe_final}")
            
        except Exception as e:
            self.status_var.set("打包失败")
            messagebox.showerror("错误", f"打包失败:\n{str(e)}")


def main():
    root = tk.Tk()
    app = PyToExeApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
