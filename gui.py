import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import algorithm
import math

class ElGamalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("El-Gamal Encryption System")
        self.root.geometry("900x750")
        
        self.p_var = tk.StringVar()
        self.x_var = tk.StringVar()
        self.k_var = tk.StringVar()
        self.g_var = tk.IntVar(value=0)
        self.file_var = tk.StringVar()
        self.root_count_var = tk.StringVar(value="Корни не вычислены")
        
        self._setup_style()
        self._build_ui()

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("Blue.TLabel", font=("Segoe UI", 16, "bold"), foreground="#0056b3")
        style.configure("Card.TLabelframe", padding=15)

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        # Параметры
        params_frame = ttk.LabelFrame(container, text=" Параметры ключей ", style="Card.TLabelframe")
        params_frame.pack(fill=tk.X, pady=5)

        inputs_grid = ttk.Frame(params_frame)
        inputs_grid.pack(fill=tk.X)

        cols = [("Модуль (p):", self.p_var), ("Закрытый ключ (x):", self.x_var), ("Начальное k:", self.k_var)]
        for i, (label, var) in enumerate(cols):
            ttk.Label(inputs_grid, text=label).grid(row=0, column=i*2, padx=5, pady=5, sticky="w")
            ttk.Entry(inputs_grid, textvariable=var, width=15).grid(row=0, column=i*2+1, padx=5, pady=5)

        ttk.Button(inputs_grid, text="Проверить параметры", command=self.validate_all_inputs).grid(row=0, column=6, padx=10)

        roots_section = ttk.Frame(params_frame)
        roots_section.pack(fill=tk.X, pady=10)

        ttk.Label(roots_section, textvariable=self.root_count_var, style="Blue.TLabel").pack(anchor="w", pady=(0, 10))

        list_container = ttk.Frame(roots_section)
        list_container.pack(fill=tk.X)

        self.lb_roots = tk.Listbox(list_container, height=6, font=("Consolas", 10), exportselection=False)
        self.lb_roots.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        scroller = ttk.Scrollbar(list_container, orient="vertical", command=self.lb_roots.yview)
        scroller.pack(side=tk.LEFT, fill=tk.Y)
        self.lb_roots.config(yscrollcommand=scroller.set)

        btns_roots = ttk.Frame(roots_section)
        btns_roots.pack(fill=tk.X, pady=5)
        
        ttk.Button(btns_roots, text="Найти все корни g", command=self.find_roots).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns_roots, text="Выбрать выделенный", command=self.select_g).pack(side=tk.LEFT, padx=5)
        self.lbl_g_display = ttk.Label(btns_roots, text="Выбран g: ---", font=("Segoe UI", 10, "bold"))
        self.lbl_g_display.pack(side=tk.LEFT, padx=15)

        file_frame = ttk.Frame(container, padding=5)
        file_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(file_frame, text="Файл:").pack(side=tk.LEFT)
        ttk.Entry(file_frame, textvariable=self.file_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(file_frame, text="Обзор", command=self.browse_file).pack(side=tk.LEFT)

        actions_frame = ttk.Frame(container)
        actions_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(actions_frame, text="ЗАШИФРОВАТЬ", command=self.encrypt).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ttk.Button(actions_frame, text="РАСШИФРОВАТЬ", command=self.decrypt).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        ttk.Label(container, text="Журнал событий:").pack(anchor="w")
        self.txt_log = scrolledtext.ScrolledText(container, height=12, font=("Consolas", 9), state="disabled")
        self.txt_log.pack(fill=tk.BOTH, expand=True, pady=5)

    def _log_status(self, msg):
        self.txt_log.configure(state="normal")
        self.txt_log.insert(tk.END, f"> {msg}\n")
        self.txt_log.see(tk.END)
        self.txt_log.configure(state="disabled")

    def validate_all_inputs(self):
        self._log_status("--- Проверка параметров ---")
        try:
            p = int(self.p_var.get())
            if not algorithm.is_prime(p):
                self._log_status(f"ОШИБКА: p={p} не простое.")
            elif p <= 255:
                self._log_status(f"ОШИБКА: p={p} должно быть > 255.")
            else:
                self._log_status(f"ОК: p подходит.")

            x = int(self.x_var.get())
            if not (1 < x < p - 1):
                self._log_status(f"ОШИБКА: x={x} вне (1, {p-1}).")
            else:
                self._log_status("ОК: x подходит.")

            k = int(self.k_var.get())
            if not (1 < k < p - 1):
                self._log_status(f"ОШИБКА: k={k} вне (1, {p-1}).")
            elif math.gcd(k, p - 1) != 1:
                self._log_status(f"ОШИБКА: НОД(k, p-1)={math.gcd(k, p-1)} != 1.")
            else:
                self._log_status("ОК: k подходит.")
        except:
            self._log_status("ОШИБКА: введите целые числа.")

    def browse_file(self):
        p = filedialog.askopenfilename()
        if p: self.file_var.set(p)

    def find_roots(self):
        try:
            p = int(self.p_var.get())
            self.lb_roots.delete(0, tk.END)
            roots = algorithm.find_primitive_roots(p)
            for r in roots: self.lb_roots.insert(tk.END, r)
            self.root_count_var.set(f"Найдено корней: {len(roots)}")
            self._log_status(f"Найдено {len(roots)} корней.")
        except:
            messagebox.showerror("Ошибка", "Проверьте число p")

    def select_g(self):
        sel = self.lb_roots.curselection()
        if sel:
            g = self.lb_roots.get(sel[0])
            self.g_var.set(g)
            self.lbl_g_display.config(text=f"Выбран g: {g}")
            self._log_status(f"Выбрано g={g}")

    def encrypt(self):
        try:
            p, g, x, k = int(self.p_var.get()), self.g_var.get(), int(self.x_var.get()), int(self.k_var.get())
            path = self.file_var.get()
            if not path: raise ValueError("Выберите файл")
            
            with open(path, "rb") as f: data = f.read()
            blocks, _ = algorithm.elgamal_encrypt(data, p, g, x, k)
            
            out_path = path + ".enc"
            with open(out_path, "wb") as f:
                for a, b in blocks:
                    f.write(a.to_bytes(2, 'big'))
                    f.write(b.to_bytes(2, 'big'))
            self._log_status(f"Зашифровано: {out_path}")
            messagebox.showinfo("Успех", "Шифрование завершено")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def decrypt(self):
        try:
            p, x = int(self.p_var.get()), int(self.x_var.get())
            path = self.file_var.get()
            with open(path, "rb") as f:
                data = f.read()
            
            blocks = []
            for i in range(0, len(data), 4):
                a = int.from_bytes(data[i:i+2], 'big')
                b = int.from_bytes(data[i+2:i+4], 'big')
                blocks.append((a, b))
            
            dec_bytes, _ = algorithm.elgamal_decrypt(blocks, p, x, 0)
            save_path = filedialog.asksaveasfilename()
            if save_path:
                with open(save_path, "wb") as f: f.write(dec_bytes)
                self._log_status(f"Расшифровано: {save_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = ElGamalApp(root)
    root.mainloop()