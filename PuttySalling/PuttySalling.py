import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext, simpledialog
import subprocess, threading, os, json, locale, time
import win32gui, win32con, win32process

CONFIG_FILE = "config.json"
LANGUAGES = ['en', 'da']

STRINGS = {
    'en': {
        'enter_store': 'Enter 4-digit Store Number:',
        'connect': 'Connect',
        'connect_last': 'Connect Last',
        'save_store': 'Save Store',
        'info': 'Developed by Avatorsinc',
        'settings_putty': 'Set putty.exe…',
        'settings_session': 'Set session name…',
        'invalid_input': 'Store number must be 4 digits.',
        'no_store': 'No saved stores.',
        'developed_by': 'Developed by Workplace Management'
    },
    'da': {
        'enter_store': 'Indtast butiksnummer med 4 cifre:',
        'connect': 'Forbind',
        'connect_last': 'Forbind Sidst',
        'save_store': 'Gem Butik',
        'info': 'Info',
        'settings_putty': 'Vælg putty.exe…',
        'settings_session': 'Vælg sessionsnavn…',
        'invalid_input': 'Butiksnummer skal være 4 cifre.',
        'no_store': 'Ingen gemte butikker.',
        'developed_by': 'Udviklet af Workplace Management'
    }
}

class SSHApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SSH to Store (embedded PuTTY)")
        self.geometry("600x550")
        self.configure(bg='#e6f0ff')

        self.cfg = self.load_config()
        self.putty_path = self.cfg.get('putty_path', 'putty.exe')
        self.session_name = self.cfg.get('session_name', 'StoreTemplate')
        self.last_store = self.cfg.get('last_store')
        self.saved_stores = self.cfg.get('saved_stores', [])
        self.info_text = self.cfg.get('info_text', '')

        sys_locale = locale.getdefaultlocale()[0]
        self.lang = 'da' if sys_locale and sys_locale.startswith('da') else 'en'

        self._build_menu()
        self._build_widgets()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {}

    def save_config(self):
        data = {
            'putty_path': self.putty_path,
            'session_name': self.session_name,
            'last_store': self.last_store,
            'saved_stores': self.saved_stores,
            'info_text': self.info_text
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def _(self, key):
        return STRINGS[self.lang].get(key, key)

    def _build_menu(self):
        menubar = tk.Menu(self)
        settings = tk.Menu(menubar, tearoff=0)
        settings.add_command(label=self._('settings_putty'), command=self._set_putty_path)
        settings.add_command(label=self._('settings_session'), command=self._set_session_name)
        menubar.add_cascade(label="Settings", menu=settings)
        self.config(menu=menubar)

    def _build_widgets(self):
        top_frame = tk.Frame(self, bg='#e6f0ff')
        top_frame.pack(fill='x', padx=10, pady=5)
        try:
            en_img = tk.PhotoImage(file='flag_en.png')
            da_img = tk.PhotoImage(file='flag_da.png')
        except Exception:
            en_img = None
            da_img = None
        if en_img:
            tk.Button(top_frame, image=en_img, command=lambda: self._set_lang('en'), bd=0).pack(side='right', padx=2)
        else:
            tk.Button(top_frame, text='EN', command=lambda: self._set_lang('en'), bd=0).pack(side='right', padx=2)
        if da_img:
            tk.Button(top_frame, image=da_img, command=lambda: self._set_lang('da'), bd=0).pack(side='right')
        else:
            tk.Button(top_frame, text='DA', command=lambda: self._set_lang('da'), bd=0).pack(side='right')
        self.flag_imgs = (en_img, da_img)

        tk.Label(self, text=self._('enter_store'), bg='#e6f0ff').pack(pady=(10,0))
        self.entry = tk.Entry(self, font=("Arial",14), justify='center')
        self.entry.pack(pady=5)

        btn_frame = tk.Frame(self, bg='#e6f0ff')
        btn_frame.pack(pady=5)
        self.connect_btn = tk.Button(btn_frame, text=self._('connect'), command=self._on_connect,
                                     bg='#007acc', fg='white', font=("Arial",12), width=12)
        self.connect_btn.grid(row=0, column=0, padx=5)

        self.last_btn = tk.Button(btn_frame, text=self._('connect_last'), command=self._on_connect_last,
                                  bg='#005999', fg='white', font=("Arial",10), width=12)
        self.last_btn.grid(row=0, column=1, padx=5)
        if not self.last_store:
            self.last_btn.config(state='disabled')

        self.save_btn = tk.Button(btn_frame, text=self._('save_store'), command=self._on_save_store,
                                  bg='#3399ff', fg='white', font=("Arial",10), width=12)
        self.save_btn.grid(row=0, column=2, padx=5)

        self.store_list = tk.Listbox(self, height=4)
        self.store_list.pack(fill='x', padx=20, pady=5)
        self.store_list.bind('<Double-1>', self._on_select_store)
        self._refresh_store_list()

        self.terminal_frame = tk.Frame(self, bg='black', width=1920, height=1080)
        self.terminal_frame.pack(padx=10, pady=5)
        self.terminal_frame.pack_propagate(False)

        bottom_frame = tk.Frame(self, bg='#e6f0ff')
        bottom_frame.pack(fill='x', padx=10, pady=5)
        tk.Button(bottom_frame, text=self._('info'), bd=0, fg='#007acc', command=self._show_info).pack(side='left')
        tk.Label(bottom_frame, text=self._('developed_by'), bg='#e6f0ff', fg='#005999').pack(side='right')

    def _set_lang(self, lang):
        self.lang = lang
        self._rebuild_texts()

    def _rebuild_texts(self):
        for w in self.winfo_children(): w.destroy()
        self._build_menu()
        self._build_widgets()

    def _set_putty_path(self):
        path = filedialog.askopenfilename(title=self._('settings_putty'), filetypes=[("EXE files","*.exe")])
        if path:
            self.putty_path = path
            self.save_config()

    def _set_session_name(self):
        name = simpledialog.askstring("Session Name", "Enter PuTTY session name:", initialvalue=self.session_name)
        if name:
            self.session_name = name
            self.save_config()

    def _refresh_store_list(self):
        self.store_list.delete(0, 'end')
        if self.saved_stores:
            for s in self.saved_stores:
                self.store_list.insert('end', s)
        else:
            self.store_list.insert('end', self._('no_store'))

    def _on_save_store(self):
        s = self.entry.get().strip()
        if s.isdigit() and len(s)==4 and s not in self.saved_stores:
            self.saved_stores.append(s)
            self.save_config()
            self._refresh_store_list()

    def _on_select_store(self, event):
        sel = self.store_list.get(self.store_list.curselection())
        if sel.isdigit(): self._start_thread(sel)

    def _on_connect(self):
        s = self.entry.get().strip()
        if not (s.isdigit() and len(s)==4):
            messagebox.showerror("Error", self._('invalid_input'))
            return
        self._start_thread(s)

    def _on_connect_last(self):
        if self.last_store: self._start_thread(self.last_store)

    def _show_info(self):
        messagebox.showinfo(self._('info'), self.info_text or "")

    def _start_thread(self, store):
        self.connect_btn.config(state='disabled')
        self.last_btn.config(state='disabled')
        threading.Thread(target=self._connect_worker, args=(store,), daemon=True).start()

    def _connect_worker(self, store):
        host = f"pv{store}"
        self.last_store = store; self.save_config()
        cmd = [self.putty_path, '-load', self.session_name, '-ssh', host]
        proc = subprocess.Popen(cmd)
        time.sleep(0.5)
        try:
            def _enum(hwnd, pid):
                if win32process.GetWindowThreadProcessId(hwnd)[1] == pid:
                    win32gui.SetParent(hwnd, self.terminal_frame.winfo_id())
                    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, win32con.WS_VISIBLE)
                    win32gui.MoveWindow(hwnd, 0, 0, 580, 220, True)
                    raise StopIteration
            win32gui.EnumWindows(lambda h, _: _enum(h, proc.pid), None)
        except StopIteration:
            pass
        proc.wait()
        self.connect_btn.config(state='normal')
        self.last_btn.config(state='normal')

if __name__=='__main__':
    app = SSHApp()
    app.mainloop()
