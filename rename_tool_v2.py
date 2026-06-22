import os
import re
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# --- Constants & Themes ---
# Catppuccin Mocha-ish Dark Palette
BG_DARK = "#181825"       # Window base background
BG_PANEL = "#1e1e2e"      # Left pane sidebar background
BG_CARD = "#252538"       # Treeview background
BG_ENTRY = "#313244"      # Input boxes background
FG_WHITE = "#cdd6f4"      # Main text color
FG_MUTED = "#a6adc8"      # Subtext/Labels color
BORDER_COLOR = "#45475a"  # Non-focused border for inputs
FOCUS_COLOR = "#89b4fa"   # Focused border (accent blue)

BTN_PRIMARY = "#89b4fa"
BTN_PRIMARY_HOVER = "#b4befe"
BTN_SUCCESS = "#a6e3a1"
BTN_SUCCESS_HOVER = "#c2f0bd"
BTN_DANGER = "#f38ba8"
BTN_DANGER_HOVER = "#f8b0c2"
BTN_DISABLED = "#313244"
FG_DISABLED = "#585b70"
FG_DARK = "#11111b"

FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_SUBTITLE = ("Segoe UI", 9)
FONT_SECTION = ("Segoe UI", 10, "bold")
FONT_NORMAL = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)

CONFIG_FILE = "rename_config.json"

# --- Globals for data sharing ---
pending_renames = []

# --- Config functions ---
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "folder_path": "",
        "title1": "",
        "title2": "",
        "season": "S01",
        "auto_save": True
    }

def save_config(path, t1, t2, season, auto_save):
    config = {
        "folder_path": path,
        "title1": t1,
        "title2": t2,
        "season": season,
        "auto_save": auto_save
    }
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception:
        pass

# --- UI Helper Classes ---
class CustomEntry(tk.Entry):
    def __init__(self, master, **kwargs):
        super().__init__(master, 
                         bg=BG_ENTRY, 
                         fg=FG_WHITE, 
                         insertbackground=FG_WHITE, 
                         relief="flat", 
                         bd=0, 
                         highlightthickness=1, 
                         highlightbackground=BORDER_COLOR, 
                         highlightcolor=FOCUS_COLOR,
                         font=FONT_NORMAL,
                         **kwargs)

# --- Main Logic ---
def browse_folder(entry_field):
    selected_dir = filedialog.askdirectory()
    if selected_dir:
        entry_field.delete(0, tk.END)
        entry_field.insert(0, os.path.normpath(selected_dir))

def scan_files():
    global pending_renames
    target_dir = entry_path.get().strip()
    season_str = entry_season.get().strip()
    title1 = entry_title1.get().strip()
    title2 = entry_title2.get().strip()

    if not target_dir or not os.path.isdir(target_dir):
        messagebox.showerror("錯誤", "請選擇正確的劇集資料夾路徑！")
        return
    
    if not re.match(r'^[Ss]\d{1,2}$', season_str):
        messagebox.showerror("錯誤", "季數格式不正確，請輸入如 S01, S02 等格式！")
        return

    # Force upper case for season
    season_str = season_str.upper()

    video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.rmvb', '.ts')
    ep_pattern = re.compile(r'[Ss]\d{1,2}[Ee](\d{1,2})|[Ee][Pp]?(\d{1,2})|[^a-zA-Z0-9](\d{1,2})[^a-zA-Z0-9]')

    pending_renames = []
    
    # Clear preview tree
    for item in tree.get_children():
        tree.delete(item)

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext.lower() not in video_extensions:
                continue
                
            match = ep_pattern.search(file)
            if match:
                ep_num_str = next(g for g in match.groups() if g is not None)
                ep_num = int(ep_num_str)
                season_ep_str = f"{season_str}E{ep_num:02d}"
                
                name_parts = []
                if title1:
                    name_parts.append(title1)
                if title2:
                    name_parts.append(title2)
                name_parts.append(season_ep_str)
                
                new_name = ".".join(name_parts) + ext
                
                if new_name != file:
                    old_path = os.path.join(root, file)
                    new_path = os.path.join(root, new_name)
                    pending_renames.append((old_path, new_path, file, new_name))

    if not pending_renames:
        lbl_status.config(text="狀態: 掃描完成，沒有需要修改的檔案。", fg=FG_MUTED)
        btn_execute.config(state="disabled", bg=BTN_DISABLED, fg=FG_DISABLED)
        messagebox.showinfo("提示", "沒有找到需要修正的劇集檔案，或檔案格式已符合。")
        return

    # Populate Treeview
    for _, _, old, new in pending_renames:
        tree.insert("", tk.END, values=(old, new))

    # Enable execute button
    btn_execute.config(state="normal", bg=BTN_SUCCESS, fg=FG_DARK)
    lbl_status.config(text=f"狀態: 掃描完成，共有 {len(pending_renames)} 個檔案待更名", fg=BTN_PRIMARY)

    # Save settings if auto_save is enabled
    if var_auto_save.get():
        save_config(target_dir, title1, title2, season_str, True)

