"""Panneau Tkinter réutilisable : deux curseurs q1 / q4 (en degrés) + affichage de l'état."""
from __future__ import annotations

import math
import tkinter as tk
from tkinter import ttk
from typing import Callable


class SliderPanel(ttk.Frame):
    """Curseurs de consigne q1, q4 et zone d'affichage des mesures.

    on_change(q1_rad, q4_rad) est appelé à chaque mouvement d'un curseur.
    """

    def __init__(self, master, ranges_rad: dict[str, tuple[float, float]],
                 initial_rad: dict[str, float], on_change: Callable[[float, float], None]):
        super().__init__(master, padding=10)
        self._on_change = on_change
        self.vars: dict[str, tk.DoubleVar] = {}
        ttk.Label(self, text="Consignes des moteurs (angles absolus / x0)",
                  font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, columnspan=3, sticky="w")
        for row, name in enumerate(("q1", "q4"), start=1):
            lo, hi = (math.degrees(v) for v in ranges_rad[name])
            var = tk.DoubleVar(value=round(math.degrees(initial_rad[name]), 1))
            self.vars[name] = var
            ttk.Label(self, text=f"{name} [°]").grid(row=row, column=0, sticky="w")
            scale = tk.Scale(self, from_=lo, to=hi, resolution=0.1, orient=tk.HORIZONTAL,
                             length=380, variable=var, command=lambda _v: self._changed())
            scale.grid(row=row, column=1, sticky="ew")
        ttk.Button(self, text="Home", command=self.reset_to_initial).grid(row=3, column=1, sticky="e")
        self._initial = dict(initial_rad)
        self.status = tk.StringVar(value="")
        ttk.Label(self, textvariable=self.status, font=("TkFixedFont", 10), justify="left").grid(
            row=4, column=0, columnspan=3, sticky="w", pady=(10, 0))
        self.columnconfigure(1, weight=1)

    def values_rad(self) -> tuple[float, float]:
        return math.radians(self.vars["q1"].get()), math.radians(self.vars["q4"].get())

    def set_values_rad(self, q1: float, q4: float) -> None:
        self.vars["q1"].set(round(math.degrees(q1), 1))
        self.vars["q4"].set(round(math.degrees(q4), 1))

    def reset_to_initial(self) -> None:
        self.set_values_rad(self._initial["q1"], self._initial["q4"])
        self._changed()

    def _changed(self) -> None:
        self._on_change(*self.values_rad())
