import os
import threading
from datetime import datetime, timedelta
from tkinter import Tk, StringVar, ttk, messagebox

from app import App
from utils import validate_date_range


def default_dates():
    end = datetime.now().replace(microsecond=0, second=0)
    start = end - timedelta(days=7)
    return start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")


class RuidoGUI:
    def __init__(self) -> None:
        self.app = App()
        self.root = Tk()
        self.root.title("Consultas Ruido SIATA")
        self.root.geometry("520x320")

        self.token_var = StringVar(value=os.getenv("AMVA_TOKEN", ""))
        self.start_var = StringVar()
        self.end_var = StringVar()
        self.station_var = StringVar()

        s, e = default_dates()
        self.start_var.set(s)
        self.end_var.set(e)

        frm = ttk.Frame(self.root, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Token (x-token)").grid(row=0, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.token_var, width=55).grid(row=0, column=1, sticky="we")

        ttk.Label(frm, text="Inicio (YYYY-MM-DD hh:mm:ss)").grid(row=1, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.start_var, width=25).grid(row=1, column=1, sticky="w")

        ttk.Label(frm, text="Fin (YYYY-MM-DD hh:mm:ss)").grid(row=2, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.end_var, width=25).grid(row=2, column=1, sticky="w")

        ttk.Label(frm, text="Estación").grid(row=3, column=0, sticky="w")
        self.station_combo = ttk.Combobox(frm, textvariable=self.station_var, width=52)
        self.station_combo.grid(row=3, column=1, sticky="we")

        btns = ttk.Frame(frm)
        btns.grid(row=4, column=0, columnspan=2, pady=10, sticky="we")

        ttk.Button(btns, text="Actualizar estaciones", command=self.load_stations).grid(row=0, column=0, padx=5)
        ttk.Button(btns, text="Stations → CSV", command=self.run_stations).grid(row=0, column=1, padx=5)
        ttk.Button(btns, text="Todas estaciones → CSV", command=self.run_all).grid(row=0, column=2, padx=5)
        ttk.Button(btns, text="Una estación → CSV", command=self.run_one).grid(row=0, column=3, padx=5)

        for i in range(2):
            frm.columnconfigure(i, weight=1)

    def ensure_token(self) -> None:
        token = self.token_var.get().strip()
        if token:
            os.environ["AMVA_TOKEN"] = token

    def load_stations(self) -> None:
        def _task():
            try:
                self.ensure_token()
                data = self.app.call_and_maybe_export("stations")
                items = []
                raw_rows = data if isinstance(data, list) else data.get("data", []) if isinstance(data, dict) else []
                for r in raw_rows:
                    if isinstance(r, dict):
                        value = str(r.get("id") or r.get("station") or r.get("code") or r.get("name") or "")
                        label = str(r.get("name") or r.get("station") or r.get("code") or r.get("id") or value)
                    else:
                        value = str(r)
                        label = value
                    if value:
                        items.append(f"{label} | {value}")
                def _apply():
                    self.station_combo["values"] = items
                    if items:
                        self.station_combo.current(0)
                    messagebox.showinfo("Listo", "Estaciones actualizadas. Se exportó stations.csv")
                self.root.after(0, _apply)
            except Exception as e:
                msg = str(e)
                self.root.after(0, lambda m=msg: messagebox.showerror("Error", m))

        threading.Thread(target=_task, daemon=True).start()

    def run_all(self) -> None:
        def _task():
            try:
                self.ensure_token()
                validate_date_range(self.start_var.get(), self.end_var.get())
                self.app.call_and_maybe_export(
                    "all_stations_noise_data",
                    {
                        "start_date": self.start_var.get(),
                        "end_date": self.end_var.get(),
                    },
                )
                messagebox.showinfo("Listo", "Exportado: all_stations_noise_data.csv")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        threading.Thread(target=_task, daemon=True).start()

    def run_one(self) -> None:
        def _task():
            try:
                self.ensure_token()
                validate_date_range(self.start_var.get(), self.end_var.get())
                raw = self.station_var.get().strip()
                station = raw.split("|")[-1].strip() if "|" in raw else raw
                if not station:
                    raise ValueError("Selecciona una estación")
                self.app.call_and_maybe_export(
                    "station_noise_data",
                    {
                        "station": station,
                        "start_date": self.start_var.get(),
                        "end_date": self.end_var.get(),
                    },
                )
                messagebox.showinfo("Listo", "Exportado: station_noise_data.csv")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        threading.Thread(target=_task, daemon=True).start()

    def run_stations(self) -> None:
        def _task():
            try:
                self.ensure_token()
                self.app.call_and_maybe_export("stations")
                messagebox.showinfo("Listo", "Exportado: stations.csv")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        threading.Thread(target=_task, daemon=True).start()

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    RuidoGUI().run()


