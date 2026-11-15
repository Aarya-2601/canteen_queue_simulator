"""
models/menu_item.py - MenuItem class for VJTI Canteen.
Owner: Chaiti
"""


class MenuItem:
    """Represents a food or beverage item on the canteen menu."""

    def __init__(self, item_id, name, category, price, prep_time, popularity_weight=1.0,
                 stock_limit=None, is_combo=False, combo_items=None):
        self.item_id = str(item_id)
        self.name = str(name)
        self.category = str(category)
        self.price = float(price)
        self.prep_time = float(prep_time)
        self.popularity_weight = float(popularity_weight)
        self.stock_limit = int(stock_limit) if stock_limit is not None else None
        self.stock_remaining = self.stock_limit
        self.is_combo = bool(is_combo)
        self.combo_items = list(combo_items) if combo_items else []

    def is_available(self, qty=1):
        """Check if item is in stock."""
        if self.stock_limit is None:
            return True
        return self.stock_remaining is not None and self.stock_remaining >= qty

    def reduce_stock(self, qty=1):
        """Deduct stock when ordered."""
        if self.is_available(qty):
            if self.stock_remaining is not None:
                self.stock_remaining -= qty
            return True
        return False

    def restock(self):
        """Reset stock to initial limit."""
        self.stock_remaining = self.stock_limit

    def to_dict(self):
        return {
            "item_id": self.item_id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "prep_time": self.prep_time,
            "is_combo": self.is_combo,
        }

    def __repr__(self):
        return f"MenuItem('{self.name}', ₹{self.price})"
