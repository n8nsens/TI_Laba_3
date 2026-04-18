import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import algorithm
import math

class ElGamalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа: Шифрование Эль-Гамаля")
        self.root.geometry("840x680")
        self.root.resizable(False, False)

        self.p_var = tk.StringVar()
        self.x_var = tk.StringVar()
        self.k_var = tk.StringVar()
        self.g_var = tk.IntVar(value=0)
        self.file_var = tk.StringVar()
        self.root_count_var = tk.StringVar()
        self.padding_len = 0
        self.encrypted_blocks = []

        self._apply_style()
        self._build_ui()

    def _apply_style(self):
    # === ТВОИ ЦВЕТА ===
        BG_COLOR = "#FFC0CB"       # розовый фон
        BTN_COLOR = "#FF738b"      # кнопки
        ENTRY_COLOR = "#FFD7DE"    # поля ввода
    
        s = ttk.Style()
        s.theme_use("clam")
    
    # Применяем цвета ко всем элементам
        s.configure(".", background=BG_COLOR, font=("Segoe UI", 10))
        s.configure("TLabel", background=BG_COLOR, foreground="#000000")
        s.configure("TLabelframe", background=BG_COLOR, foreground="#000000")
        s.configure("TLabelframe.Label", background=BG_COLOR, foreground="#000000", font=("Segoe UI", 11, "bold"))
        s.configure("TButton", background=BTN_COLOR, foreground="#000000", font=("Segoe UI", 10))
        s.configure("RootCount.TLabel", font=("Segoe UI", 14, "bold"), foreground="#003399", background=ENTRY_COLOR)
    
    # Для полей ввода (tk.Entry, не ttk)
        self.root.option_add("*Entry.background", ENTRY_COLOR)
        self.root.option_add("*Entry.foreground", "#000000")
        self.root.option_add("*Entry.font", "Segoe UI 10")
    
    # Для текстового лога
        self.root.option_add("*Text.background", "#FFE4E9")
        self.root.option_add("*Text.foreground", "#000000")
        self.root.option_add("*Text.font", "Consolas 10")
        
    def _enable_paste(self, entry):
        entry.bind("<Control-v>", lambda e: self._do_paste(entry))
        entry.bind("<Control-V>", lambda e: self._do_paste(entry))
        menu = tk.Menu(entry, tearoff=0)
        menu.add_command(label="Вставить", command=lambda: self._do_paste(entry))
        entry.bind("<Button-3>", lambda e: menu.post(e.x_root, e.y_root))

    def _do_paste(self, entry):
        try:
            text = entry.clipboard_get().strip()
            entry.delete(0, tk.END)
            entry.insert(0, text)
            entry.icursor(tk.END)
        except tk.TclError:
            pass

    def _get_valid_int(self, var, name):
        try:
            val = int(var.get().strip())
            return val
        except (ValueError, tk.TclError):
            return None

    def _validate_all(self, mode="encrypt"):
        p = self._get_valid_int(self.p_var, "Модуль p")
        x = self._get_valid_int(self.x_var, "Ключ x")
        
        if None in (p, x):
            messagebox.showerror("Ошибка ввода", "Поля p и x должны содержать целые числа.")
            return None

        if not algorithm.is_prime(p):
            messagebox.showerror("Ошибка", "Модуль p должен быть простым числом.")
            return None

        if mode == "encrypt":
            k = self._get_valid_int(self.k_var, "Ключ k")
            if k is None:
                messagebox.showerror("Ошибка ввода", "Поле k должно содержать целое число.")
                return None
            if p <= 65535:
                messagebox.showerror("Ошибка", "Для 2-байтовых блоков требуется p > 65535.")
                return None
            if not (1 < x < p - 1):
                messagebox.showerror("Ошибка", "x должен удовлетворять условию: 1 < x < p-1.")
                return None
            if not (1 < k < p - 1):
                messagebox.showerror("Ошибка", "k должен удовлетворять условию: 1 < k < p-1.")
                return None
            if math.gcd(k, p - 1) != 1:
                messagebox.showerror("Ошибка", "k и p-1 должны быть взаимно простыми (gcd(k, p-1) == 1).")
                return None
            if self.g_var.get() == 0:
                messagebox.showerror("Ошибка", "Не выбран первообразный корень g.")
                return None
            fpath = self.file_var.get()
            if not fpath or not os.path.exists(fpath):
                messagebox.showerror("Ошибка", "Укажите путь к существующему файлу.")
                return None
            return {"p": p, "x": x, "k": k, "g": self.g_var.get(), "path": fpath}
        
        return {"p": p, "x": x}

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        frm_param = ttk.LabelFrame(main, text="Параметры алгоритма")
        frm_param.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frm_param, text="Модуль p:").grid(row=0, column=0, sticky="e", padx=10, pady=8)
        e_p = ttk.Entry(frm_param, textvariable=self.p_var, width=16)
        e_p.grid(row=0, column=1, sticky="w", padx=5, pady=8)
        self._enable_paste(e_p)

        ttk.Label(frm_param, text="Закрытый ключ x:").grid(row=0, column=2, sticky="e", padx=10, pady=8)
        e_x = ttk.Entry(frm_param, textvariable=self.x_var, width=16)
        e_x.grid(row=0, column=3, sticky="w", padx=5, pady=8)
        self._enable_paste(e_x)

        ttk.Button(frm_param, text="Найти корни", command=self.find_roots).grid(row=0, column=4, padx=10, pady=8)

        ttk.Label(frm_param, textvariable=self.root_count_var, style="RootCount.TLabel").grid(row=1, column=0, columnspan=5, sticky="w", padx=10, pady=6)

        ttk.Label(frm_param, text="Корни g:").grid(row=2, column=0, sticky="ne", padx=10, pady=8)
        # Исправлено: убран background у ttk.Frame
        lb_container = ttk.Frame(frm_param, borderwidth=1, relief="solid")
        lb_container.grid(row=2, column=1, columnspan=3, sticky="ew", padx=5, pady=8)
        self.lb_roots = tk.Listbox(lb_container, height=4, width=48, selectmode=tk.SINGLE, font=("Consolas", 10))
        self.lb_roots.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        ttk.Button(frm_param, text="Выбрать", command=self.select_g).grid(row=2, column=4, sticky="ns", padx=10, pady=8)
        self.lbl_g = ttk.Label(frm_param, text="g = не выбран", foreground="#0044aa", font=("Segoe UI", 10, "bold"))
        self.lbl_g.grid(row=2, column=5, sticky="w", padx=5, pady=8)

        ttk.Label(frm_param, text="Начальный k:").grid(row=3, column=0, sticky="e", padx=10, pady=6)
        e_k = ttk.Entry(frm_param, textvariable=self.k_var, width=16)
        e_k.grid(row=3, column=1, sticky="w", padx=5, pady=6)
        self._enable_paste(e_k)

        frm_file = ttk.LabelFrame(main, text="Файл")
        frm_file.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frm_file, text="Путь:").pack(side=tk.LEFT, padx=10, pady=8)
        e_file = ttk.Entry(frm_file, textvariable=self.file_var)
        e_file.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=8)
        self._enable_paste(e_file)
        ttk.Button(frm_file, text="Обзор", command=self.browse_file).pack(side=tk.RIGHT, padx=10, pady=8)

        frm_act = ttk.Frame(main)
        frm_act.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(frm_act, text="Зашифровать", command=self.encrypt).pack(side=tk.LEFT, padx=30, expand=True)
        ttk.Button(frm_act, text="Расшифровать", command=self.decrypt).pack(side=tk.LEFT, padx=30, expand=True)

        ttk.Separator(main, orient="horizontal").pack(fill=tk.X, pady=10)
        ttk.Label(main, text="Журнал операций:").pack(anchor="w", padx=10, pady=(0, 5))
        self.txt_out = scrolledtext.ScrolledText(main, height=16, state="disabled", font=("Consolas", 10), bg="#ffffff")
        self.txt_out.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def _log(self, msg: str):
        self.txt_out.configure(state="normal")
        self.txt_out.insert(tk.END, msg + "\n")
        self.txt_out.see(tk.END)
        self.txt_out.configure(state="disabled")

    def browse_file(self):
        p = filedialog.askopenfilename(filetypes=[("Все файлы", "*.*")])
        if p: self.file_var.set(p)

    def find_roots(self):
        p = self._get_valid_int(self.p_var, "Модуль p")
        if p is None:
            messagebox.showerror("Ошибка ввода", "Введите корректное целое число для p.")
            return
        if not algorithm.is_prime(p):
            messagebox.showerror("Ошибка", "Число p должно быть простым.")
            return

        self.lb_roots.delete(0, tk.END)
        self._log("Поиск первообразных корней для p = {}...".format(p))
        roots = algorithm.find_primitive_roots(p)
        
        if not roots:
            self._log("Корней не найдено.")
            self.root_count_var.set("")
            return

        self._log("Найдено корней: {}".format(len(roots)))
        for r in roots: self.lb_roots.insert(tk.END, r)
        self.root_count_var.set("Количество найденных корней: {}".format(len(roots)))
        self._log("Выберите значение из списка и нажмите кнопку 'Выбрать'.")

    def select_g(self):
        sel = self.lb_roots.curselection()
        if not sel:
            messagebox.showwarning("Внимание", "Сначала выберите корень из списка.")
            return
        g = self.lb_roots.get(sel[0])
        self.g_var.set(g)
        self.lbl_g.configure(text="g = {}".format(g))
        self._log("Выбран базовый элемент: g = {}".format(g))

    def encrypt(self):
        params = self._validate_all("encrypt")
        if params is None: return

        self._log("Начало шифрования файла: {}".format(params["path"]))
        with open(params["path"], "rb") as f: data = f.read()
        
        self.encrypted_blocks, self.padding_len = algorithm.elgamal_encrypt(
            data, params["p"], params["g"], params["x"], params["k"]
        )

        self._log("Зашифрованные блоки (a, b) в десятичной системе (формат 2 байта):")
        for i, (a, b) in enumerate(self.encrypted_blocks):
            self._log("  Блок {:03d} | a = {:05d} | b = {:05d}".format(i+1, a, b))

        out_enc = params["path"] + ".enc"
        blen = 4
        with open(out_enc, "wb") as f:
            for a, b in self.encrypted_blocks:
                f.write(a.to_bytes(blen, 'big'))
                f.write(b.to_bytes(blen, 'big'))
        self._log("Файл сохранен: {}".format(out_enc))
        if self.padding_len > 0:
            self._log("Примечание: добавлено {} байт дополнения до кратности 2.".format(self.padding_len))
        messagebox.showinfo("Успех", "Шифрование завершено.")

    def decrypt(self):
        params = self._validate_all("decrypt")
        if params is None: return
        
        fpath = self.file_var.get()
        if not fpath.endswith(".enc"):
            messagebox.showerror("Ошибка", "Для расшифровки выберите файл с расширением .enc")
            return

        blen = 4
        with open(fpath, "rb") as f: data = f.read()
        if len(data) % (blen * 2) != 0:
            messagebox.showerror("Ошибка", "Неверный размер зашифрованного файла.")
            return

        blocks = []
        for i in range(0, len(data), blen * 2):
            a = int.from_bytes(data[i:i+blen], 'big')
            b = int.from_bytes(data[i+blen:i+blen*2], 'big')
            blocks.append((a, b))

        self._log("Начало расшифрования файла: {}".format(fpath))
        dec_bytes, dec_vals = algorithm.elgamal_decrypt(blocks, params["p"], params["x"], self.padding_len)

        self._log("Восстановленные блоки (2 байта, десятичная система):")
        for i, val in enumerate(dec_vals):
            tag = " [дополнение]" if (self.padding_len > 0 and i >= len(dec_vals) - (self.padding_len + 1) // 2) else ""
            self._log("  Блок {:03d} | m = {:05d}{}".format(i+1, val, tag))

        out_dec = fpath.replace(".enc", "")
        if not os.path.splitext(out_dec)[1]: out_dec += ".dec"
        with open(out_dec, "wb") as f: f.write(dec_bytes)
        self._log("Файл восстановлен: {}".format(out_dec))
        messagebox.showinfo("Успех", "Расшифрование завершено.")

if __name__ == "__main__":
    root = tk.Tk()
    ElGamalApp(root)
    root.mainloop()