"""
tests/test_models_config.py
Owner: Chaiti

Comprehensive unit test suite for:
- MenuItem, Customer, and Counter domain models
- Configuration loader and validation (canteen_config.json)
- Menu CSV parsing (data/menu.csv)
- Matplotlib plotting functions and 2x2 executive dashboard

Can be run via:
    pytest tests/test_models_config.py -v
or:
    python -m unittest tests/test_models_config.py -v
"""

import os
import math
import unittest
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from models.menu_item import MenuItem
from models.customer import Customer
from models.counter import Counter
from config.config_loader import load_config, load_menu, validate_config, get_default_config
from visualization.plots import (
    plot_wait_by_hour,
    plot_queue_lengths,
    plot_utilisation,
    plot_wait_histogram,
    plot_scenario_comparison,
)
from visualization.dashboard import plot_dashboard


class TestMenuItem(unittest.TestCase):
    """Tests for the MenuItem model."""

    def test_menu_item_initialization(self):
        item = MenuItem(
            item_id="ITM01",
            name="Vada Pav",
            category="Snacks",
            price=15.0,
            prep_time=1.0,
            popularity_weight=0.2,
            stock_limit=100,
            is_combo=False
        )
        self.assertEqual(item.name, "Vada Pav")
        self.assertEqual(item.price, 15.0)
        self.assertEqual(item.stock_remaining, 100)
        self.assertTrue(item.is_available())

    def test_stock_depletion_and_restock(self):
        item = MenuItem("ITM02", "Samosa Pav", "Snacks", 18.0, 1.0, stock_limit=2)
        self.assertTrue(item.reduce_stock(1))
        self.assertEqual(item.stock_remaining, 1)
        self.assertTrue(item.reduce_stock(1))
        self.assertEqual(item.stock_remaining, 0)
        self.assertFalse(item.is_available(1))
        self.assertFalse(item.reduce_stock(1))  # out of stock

        item.restock()
        self.assertEqual(item.stock_remaining, 2)
        self.assertTrue(item.is_available(1))

    def test_combo_bundle(self):
        combo = MenuItem(
            item_id="ITM18",
            name="Samosa Pav + Cutting Chai",
            category="Combos",
            price=25.0,
            prep_time=1.2,
            is_combo=True,
            combo_items=["Samosa Pav", "Cutting Chai"]
        )
        self.assertTrue(combo.is_combo)
        self.assertEqual(len(combo.combo_items), 2)
        self.assertIn("Cutting Chai", combo.combo_items)


class TestCustomer(unittest.TestCase):
    """Tests for Customer lifecycle and contract serialization."""

    def test_customer_lifecycle_normal(self):
        c = Customer(
            customer_id=1,
            arrival_time=10,
            counter="Snacks",
            items="Vada Pav",
            queue_length_on_arrival=2,
            balking_threshold=5,
            order_value=15.0,
        )
        self.assertFalse(c.balked)

        # Start service at minute 14
        c.start_service(current_time=14.0)
        self.assertEqual(c.service_start, 14.0)
        self.assertEqual(c.wait_time, 4.0)

        # Complete service at minute 16
        c.service_time = 2.0
        c.complete_service(current_time=16.0)
        self.assertEqual(c.departure, 16.0)
        self.assertFalse(c.balked)

    def test_customer_balking(self):
        c = Customer(customer_id=2, arrival_time=50, counter="Thali", balking_threshold=4)
        balked = c.check_balk(current_queue_length=7)
        self.assertTrue(balked)
        self.assertTrue(c.balked)
        self.assertTrue(math.isnan(c.wait_time))

    def test_to_dict_matches_contract(self):
        c = Customer(
            customer_id=42,
            arrival_time=100,
            counter="Beverages",
            items="Cutting Chai",
            order_value=12.0,
            service_time=1.0,
        )
        c.start_service(105.0)
        c.complete_service(106.0)
        d = c.to_dict()

        expected_keys = {
            "customer_id", "arrival_time", "counter", "items",
            "queue_length_on_arrival", "service_start", "departure",
            "wait_time", "service_time", "order_value", "balked"
        }
        self.assertTrue(expected_keys.issubset(set(d.keys())))
        self.assertEqual(d["customer_id"], 42)
        self.assertEqual(d["wait_time"], 5.0)
        self.assertFalse(d["balked"])


