"""
Unit Converter
--------------
A Tkinter desktop app that converts values between units across categories:
    - Length, Weight, Temperature, Volume, Speed

Features:
    - Category dropdown (units update automatically based on category)
    - From / To unit dropdowns with a swap (↔) button
    - Live conversion as you type (no need to click a button)
    - Dark / Light theme toggle (same plum color theme as the clock app)
"""

import tkinter as tk
from tkinter import ttk


# ================= COLOR THEME (same palette as the clock app) =================

THEMES = {
    "dark": {
        "bg": "#0A2947",      # deep navy background
        "card": "#2F4963",    # lighter navy card
        "text": "#F3E4C9",    # cream text
        "accent": "#976E50",  # lightened brown so it stands out on navy
        "muted": "#D3D4C0",   # sage for secondary text
    },
    "light": {
        "bg": "#F3E4C9",      # cream background
        "card": "#F9F2E4",    # near-white cream card
        "text": "#0A2947",    # navy text
        "accent": "#8B5E3C",  # brown accent
        "muted": "#939486",   # darkened sage for secondary text
    },
}

dark_mode = True


# ================= CONVERSION DATA =================
#
# Each category maps every unit to "how many base units it equals".
# To convert: value -> base units -> target unit.
# Temperature doesn't fit this pattern (it has offsets), so it's handled
# separately with its own formulas.

LENGTH = {  # base unit: meter
    "Meter": 1,
    "Kilometer": 1000,
    "Centimeter": 0.01,
    "Millimeter": 0.001,
    "Mile": 1609.34,
    "Yard": 0.9144,
    "Foot": 0.3048,
    "Inch": 0.0254,
}

WEIGHT = {  # base unit: gram
    "Gram": 1,
    "Kilogram": 1000,
    "Milligram": 0.001,
    "Pound": 453.592,
    "Ounce": 28.3495,
    "Tonne": 1_000_000,
}

VOLUME = {  # base unit: liter
    "Liter": 1,
    "Milliliter": 0.001,
    "Cubic Meter": 1000,
    "Gallon (US)": 3.78541,
    "Quart (US)": 0.946353,
    "Cup (US)": 0.236588,
}

SPEED = {  # base unit: meters per second
    "Meter/sec": 1,
    "Kilometer/hour": 0.277778,
    "Mile/hour": 0.44704,
    "Knot": 0.514444,
}

TEMPERATURE_UNITS = ["Celsius", "Fahrenheit", "Kelvin"]

CATEGORIES = {
    "Length": LENGTH,
    "Weight": WEIGHT,
    "Volume": VOLUME,
    "Speed": SPEED,
    "Temperature": None,   # handled specially
}


def convert_temperature(value, from_unit, to_unit):
    """Convert between Celsius, Fahrenheit and Kelvin (these need formulas, not simple ratios)."""
    # Step 1: convert input to Celsius first
    if from_unit == "Celsius":
        celsius = value
    elif from_unit == "Fahrenheit":
        celsius = (value - 32) * 5 / 9
    else:  # Kelvin
        celsius = value - 273.15

    # Step 2: convert from Celsius to the target unit
    if to_unit == "Celsius":
        return celsius
    elif to_unit == "Fahrenheit":
        return celsius * 9 / 5 + 32
    else:  # Kelvin
        return celsius + 273.15


def convert_value(value, category, from_unit, to_unit):
    """General-purpose converter: dispatches to temperature logic or ratio-based math."""
    if category == "Temperature":
        return convert_temperature(value, from_unit, to_unit)

    units = CATEGORIES[category]
    value_in_base_units = value * units[from_unit]
    return value_in_base_units / units[to_unit]


# ================= MAIN WINDOW =================

root = tk.Tk()
root.title("Unit Converter")
root.geometry("460x520")
root.minsize(380, 460)
root.resizable(True, True)

FONT_FAMILY = "Segoe UI"


# ================= THEME =================

def apply_theme():
    """Repaint every widget using the colors for the current theme."""
    theme = THEMES["dark"] if dark_mode else THEMES["light"]

    root.configure(bg=theme["bg"])
    container.configure(bg=theme["bg"])

    for card in cards:
        card.configure(bg=theme["card"])

    for widget in section_titles:
        widget.configure(bg=theme["card"], fg=theme["muted"])

    result_label.configure(bg=theme["card"], fg=theme["accent"])

    style.configure("TButton", background=theme["accent"], foreground="#ffffff")
    style.configure("TEntry", fieldbackground=theme["bg"])
    style.configure("TCombobox", fieldbackground=theme["bg"])

    theme_button.config(text="☀️  Light Mode" if dark_mode else "🌙  Dark Mode")