def execute_rename():
    global pending_renames
    if not pending_renames:
        return
        
    confirm = messagebox.askyesno("確認執行", f"確定要執行這 {len(pending_renames)} 個檔案的名稱修改嗎？\n此動作將直接修改硬碟中的檔案名稱！")
    if not confirm:
        return

    try:
        success_count = 0
        for old_path, new_path, _, _ in pending_renames:
            os.rename(old_path, new_path)
            success_count += 1
        
        messagebox.showinfo("成功", f"成功修改 {success_count} 個檔案！")
        lbl_status.config(text=f"狀態: 成功修改 {success_count} 個檔案！", fg=BTN_SUCCESS)
        
        # Reset lists and button states
        pending_renames = []
        for item in tree.get_children():
            tree.delete(item)
        btn_execute.config(state="disabled", bg=BTN_DISABLED, fg=FG_DISABLED)
        
    except Exception as e:
        messagebox.showerror("錯誤", f"更名過程中發生錯誤：\n{str(e)}")
        lbl_status.config(text="狀態: 更名發生錯誤，請檢查權限或檔案佔用狀態", fg=BTN_DANGER)

def setup_button_hover(btn, normal_bg, hover_bg, normal_fg=FG_DARK, hover_fg=FG_DARK):
    def on_enter(e):
        if btn["state"] != "disabled":
            btn.config(bg=hover_bg, fg=hover_fg)
    def on_leave(e):
        if btn["state"] != "disabled":
            btn.config(bg=normal_bg, fg=normal_fg)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

# --- Window setup ---
root = tk.Tk()
root.title("劇集名稱重組與標準化工具")
root.geometry("960x600")
root.minsize(900, 500)
root.configure(bg=BG_DARK)

# Configuration persistence
config_data = load_config()

# Split panels: Left frame (Sidebar), Right frame (Table view)
root.grid_columnconfigure(0, weight=0, minsize=350)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

# --- Left Sidebar ---
sidebar = tk.Frame(root, bg=BG_PANEL, padx=20, pady=20)
sidebar.grid(row=0, column=0, sticky="nsew")
sidebar.grid_columnconfigure(0, weight=1)

# Header
lbl_title = tk.Label(sidebar, text="劇集名稱標準化工具", font=FONT_TITLE, fg=FG_WHITE, bg=BG_PANEL, anchor="w")
lbl_title.grid(row=0, column=0, sticky="w", pady=(0, 2))
lbl_subtitle = tk.Label(sidebar, text="統一命名格式，快速清理檔名雜贅資訊", font=FONT_SUBTITLE, fg=FG_MUTED, bg=BG_PANEL, anchor="w")
lbl_subtitle.grid(row=1, column=0, sticky="w", pady=(0, 15))

# Divider
div = tk.Frame(sidebar, height=1, bg=BORDER_COLOR)
div.grid(row=2, column=0, sticky="ew", pady=(0, 15))

# 1. 資料夾路徑
lbl_path = tk.Label(sidebar, text="劇集資料夾路徑", font=FONT_SECTION, fg=FG_WHITE, bg=BG_PANEL, anchor="w")
lbl_path.grid(row=3, column=0, sticky="w", pady=(5, 5))

path_frame = tk.Frame(sidebar, bg=BG_PANEL)
path_frame.grid(row=4, column=0, sticky="ew")
path_frame.grid_columnconfigure(0, weight=1)

entry_path = CustomEntry(path_frame)
entry_path.insert(0, config_data["folder_path"])
entry_path.grid(row=0, column=0, sticky="ew", ipady=6, padx=(0, 5))

btn_browse = tk.Button(path_frame, text="瀏覽資料夾", font=FONT_SMALL, bg=BG_ENTRY, fg=FG_WHITE, 
                       activebackground=BORDER_COLOR, activeforeground=FG_WHITE, relief="flat", bd=0, 
                       cursor="hand2", command=lambda: browse_folder(entry_path), padx=10)
btn_browse.grid(row=0, column=1, sticky="ns")
setup_button_hover(btn_browse, BG_ENTRY, BORDER_COLOR, FG_WHITE, FG_WHITE)

# 2. 標題一
lbl_t1 = tk.Label(sidebar, text="標題一 (如: 劇名 / Show Title)", font=FONT_SECTION, fg=FG_WHITE, bg=BG_PANEL, anchor="w")
lbl_t1.grid(row=5, column=0, sticky="w", pady=(15, 5))
entry_title1 = CustomEntry(sidebar)
entry_title1.insert(0, config_data["title1"])
entry_title1.grid(row=6, column=0, sticky="ew", ipady=6)

# 3. 標題二
lbl_t2 = tk.Label(sidebar, text="標題二 (如: 畫質標籤 / 1080p.NF)", font=FONT_SECTION, fg=FG_WHITE, bg=BG_PANEL, anchor="w")
lbl_t2.grid(row=7, column=0, sticky="w", pady=(15, 5))
entry_title2 = CustomEntry(sidebar)
entry_title2.insert(0, config_data["title2"])
entry_title2.grid(row=8, column=0, sticky="ew", ipady=6)

