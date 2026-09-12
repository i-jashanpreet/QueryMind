"""
seed.py — Populate the querymind database with realistic e-commerce data.

Usage (from backend/ directory):
    python -m scripts.seed

Idempotent: will skip seeding if users already exist.
"""

import sys
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal

# Allow running as `python -m scripts.seed` from the backend/ directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.database.connection import engine, SessionLocal
from app.database.models import (
    Base, User, Category, Product, Order, OrderItem, Payment, Review
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def utc(year: int, month: int, day: int, hour: int = 12, minute: int = 0) -> datetime:
    return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Raw seed data
# ---------------------------------------------------------------------------

USERS = [
    ("Arjun Sharma",      "arjun.sharma@example.com"),
    ("Priya Mehta",       "priya.mehta@example.com"),
    ("Rohit Verma",       "rohit.verma@example.com"),
    ("Sneha Nair",        "sneha.nair@example.com"),
    ("Vikram Singh",      "vikram.singh@example.com"),
    ("Ananya Iyer",       "ananya.iyer@example.com"),
    ("Rajesh Kumar",      "rajesh.kumar@example.com"),
    ("Pooja Reddy",       "pooja.reddy@example.com"),
    ("Karan Malhotra",    "karan.malhotra@example.com"),
    ("Meena Pillai",      "meena.pillai@example.com"),
    ("Aditya Gupta",      "aditya.gupta@example.com"),
    ("Divya Bansal",      "divya.bansal@example.com"),
    ("Suresh Rao",        "suresh.rao@example.com"),
    ("Lakshmi Bhat",      "lakshmi.bhat@example.com"),
    ("Mohit Joshi",       "mohit.joshi@example.com"),
    ("Kavita Desai",      "kavita.desai@example.com"),
    ("Rahul Pandey",      "rahul.pandey@example.com"),
    ("Sunita Agarwal",    "sunita.agarwal@example.com"),
    ("Deepak Sinha",      "deepak.sinha@example.com"),
    ("Nisha Kaur",        "nisha.kaur@example.com"),
    ("Amit Trivedi",      "amit.trivedi@example.com"),
    ("Riya Ghosh",        "riya.ghosh@example.com"),
]

CATEGORIES = [
    "Electronics",
    "Clothing",
    "Home & Kitchen",
    "Books",
    "Sports & Fitness",
]

# (name, category_name, price, stock)
PRODUCTS = [
    # Electronics
    ("Samsung 65\" 4K Smart TV",         "Electronics",     62999, 18),
    ("Apple iPhone 15",                   "Electronics",    79999, 45),
    ("Sony WH-1000XM5 Headphones",       "Electronics",    29999, 60),
    ("Logitech MX Master 3 Mouse",        "Electronics",     8499, 120),
    ("Dell 27\" Monitor",                 "Electronics",    22999, 30),
    ("JBL Charge 5 Bluetooth Speaker",   "Electronics",     9999, 75),
    ("Realme Buds Air 5 Pro",            "Electronics",     3999, 200),
    ("Canon EOS R50 Camera",             "Electronics",    65000, 12),
    ("Lenovo IdeaPad Slim 5 Laptop",     "Electronics",    55999, 20),
    ("Amazon Echo Dot (5th Gen)",         "Electronics",     4999, 150),
    # Clothing
    ("Levi's 511 Slim Jeans",            "Clothing",         3599,  80),
    ("Nike Dri-FIT Running T-Shirt",     "Clothing",         1999, 150),
    ("Puma Women's Sports Bra",          "Clothing",         1299, 100),
    ("Allen Solly Formal Shirt",         "Clothing",         1799,  90),
    ("H&M Oversized Hoodie",             "Clothing",         2499,  60),
    ("Jockey Cotton Briefs (Pack of 3)", "Clothing",          799, 200),
    ("W Ethnic Kurta Set",               "Clothing",         2999,  70),
    ("Woodland Casual Sneakers",         "Clothing",         3999,  55),
    # Home & Kitchen
    ("Instant Pot Duo 7-in-1",           "Home & Kitchen",  9999,  35),
    ("Philips Air Fryer HD9200",         "Home & Kitchen",  6799,  50),
    ("Milton Thermosteel Flask 1L",      "Home & Kitchen",   899, 300),
    ("Prestige Induction Cooktop",       "Home & Kitchen",  2999,  45),
    ("Cello Plastic Storage Container",  "Home & Kitchen",   499, 400),
    ("Bombay Dyeing Bed Sheet Set",      "Home & Kitchen",  1699, 120),
    ("Pigeon Non-Stick Kadai",           "Home & Kitchen",  1299,  85),
    # Books
    ("Atomic Habits — James Clear",      "Books",             499, 500),
    ("The Psychology of Money",          "Books",             399, 450),
    ("Rich Dad Poor Dad",                "Books",             299, 600),
    ("Ikigai",                           "Books",             349, 380),
    ("The Alchemist — Paulo Coelho",     "Books",             249, 700),
    ("Deep Work — Cal Newport",          "Books",             449, 300),
    # Sports & Fitness
    ("Cosco Football Size 5",            "Sports & Fitness",  799, 100),
    ("Yonex Badminton Racket",           "Sports & Fitness", 1499,  60),
    ("Boldfit Yoga Mat 6mm",             "Sports & Fitness",  599, 200),
    ("Decathlon Gym Gloves",             "Sports & Fitness",  399, 250),
    ("Vector X Cricket Bat",             "Sports & Fitness", 1999,  40),
]

ORDER_STATUSES = ["pending", "processing", "shipped", "delivered", "cancelled"]
PAYMENT_METHODS = ["Credit Card", "Debit Card", "UPI", "Net Banking"]
PAYMENT_STATUSES = ["paid", "pending", "failed"]

REVIEW_TEXTS = [
    "Absolutely love this product! Great value for money.",
    "Good quality. Delivery was quick and packaging was secure.",
    "Decent product but could be better. Does the job.",
    "Amazing! Exactly as described. Will buy again.",
    "Not worth the price. Quality is below expectations.",
    "Outstanding quality. Highly recommend to everyone.",
    "Okay product. Nothing special, but it works.",
    "Fantastic build quality and great after-sales support.",
    "Received a defective unit initially but got a replacement quickly.",
    "Very happy with the purchase. My family loves it.",
    "Looks premium and works flawlessly. Five stars!",
    "Average product. Might consider alternatives next time.",
    "The product is sturdy and well-made. Satisfied.",
    "Shipping was fast and the item was well-packed.",
    "Great price for this quality. Highly satisfied.",
]


# ---------------------------------------------------------------------------
# Seeding logic
# ---------------------------------------------------------------------------

def seed() -> None:
    db = SessionLocal()

    try:
        # --- Idempotency check ---
        if db.query(User).count() > 0:
            print("Seed data already exists. Skipping.")
            return

        print("Creating tables...")
        Base.metadata.create_all(bind=engine)

        # --- Users ---
        print(f"Inserting {len(USERS)} users...")
        user_objs: list[User] = []
        for i, (name, email) in enumerate(USERS):
            created = utc(2023, 1, 1) + timedelta(days=i * 14)
            user_objs.append(User(name=name, email=email, created_at=created))
        db.add_all(user_objs)
        db.flush()

        # --- Categories ---
        print(f"Inserting {len(CATEGORIES)} categories...")
        cat_map: dict[str, Category] = {}
        for cat_name in CATEGORIES:
            c = Category(name=cat_name)
            db.add(c)
            cat_map[cat_name] = c
        db.flush()

        # --- Products ---
        print(f"Inserting {len(PRODUCTS)} products...")
        product_objs: list[Product] = []
        for i, (pname, cat_name, price, stock) in enumerate(PRODUCTS):
            created = utc(2023, 2, 1) + timedelta(days=i * 5)
            p = Product(
                name=pname,
                category_id=cat_map[cat_name].id,
                price=Decimal(str(price)),
                stock_quantity=stock,
                created_at=created,
            )
            product_objs.append(p)
        db.add_all(product_objs)
        db.flush()

        # --- Orders, OrderItems, Payments ---
        # Build 55 orders spread across all users with varied statuses and dates.
        print("Inserting orders, order items, and payments...")
        order_count = 0

        order_configs = [
            # (user_idx, status, date_offset_days, product_indices, quantities, payment_method, payment_status)
            (0,  "delivered",   10, [1, 6],       [1, 2],  "Credit Card",  "paid"),
            (1,  "shipped",     20, [10, 11],      [2, 1],  "UPI",          "paid"),
            (2,  "delivered",   30, [18, 25],      [1, 3],  "Debit Card",   "paid"),
            (3,  "processing",  40, [0, 9],        [1, 1],  "Net Banking",  "pending"),
            (4,  "delivered",   50, [26, 27, 28],  [2, 1, 1], "UPI",        "paid"),
            (5,  "cancelled",   60, [31],           [1],     "Credit Card",  "failed"),
            (6,  "delivered",   70, [7, 8],        [1, 1],  "Credit Card",  "paid"),
            (7,  "shipped",     80, [16, 17],      [1, 2],  "UPI",          "paid"),
            (8,  "delivered",   90, [19, 20, 21],  [1, 2, 1], "Debit Card", "paid"),
            (9,  "pending",    100, [33],           [3],     "UPI",          "pending"),
            (10, "delivered",  110, [2, 3, 4],     [1, 1, 1], "Net Banking","paid"),
            (11, "processing", 120, [12, 13],      [2, 1],  "Credit Card",  "pending"),
            (12, "delivered",  130, [29, 30],      [1, 2],  "UPI",          "paid"),
            (13, "shipped",    140, [5, 6],        [1, 1],  "Credit Card",  "paid"),
            (14, "delivered",  150, [24, 25, 26],  [1, 1, 3], "Debit Card", "paid"),
            (15, "cancelled",  160, [0],            [1],     "Net Banking",  "failed"),
            (16, "delivered",  170, [14, 15],      [1, 3],  "UPI",          "paid"),
            (17, "processing", 180, [8, 9],        [1, 1],  "Credit Card",  "pending"),
            (18, "delivered",  190, [22, 23],      [2, 1],  "UPI",          "paid"),
            (19, "shipped",    200, [34],           [2],     "Debit Card",   "paid"),
            (0,  "delivered",  210, [27, 28],      [2, 1],  "Credit Card",  "paid"),
            (1,  "delivered",  220, [1, 2],        [1, 1],  "UPI",          "paid"),
            (2,  "cancelled",  230, [5],            [1],     "Net Banking",  "failed"),
            (3,  "delivered",  240, [11, 12, 13],  [1, 1, 2], "Credit Card","paid"),
            (4,  "shipped",    250, [7],            [1],     "UPI",          "paid"),
            (5,  "delivered",  260, [20, 21],      [1, 1],  "Debit Card",   "paid"),
            (6,  "processing", 270, [32, 33],      [2, 1],  "Credit Card",  "pending"),
            (7,  "delivered",  280, [3, 4, 5],     [1, 2, 1], "UPI",        "paid"),
            (8,  "pending",    290, [16],           [1],     "Credit Card",  "pending"),
            (9,  "delivered",  300, [26, 29, 30],  [1, 1, 2], "Debit Card", "paid"),
            (10, "shipped",    310, [0, 6],        [1, 1],  "Net Banking",  "paid"),
            (11, "delivered",  320, [17, 18],      [1, 1],  "Credit Card",  "paid"),
            (12, "cancelled",  330, [9],            [2],     "UPI",          "failed"),
            (13, "delivered",  340, [24, 25],      [1, 1],  "Debit Card",   "paid"),
            (14, "processing", 350, [14, 15],      [2, 3],  "Credit Card",  "pending"),
            (15, "delivered",  360, [31, 34],      [1, 1],  "UPI",          "paid"),
            (16, "shipped",    370, [2, 8],        [1, 1],  "Debit Card",   "paid"),
            (17, "delivered",  380, [22, 23],      [2, 1],  "Net Banking",  "paid"),
            (18, "pending",    390, [10],           [1],     "UPI",          "pending"),
            (19, "delivered",  400, [1, 7],        [1, 1],  "Credit Card",  "paid"),
            (0,  "delivered",  410, [19, 20],      [1, 2],  "UPI",          "paid"),
            (1,  "shipped",    420, [28, 29],      [1, 1],  "Debit Card",   "paid"),
            (2,  "delivered",  430, [11, 13],      [2, 1],  "Credit Card",  "paid"),
            (3,  "cancelled",  440, [33],           [1],     "Net Banking",  "failed"),
            (4,  "delivered",  450, [4, 5, 6],     [1, 1, 2], "UPI",        "paid"),
            (5,  "processing", 460, [0, 1],        [1, 1],  "Credit Card",  "pending"),
            (6,  "delivered",  470, [30, 31],      [1, 2],  "Debit Card",   "paid"),
            (7,  "shipped",    480, [16, 17],      [2, 1],  "UPI",          "paid"),
            (8,  "delivered",  490, [26, 27],      [1, 1],  "Credit Card",  "paid"),
            (9,  "delivered",  500, [3, 8, 9],     [1, 1, 1], "Net Banking","paid"),
            (10, "pending",    510, [21],           [1],     "UPI",          "pending"),
            (11, "delivered",  520, [14, 15, 24],  [1, 2, 1], "Credit Card","paid"),
            (12, "shipped",    530, [6, 7],        [1, 1],  "Debit Card",   "paid"),
            (13, "delivered",  540, [32, 33, 34],  [2, 1, 1], "UPI",        "paid"),
            (14, "cancelled",  550, [2],            [1],     "Credit Card",  "failed"),
        ]

        base_order_date = utc(2023, 3, 1)
        for (
            user_idx, status, day_offset,
            prod_idxs, quantities,
            pay_method, pay_status
        ) in order_configs:
            order_date = base_order_date + timedelta(days=day_offset // 10, hours=day_offset % 10)

            # Calculate total
            total = Decimal("0")
            line_prices = []
            for pi, qty in zip(prod_idxs, quantities):
                unit = product_objs[pi].price
                line_prices.append(unit)
                total += unit * qty

            order = Order(
                user_id=user_objs[user_idx].id,
                order_date=order_date,
                status=status,
                total_amount=total,
            )
            db.add(order)
            db.flush()

            for pi, qty, unit in zip(prod_idxs, quantities, line_prices):
                db.add(OrderItem(
                    order_id=order.id,
                    product_id=product_objs[pi].id,
                    quantity=qty,
                    unit_price=unit,
                ))

            paid_at = order_date + timedelta(hours=1) if pay_status == "paid" else None
            db.add(Payment(
                order_id=order.id,
                payment_method=pay_method,
                payment_status=pay_status,
                paid_at=paid_at,
            ))
            order_count += 1

        db.flush()

        # --- Reviews ---
        print("Inserting reviews...")
        review_configs = [
            # (user_idx, product_idx, rating, text_idx)
            (0,  1,  5, 0),   (1,  10, 4, 1),  (2,  18, 4, 2),
            (3,  0,  3, 3),   (4,  26, 5, 4),   (5,  7,  2, 5),
            (6,  8,  5, 6),   (7,  16, 4, 7),   (8,  19, 4, 8),
            (9,  33, 5, 9),   (10, 2,  4, 10),  (11, 12, 3, 11),
            (12, 29, 5, 12),  (13, 5,  4, 13),  (14, 24, 5, 14),
            (15, 0,  2, 0),   (16, 14, 4, 1),   (17, 22, 3, 2),
            (18, 1,  5, 3),   (19, 34, 5, 4),   (0,  27, 4, 5),
            (1,  2,  3, 6),   (2,  11, 4, 7),   (3,  13, 5, 8),
            (4,  7,  5, 9),   (5,  20, 4, 10),  (6,  31, 3, 11),
            (7,  3,  4, 12),  (8,  16, 5, 13),  (9,  26, 5, 14),
            (10, 0,  4, 0),   (11, 14, 3, 1),
        ]

        for user_idx, prod_idx, rating, text_idx in review_configs:
            db.add(Review(
                user_id=user_objs[user_idx].id,
                product_id=product_objs[prod_idx].id,
                rating=rating,
                review_text=REVIEW_TEXTS[text_idx],
            ))

        db.commit()

        # --- Summary ---
        print("\n✅  Seed complete!")
        print(f"   Users:       {db.query(User).count()}")
        print(f"   Categories:  {db.query(Category).count()}")
        print(f"   Products:    {db.query(Product).count()}")
        print(f"   Orders:      {db.query(Order).count()}")
        print(f"   Order Items: {db.query(OrderItem).count()}")
        print(f"   Payments:    {db.query(Payment).count()}")
        print(f"   Reviews:     {db.query(Review).count()}")

    except Exception as exc:
        db.rollback()
        print(f"\n❌  Seed failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