class TestCounter(unittest.TestCase):
    """Tests for Counter parallel queue servicing and utilisation."""

    def test_counter_queue_and_step(self):
        counter = Counter(name="Snacks", staff_count=2, balking_queue_limit=10)
        c1 = Customer(customer_id=1, arrival_time=0)
        c1._prep = 2.0
        c2 = Customer(customer_id=2, arrival_time=0)
        c2._prep = 3.0
        c3 = Customer(customer_id=3, arrival_time=0)
        c3._prep = 1.0

        counter.add_to_queue(c1)
        counter.add_to_queue(c2)
        counter.add_to_queue(c3)

        self.assertEqual(counter.queue_length(), 3)
        self.assertTrue(counter.is_free())

        # Step 1: Assign staff to c1 and c2
        counter.step(current_time=1)
        self.assertEqual(counter.queue_length(), 1)  # c3 remains in queue
        self.assertFalse(counter.is_free())  # 2 staff both busy

        # Step 2: c1 finishes (was 2.0 min)
        completed = counter.step(current_time=2)
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0].customer_id, 1)

    def test_counter_utilisation(self):
        counter = Counter(name="Beverages", staff_count=1)
        c1 = Customer(1, arrival_time=0)
        c1._prep = 20.0
        counter.add_to_queue(c1)
        counter.assign_next_customer(0, base_service_duration=20.0)

        for t in range(1, 21):
            counter.tick(t)

        util = counter.utilisation(total_minutes=100)
        self.assertAlmostEqual(util, 20.0, places=1)


class TestConfigAndMenuLoader(unittest.TestCase):
    """Tests for JSON config and CSV menu loader functions."""

    def test_load_config_valid(self):
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "canteen_config.json")
        cfg = load_config(config_path)
        self.assertIn("counters", cfg)
        self.assertIn("arrival_rates", cfg)
        self.assertGreaterEqual(len(cfg["counters"]), 1)

    def test_load_config_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            load_config("non_existent_config.json")

    def test_validate_config_missing_section(self):
        invalid_cfg = {"canteen_name": "Test"}
        with self.assertRaises(ValueError):
            validate_config(invalid_cfg)

    def test_load_menu(self):
        menu_path = os.path.join(os.path.dirname(__file__), "..", "data", "menu.csv")
        items = load_menu(menu_path)
        self.assertGreaterEqual(len(items), 15)

        for it in items:
            self.assertIsInstance(it, MenuItem)
            self.assertGreater(it.price, 0)
            self.assertGreater(it.prep_time, 0)
            self.assertGreater(it.popularity_weight, 0)

        combos = [it for it in items if it.is_combo]
        self.assertGreaterEqual(len(combos), 1)


class TestVisualizations(unittest.TestCase):
    """Tests that all plot functions accept DataFrame and return Matplotlib Figure."""

    @classmethod
    def setUpClass(cls):
        data = [
            {"customer_id": 1, "arrival_time": 10, "counter": "Snacks", "items": "Vada Pav",
             "queue_length_on_arrival": 2, "service_start": 12.0, "departure": 14.0,
             "wait_time": 2.0, "service_time": 2.0, "order_value": 15.0, "balked": False},
            {"customer_id": 2, "arrival_time": 20, "counter": "Beverages", "items": "Cutting Chai",
             "queue_length_on_arrival": 1, "service_start": 21.0, "departure": 22.0,
             "wait_time": 1.0, "service_time": 1.0, "order_value": 10.0, "balked": False},
            {"customer_id": 3, "arrival_time": 160, "counter": "Thali", "items": "Veg Mini Thali",
             "queue_length_on_arrival": 14, "service_start": float("nan"), "departure": float("nan"),
             "wait_time": float("nan"), "service_time": 0.0, "order_value": 60.0, "balked": True},
            {"customer_id": 4, "arrival_time": 170, "counter": "Snacks", "items": "Samosa Pav",
             "queue_length_on_arrival": 8, "service_start": 178.0, "departure": 180.0,
             "wait_time": 8.0, "service_time": 2.0, "order_value": 18.0, "balked": False},
        ]
        cls.df = pd.DataFrame(data)

    def test_plot_wait_by_hour(self):
        fig = plot_wait_by_hour(self.df)
        self.assertIsInstance(fig, Figure)

    def test_plot_queue_lengths(self):
        fig = plot_queue_lengths(self.df)
        self.assertIsInstance(fig, Figure)

    def test_plot_utilisation(self):
        fig = plot_utilisation(self.df)
        self.assertIsInstance(fig, Figure)

    def test_plot_wait_histogram(self):
        fig = plot_wait_histogram(self.df)
        self.assertIsInstance(fig, Figure)

    def test_plot_scenario_comparison(self):
        comp_df = pd.DataFrame([
            {"scenario": "Current Setup", "avg_wait": 6.8, "balking_rate": 14.2},
            {"scenario": "Add One Counter", "avg_wait": 3.9, "balking_rate": 5.1},
            {"scenario": "Faster Billing", "avg_wait": 4.5, "balking_rate": 7.3},
        ])
        fig = plot_scenario_comparison(comp_df)
        self.assertIsInstance(fig, Figure)

    def test_plot_dashboard(self):
        fig = plot_dashboard(self.df)
        self.assertIsInstance(fig, Figure)


if __name__ == "__main__":
    unittest.main()