# 4. 指定季數
lbl_season_title = tk.Label(sidebar, text="設定指定季數", font=FONT_SECTION, fg=FG_WHITE, bg=BG_PANEL, anchor="w")
lbl_season_title.grid(row=9, column=0, sticky="w", pady=(15, 5))

season_frame = tk.Frame(sidebar, bg=BG_PANEL)
season_frame.grid(row=10, column=0, sticky="ew")
season_frame.grid_columnconfigure(1, weight=1)

entry_season = CustomEntry(season_frame, width=10)
entry_season.insert(0, config_data["season"])
entry_season.grid(row=0, column=0, sticky="w", ipady=6, padx=(0, 8))

lbl_season_hint = tk.Label(season_frame, text="(格式: S01, S02...)", font=FONT_SMALL, fg=FG_MUTED, bg=BG_PANEL)
lbl_season_hint.grid(row=0, column=1, sticky="w")

# Options (Auto-save)
var_auto_save = tk.BooleanVar(value=config_data["auto_save"])
chk_auto_save = tk.Checkbutton(sidebar, text="自動儲存設定欄位", variable=var_auto_save, 
                               font=FONT_SMALL, fg=FG_WHITE, bg=BG_PANEL, selectcolor=BG_DARK, 
                               activebackground=BG_PANEL, activeforeground=FG_WHITE, 
                               relief="flat", bd=0, highlightthickness=0)
chk_auto_save.grid(row=11, column=0, sticky="w", pady=(15, 10))

# Status Display
lbl_status = tk.Label(sidebar, text="狀態: 準備就緒", font=FONT_SMALL, fg=FG_MUTED, bg=BG_PANEL, anchor="w")
lbl_status.grid(row=12, column=0, sticky="ew", pady=(0, 15))

# Action Buttons
btn_scan = tk.Button(sidebar, text=" 掃描與分析檔案 ", font=FONT_NORMAL, bg=BTN_PRIMARY, fg=FG_DARK, 
                     relief="flat", bd=0, cursor="hand2", height=2, command=scan_files)
btn_scan.grid(row=13, column=0, sticky="ew", pady=5)
setup_button_hover(btn_scan, BTN_PRIMARY, BTN_PRIMARY_HOVER)

btn_execute = tk.Button(sidebar, text=" 執行更名 ", font=FONT_NORMAL, bg=BTN_DISABLED, fg=FG_DISABLED, 
                       relief="flat", bd=0, state="disabled", height=2, command=execute_rename)
btn_execute.grid(row=14, column=0, sticky="ew", pady=5)
setup_button_hover(btn_execute, BTN_SUCCESS, BTN_SUCCESS_HOVER)


# --- Right Preview Panel ---
preview_panel = tk.Frame(root, bg=BG_DARK, padx=20, pady=20)
preview_panel.grid(row=0, column=1, sticky="nsew")
preview_panel.grid_rowconfigure(1, weight=1)
preview_panel.grid_columnconfigure(0, weight=1)

lbl_table_header = tk.Label(preview_panel, text="更名預覽對照表", font=FONT_SECTION, fg=FG_WHITE, bg=BG_DARK, anchor="w")
lbl_table_header.grid(row=0, column=0, sticky="w", pady=(0, 10))

# Custom TTK styling for Treeview to make it dark themed
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", 
                background=BG_CARD, 
                foreground=FG_WHITE, 
                fieldbackground=BG_CARD, 
                rowheight=28, 
                bordercolor=BORDER_COLOR, 
                borderwidth=0)
style.map("Treeview", background=[("selected", "#3e3f5c")], foreground=[("selected", FG_WHITE)])
style.configure("Treeview.Heading", 
                background=BG_ENTRY, 
                foreground=FG_WHITE, 
                font=FONT_SECTION, 
                relief="flat", 
                borderwidth=0)

# Table Container (for tree + scrollbar)
table_frame = tk.Frame(preview_panel, bg=BG_DARK)
table_frame.grid(row=1, column=0, sticky="nsew")
table_frame.grid_columnconfigure(0, weight=1)
table_frame.grid_rowconfigure(0, weight=1)

tree = ttk.Treeview(table_frame, columns=("old", "new"), show="headings", selectmode="browse")
tree.heading("old", text="原檔名 (含有雜贅後綴)")
tree.heading("new", text="新檔名 (重新標準化)")
tree.column("old", width=280, anchor="w")
tree.column("new", width=280, anchor="w")
tree.grid(row=0, column=0, sticky="nsew")

scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(row=0, column=1, sticky="ns")

# Save on close
def on_closing():
    if var_auto_save.get():
        save_config(entry_path.get().strip(), entry_title1.get().strip(), 
                    entry_title2.get().strip(), entry_season.get().strip().upper(), True)
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()