"""Colours, fonts and ttk theme for the whole app (owner: Jiya).

Every visual constant lives here so the look can be changed in one place.
Other UI modules import ``PALETTE``, ``FONTS`` and call ``apply_theme(root)`` once.
"""

from tkinter import ttk

PALETTE = {
    "bg": "#F4F6FA",          # window background
    "surface": "#FFFFFF",     # cards, tables
    "primary": "#1E4E8C",     # header, headings, KPI numbers
    "primary_dark": "#163A69",
    "accent": "#E8870E",      # main action buttons
    "accent_dark": "#C26F06",
    "text": "#1F2933",
    "muted": "#6B7785",
    "border": "#D5DBE3",
    "good": "#2E8B57",
    "bad": "#C0392B",
    "header_text": "#FFFFFF",
}

FONT_FAMILY = "Segoe UI"  # Tk falls back to a default font if this is missing

FONTS = {
    "base": (FONT_FAMILY, 10),
    "small": (FONT_FAMILY, 9),
    "bold": (FONT_FAMILY, 10, "bold"),
    "heading": (FONT_FAMILY, 13, "bold"),
    "title": (FONT_FAMILY, 17, "bold"),
    "kpi_value": (FONT_FAMILY, 22, "bold"),
    "kpi_label": (FONT_FAMILY, 9),
    "mono": ("Consolas", 10),
}


def apply_theme(root) -> ttk.Style:
    """Configure the ttk theme and named styles used across the app."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:  # theme missing on an unusual Tk build - keep the default
        pass

    p, f = PALETTE, FONTS
    root.configure(background=p["bg"])

    style.configure(".", font=f["base"], background=p["bg"], foreground=p["text"])
    style.configure("TFrame", background=p["bg"])
    style.configure("TLabel", background=p["bg"], foreground=p["text"])
    style.configure("Muted.TLabel", foreground=p["muted"], font=f["small"])
    style.configure("Heading.TLabel", font=f["heading"], foreground=p["primary"])
    style.configure("Good.TLabel", foreground=p["good"], font=f["bold"])
    style.configure("Bad.TLabel", foreground=p["bad"], font=f["bold"])

    # Header bar
    style.configure("Header.TFrame", background=p["primary"])
    style.configure("HeaderTitle.TLabel", background=p["primary"],
                    foreground=p["header_text"], font=f["title"])
    style.configure("HeaderSub.TLabel", background=p["primary"],
                    foreground="#C9D8EE", font=f["small"])

    # Cards (KPI tiles, panels)
    style.configure("Card.TFrame", background=p["surface"],
                    bordercolor=p["border"], borderwidth=1, relief="solid")
    style.configure("Card.TLabel", background=p["surface"], foreground=p["text"])
    style.configure("KpiValue.TLabel", background=p["surface"],
                    foreground=p["primary"], font=f["kpi_value"])
    style.configure("KpiLabel.TLabel", background=p["surface"],
                    foreground=p["muted"], font=f["kpi_label"])

    # Buttons
    style.configure("TButton", padding=(12, 6), font=f["base"])
    style.configure("Accent.TButton", background=p["accent"], foreground="#FFFFFF",
                    font=f["bold"], padding=(16, 8), borderwidth=0)
    style.map("Accent.TButton",
              background=[("disabled", p["border"]), ("active", p["accent_dark"])],
              foreground=[("disabled", p["muted"])])
    style.configure("Switch.TButton", padding=(12, 5), font=f["bold"])

    # Notebook (tabs)
    style.configure("TNotebook", background=p["bg"], borderwidth=0)
    style.configure("TNotebook.Tab", padding=(16, 8), font=f["bold"],
                    background=p["border"], foreground=p["text"])
    style.map("TNotebook.Tab",
              background=[("selected", p["surface"])],
              foreground=[("selected", p["primary"])])

    # Tables
    style.configure("Treeview", rowheight=26, font=f["base"],
                    background=p["surface"], fieldbackground=p["surface"],
                    bordercolor=p["border"])
    style.configure("Treeview.Heading", font=f["bold"], background=p["primary"],
                    foreground="#FFFFFF", padding=(6, 6))
    style.map("Treeview.Heading", background=[("active", p["primary_dark"])])
    style.map("Treeview", background=[("selected", "#CFE0F5")],
              foreground=[("selected", p["text"])])

    # Misc
    style.configure("TLabelframe", background=p["bg"], bordercolor=p["border"])
    style.configure("TLabelframe.Label", background=p["bg"],
                    foreground=p["primary"], font=f["bold"])
    style.configure("Horizontal.TProgressbar", troughcolor=p["border"],
                    background=p["accent"], bordercolor=p["border"])
    style.configure("TCombobox", padding=4)
    style.configure("TEntry", padding=4)
    style.configure("TSpinbox", padding=4)
    return style