def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    apply_theme()


# ================= APP LOGIC =================

def refresh_unit_dropdowns(*_):
    """
    Called whenever the category changes.
    Repopulates the From/To dropdowns with units that belong to the new category.
    """
    category = category_combo.get()
    units = TEMPERATURE_UNITS if category == "Temperature" else list(CATEGORIES[category].keys())

    from_combo.config(values=units)
    to_combo.config(values=units)

    from_combo.set(units[0])
    to_combo.set(units[1] if len(units) > 1 else units[0])

    run_conversion()


def run_conversion(*_):
    """Read the current inputs and update the result label. Runs live as you type."""
    try:
        value = float(value_entry.get())
        category = category_combo.get()
        from_unit = from_combo.get()
        to_unit = to_combo.get()

        result = convert_value(value, category, from_unit, to_unit)
        result_label.config(text=f"{result:,.4f} {to_unit}")
    except ValueError:
        result_label.config(text="Enter a valid number")
    except (KeyError, ZeroDivisionError):
        result_label.config(text="—")


def swap_units():
    """Swap the From and To unit selections, then re-run the conversion."""
    from_unit = from_combo.get()
    to_unit = to_combo.get()
    from_combo.set(to_unit)
    to_combo.set(from_unit)
    run_conversion()


# ================= GUI LAYOUT =================

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=(FONT_FAMILY, 11, "bold"), padding=8, borderwidth=0)
style.configure("TEntry", font=(FONT_FAMILY, 13), padding=6)
style.configure("TCombobox", font=(FONT_FAMILY, 11), padding=6)

container = tk.Frame(root, padx=20, pady=20)
container.pack(fill="both", expand=True)

cards = []
section_titles = []


def make_card(parent, pad_y=(0, 16)):
    card = tk.Frame(parent, padx=18, pady=16, highlightthickness=0)
    card.pack(fill="x", pady=pad_y)
    cards.append(card)
    return card


def make_section_title(card, text):
    label = tk.Label(card, text=text, font=(FONT_FAMILY, 10, "bold"), anchor="w")
    label.pack(fill="x", pady=(0, 8))
    section_titles.append(label)
    return label


# --- Category card ---
category_card = make_card(container)
make_section_title(category_card, "CATEGORY")
category_combo = ttk.Combobox(category_card, values=list(CATEGORIES.keys()), state="readonly")
category_combo.set("Length")
category_combo.pack(fill="x")
category_combo.bind("<<ComboboxSelected>>", refresh_unit_dropdowns)

# --- Input value card ---
value_card = make_card(container)
make_section_title(value_card, "VALUE TO CONVERT")
value_entry = ttk.Entry(value_card, font=(FONT_FAMILY, 16))
value_entry.insert(0, "1")
value_entry.pack(fill="x")
value_entry.bind("<KeyRelease>", run_conversion)

# --- From / To card ---
units_card = make_card(container)

from_to_row = tk.Frame(units_card)
from_to_row.pack(fill="x")
from_to_row.columnconfigure(0, weight=1)
from_to_row.columnconfigure(1, weight=0)
from_to_row.columnconfigure(2, weight=1)

from_box = tk.Frame(from_to_row)
from_box.grid(row=0, column=0, sticky="ew")
make_section_title(from_box, "FROM")
from_combo = ttk.Combobox(from_box, state="readonly")
from_combo.pack(fill="x")
from_combo.bind("<<ComboboxSelected>>", run_conversion)

ttk.Button(from_to_row, text="⇄", width=3, command=swap_units).grid(row=0, column=1, padx=10)

to_box = tk.Frame(from_to_row)
to_box.grid(row=0, column=2, sticky="ew")
make_section_title(to_box, "TO")
to_combo = ttk.Combobox(to_box, state="readonly")
to_combo.pack(fill="x")
to_combo.bind("<<ComboboxSelected>>", run_conversion)

# --- Result card ---
result_card = make_card(container)
make_section_title(result_card, "RESULT")
result_label = tk.Label(result_card, font=(FONT_FAMILY, 26, "bold"))
result_label.pack(fill="x", pady=(4, 0))

# --- Theme toggle ---
theme_button = ttk.Button(container, command=toggle_theme)
theme_button.pack(pady=(10, 0))


# ================= START =================

apply_theme()
refresh_unit_dropdowns()   # populate From/To with Length units and run first conversion

root.mainloop()