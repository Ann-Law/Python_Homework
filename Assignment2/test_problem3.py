"""
Unit tests for Problem 3: Order

Instructions:
Complete the unit test methods below using Python's unittest framework.
Your test methods must assert MULTIPLE ATTRIBUTES on the Order object
(e.g., subtotal, discount_amount, tax_amount, shipping_fee, final_total, status)
to verify state consistency under various conditions.

Running tests:
    python -m unittest test_problem3.py -v
"""
import unittest
from problem3 import Order


class TestOrder(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.regular_order = Order("ORD100", customer_tier="regular")
        self.silver_order = Order("ORD200", customer_tier="silver")
        self.gold_order = Order("ORD300", customer_tier="gold")

    # TODO: develop 5 test methods for Order class
    def test_add_item_and_subtotal(self):
        """
        Test adding items, including same-item quantity accumulation,
        and verify subtotal, items dict, and summary.
        """
        # Add first item: Apple $10 x2
        self.regular_order.add_item("Apple", 10.0, quantity=2)
        self.assertEqual(self.regular_order.subtotal, 20.0)
        self.assertEqual(len(self.regular_order.items), 1)
        self.assertEqual(self.regular_order.items["Apple"]["quantity"], 2)

        # Add same item again: Apple $10 x3 → quantity becomes 5, subtotal = 50
        self.regular_order.add_item("Apple", 10.0, quantity=3)
        self.assertEqual(self.regular_order.subtotal, 50.0)
        self.assertEqual(self.regular_order.items["Apple"]["quantity"], 5)

        # Add second item
        self.regular_order.add_item("Banana", 5.0)
        self.assertEqual(self.regular_order.subtotal, 55.0)
        self.assertEqual(len(self.regular_order.items), 2)

        summary = self.regular_order.get_summary()
        self.assertEqual(summary["item_count"], 6)  # 5 apples + 1 banana
        self.assertEqual(summary["subtotal"], 55.0)
        self.assertEqual(summary["status"], "PENDING")

    def test_member_tier_discounts(self):
        """
        Test that regular/silver/gold tiers apply the correct discount rates.
        All orders add a $40 book (general category).
        """
        for order in (self.regular_order, self.silver_order, self.gold_order):
            order.add_item("Book", 40.0, quantity=1)

        # regular: no discount, net=40, shipping=5.99 (40<50), tax=40*0.08=3.20
        # final = 40 + 3.20 + 5.99 = 49.19
        self.assertEqual(self.regular_order.discount_amount, 0.0)
        self.assertEqual(self.regular_order.tax_amount, 3.20)
        self.assertEqual(self.regular_order.shipping_fee, 5.99)
        self.assertEqual(self.regular_order.final_total, 49.19)

        # silver: 5% discount = 2.00, net=38, shipping=5.99, tax=38*0.08=3.04
        # final = 38 + 3.04 + 5.99 = 47.03
        self.assertEqual(self.silver_order.discount_amount, 2.0)
        self.assertEqual(self.silver_order.tax_amount, 3.04)
        self.assertEqual(self.silver_order.shipping_fee, 5.99)
        self.assertEqual(self.silver_order.final_total, 47.03)

        # gold: 10% discount = 4.00, net=36, shipping=5.99, tax=36*0.08=2.88
        # final = 36 + 2.88 + 5.99 = 44.87
        self.assertEqual(self.gold_order.discount_amount, 4.0)
        self.assertEqual(self.gold_order.tax_amount, 2.88)
        self.assertEqual(self.gold_order.shipping_fee, 5.99)
        self.assertEqual(self.gold_order.final_total, 44.87)

    def test_coupon_discounts(self):
        """
        Test SAVE10 (10% off remaining) and FLAT15 ($15 off remaining) coupons.
        """
        # Start with a $100 laptop on regular tier
        self.regular_order.add_item("Laptop", 100.0, quantity=1)
        # No coupon: net=100, shipping=0 (>=50), tax=8.00, final=108.00
        self.assertEqual(self.regular_order.discount_amount, 0.0)
        self.assertEqual(self.regular_order.final_total, 108.00)

        # Apply SAVE10: coupon = 100 * 0.10 = 10, net=90, tax=90*0.08=7.20
        # final = 90 + 7.20 = 97.20
        self.regular_order.apply_coupon("SAVE10")
        self.assertEqual(self.regular_order.applied_coupon, "SAVE10")
        self.assertEqual(self.regular_order.discount_amount, 10.0)
        self.assertEqual(self.regular_order.tax_amount, 7.20)
        self.assertEqual(self.regular_order.final_total, 97.20)

        # Apply FLAT15: coupon = min(15, 100) = 15, net=85, tax=85*0.08=6.80
        # final = 85 + 6.80 = 91.80
        self.regular_order.apply_coupon("FLAT15")
        self.assertEqual(self.regular_order.applied_coupon, "FLAT15")
        self.assertEqual(self.regular_order.discount_amount, 15.0)
        self.assertEqual(self.regular_order.tax_amount, 6.80)
        self.assertEqual(self.regular_order.final_total, 91.80)

    def test_tax_exemption_and_free_shipping(self):
        """
        Test that grocery items are tax-exempt, and that net subtotal >= $50 gets free shipping.
        """
        # Grocery (Milk $10) + taxable (Pen $5), regular tier
        self.regular_order.add_item("Milk", 10.0, category="grocery")
        self.regular_order.add_item("Pen", 5.0, category="general")
        # subtotal=15, discount=0, net=15
        # tax only on Pen: 5 * 1.0 * 0.08 = 0.40
        # shipping: 15 < 50 → 5.99
        # final = 15 + 0.40 + 5.99 = 21.39
        self.assertEqual(self.regular_order.subtotal, 15.0)
        self.assertEqual(self.regular_order.tax_amount, 0.40)
        self.assertEqual(self.regular_order.shipping_fee, 5.99)
        self.assertEqual(self.regular_order.final_total, 21.39)

        # Free shipping threshold: add a $60 chair (regular tier, net=60 >= 50)
        self.silver_order.add_item("Chair", 60.0, category="furniture")
        # subtotal=60, silver discount=3.00, net=57 >= 50 → free shipping
        # tax = 57 * 0.08 = 4.56
        # final = 57 + 4.56 + 0 = 61.56
        self.assertEqual(self.silver_order.discount_amount, 3.0)
        self.assertEqual(self.silver_order.shipping_fee, 0.0)
        self.assertEqual(self.silver_order.tax_amount, 4.56)
        self.assertEqual(self.silver_order.final_total, 61.56)

    def test_order_status_transitions_and_exceptions(self):
        """
        Test PENDING → PAID / CANCELLED transitions and exception rules.
        """
        # Add an item, then checkout
        self.regular_order.add_item("Book", 20.0)
        self.assertTrue(self.regular_order.checkout())
        self.assertEqual(self.regular_order.status, "PAID")

        # Cannot modify a PAID order
        with self.assertRaises(RuntimeError):
            self.regular_order.add_item("Pen", 5.0)
        with self.assertRaises(RuntimeError):
            self.regular_order.apply_coupon("SAVE10")

        # Cannot checkout a PAID order again
        with self.assertRaises(RuntimeError):
            self.regular_order.checkout()

        # Cannot cancel a PAID order
        with self.assertRaises(RuntimeError):
            self.regular_order.cancel()

        # New order: cancel works
        self.silver_order.add_item("Pen", 5.0)
        self.assertTrue(self.silver_order.cancel())
        self.assertEqual(self.silver_order.status, "CANCELLED")

        # Cannot modify a CANCELLED order
        with self.assertRaises(RuntimeError):
            self.silver_order.add_item("Book", 10.0)

        # Checkout an empty order → ValueError
        empty_order = Order("ORD999", "regular")
        with self.assertRaises(ValueError):
            empty_order.checkout()

        # Invalid customer tier → ValueError
        with self.assertRaises(ValueError):
            Order("ORD000", "platinum")

        # Invalid coupon → ValueError
        self.gold_order.add_item("Book", 20.0)
        with self.assertRaises(ValueError):
            self.gold_order.apply_coupon("FAKECODE")




if __name__ == "__main__":
    unittest.main()
