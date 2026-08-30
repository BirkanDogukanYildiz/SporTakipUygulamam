from datetime import date

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import messagebox, ttk

import database

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Spor Takip - Vücut Ölçümleri")
        self.geometry("1000x650")

        database.init_db()

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_form()
        self._build_table_and_chart()

        self.yenile()

    def _build_form(self):
        form = ctk.CTkFrame(self)
        form.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

        alanlar = [
            ("Tarih (YYYY-AA-GG)", "tarih"),
            ("Kilo (kg)", "kilo"),
            ("Yağ Oranı (%)", "yag_orani"),
            ("Kas Oranı (%)", "kas_orani"),
            ("Bel Çevresi (cm)", "bel_cevresi"),
            ("Göğüs Çevresi (cm)", "gogus_cevresi"),
            ("Kol Çevresi (cm)", "kol_cevresi"),
        ]

        self.entries = {}
        for i, (label, key) in enumerate(alanlar):
            ctk.CTkLabel(form, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=5)
            entry = ctk.CTkEntry(form, width=160)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[key] = entry

        self.entries["tarih"].insert(0, date.today().isoformat())

        row = len(alanlar)
        ctk.CTkLabel(form, text="Not").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.not_entry = ctk.CTkEntry(form, width=160)
        self.not_entry.grid(row=row, column=1, padx=5, pady=5)

        row += 1
        ctk.CTkButton(form, text="Kaydet", command=self.kaydet).grid(
            row=row, column=0, columnspan=2, pady=(15, 5), sticky="ew"
        )
        ctk.CTkButton(form, text="Seçili Kaydı Sil", fg_color="darkred", command=self.sil).grid(
            row=row + 1, column=0, columnspan=2, pady=5, sticky="ew"
        )

    def _build_table_and_chart(self):
        right = ctk.CTkFrame(self)
        right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right.grid_rowconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", fieldbackground="#2b2b2b", foreground="white")
        style.configure("Treeview.Heading", background="#1f1f1f", foreground="white")

        columns = ("id", "tarih", "kilo", "yag_orani", "kas_orani", "bel_cevresi", "gogus_cevresi", "kol_cevresi", "not_")
        self.tree = ttk.Treeview(right, columns=columns, show="headings", height=10)
        headers = ["ID", "Tarih", "Kilo", "Yağ %", "Kas %", "Bel", "Göğüs", "Kol", "Not"]
        for col, header in zip(columns, headers):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=80, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.figure = Figure(figsize=(5, 3), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=right)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", pady=(10, 0))

    def kaydet(self):
        tarih = self.entries["tarih"].get().strip()
        if not tarih:
            messagebox.showerror("Hata", "Tarih boş olamaz.")
            return

        def to_float(key):
            val = self.entries[key].get().strip()
            return float(val) if val else None

        try:
            kilo = to_float("kilo")
            yag_orani = to_float("yag_orani")
            kas_orani = to_float("kas_orani")
            bel_cevresi = to_float("bel_cevresi")
            gogus_cevresi = to_float("gogus_cevresi")
            kol_cevresi = to_float("kol_cevresi")
        except ValueError:
            messagebox.showerror("Hata", "Sayısal alanlara geçerli bir sayı giriniz.")
            return

        not_ = self.not_entry.get().strip()

        database.kayit_ekle(tarih, kilo, yag_orani, kas_orani, bel_cevresi, gogus_cevresi, kol_cevresi, not_)
        self.yenile()

        for key in self.entries:
            if key != "tarih":
                self.entries[key].delete(0, "end")
        self.not_entry.delete(0, "end")

    def sil(self):
        secili = self.tree.selection()
        if not secili:
            messagebox.showinfo("Bilgi", "Silmek için bir kayıt seçin.")
            return
        kayit_id = self.tree.item(secili[0])["values"][0]
        database.kayit_sil(kayit_id)
        self.yenile()

    def yenile(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        kayitlar = database.tum_kayitlari_getir()
        for k in kayitlar:
            self.tree.insert("", "end", values=(
                k["id"], k["tarih"], k["kilo"], k["yag_orani"], k["kas_orani"],
                k["bel_cevresi"], k["gogus_cevresi"], k["kol_cevresi"], k["not_"] or ""
            ))

        self._grafik_ciz(kayitlar)

    def _grafik_ciz(self, kayitlar):
        self.ax.clear()
        tarihler = [k["tarih"] for k in kayitlar]
        kilolar = [k["kilo"] for k in kayitlar]
        yaglar = [k["yag_orani"] for k in kayitlar]
        kaslar = [k["kas_orani"] for k in kayitlar]

        if any(v is not None for v in kilolar):
            self.ax.plot(tarihler, kilolar, marker="o", label="Kilo")
        if any(v is not None for v in yaglar):
            self.ax.plot(tarihler, yaglar, marker="o", label="Yağ %")
        if any(v is not None for v in kaslar):
            self.ax.plot(tarihler, kaslar, marker="o", label="Kas %")

        self.ax.set_title("Zaman İçinde Değişim")
        if self.ax.get_legend_handles_labels()[0]:
            self.ax.legend()
        self.figure.autofmt_xdate(rotation=45)
        self.canvas.draw()


if __name__ == "__main__":
    app = App()
    app.mainloop()
