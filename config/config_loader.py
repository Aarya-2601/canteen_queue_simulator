"""
config/config_loader.py - Loads JSON config and CSV menu.
Owner: Chaiti
"""

import os
import json
import csv
from models.menu_item import MenuItem


def validate_config(config):
    """Validates that config is a dict and has counters defined."""
    if not isinstance(config, dict):
        raise ValueError("Config must be a dictionary.")
    if "counters" not in config:
        raise ValueError("Config missing 'counters' section.")
    return True


def load_config(path="config/canteen_config.json"):
    """Loads and returns simulation configuration dictionary."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)

    validate_config(config)
    return config


def load_menu(path="data/menu.csv"):
    """Parses menu CSV into a list of MenuItem objects."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Menu file not found: {path}")

    items = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            combo_str = row.get("combo_items", "").strip()
            combos = [c.strip() for c in combo_str.split(";") if c.strip()] if combo_str else []
            item = MenuItem(
                item_id=row.get("item_id", ""),
                name=row.get("name", ""),
                category=row.get("category", "General"),
                price=float(row.get("price", 0.0)),
                prep_time=float(row.get("prep_time", 1.0)),
                popularity_weight=float(row.get("popularity_weight", 1.0)),
                stock_limit=int(row["stock_limit"]) if row.get("stock_limit") else None,
                is_combo=str(row.get("is_combo", "")).lower() in ["true", "1"],
                combo_items=combos
            )
            items.append(item)
    return items


def save_config(config, path="config/canteen_config.json"):
    """Saves config dictionary to JSON."""
    validate_config(config)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def get_default_config():
    """Fallback default configuration."""
    return load_config() if os.path.exists("config/canteen_config.json") else {}
