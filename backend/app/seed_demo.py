"""Opt-in development data. Never runs at application startup or in production."""

import getpass
import os
from decimal import Decimal

from sqlalchemy import select

from app.core.config import Settings
from app.db.session import make_engine, make_sessions
from app.models import Address, Category, City, Driver, Merchant, Product, User
from app.schemas.auth import Register
from app.security.passwords import hash_password


def main():
    settings = Settings()
    if settings.environment == "production":
        raise SystemExit("Demo data is forbidden in production.")
    password = os.environ.get("DEMO_PASSWORD") or getpass.getpass(
        "Choose a demo password (12+ chars): "
    )
    Register(name="Demo account", email="demo@example.com", phone="01000000000", password=password)
    engine = make_engine(settings.database_url)
    try:
        with make_sessions(engine).begin() as db:
            emails = [
                "admin@example.com",
                "merchant@example.com",
                "driver@example.com",
                "customer@example.com",
                "driver2@example.com",
                "bakery@example.com",
            ]
            if db.scalar(select(User.id).where(User.email.in_(emails)).limit(1)):
                raise SystemExit(
                    "Demo account already exists; no existing accounts or data were changed."
                )
            users = []
            for index, (email, role, name) in enumerate(
                zip(
                    emails,
                    ["Admin", "Merchant", "Driver", "Customer", "Driver", "Merchant"],
                    [
                        "مدير وصلة",
                        "أحمد — سوق البلد",
                        "علي — التوصيل",
                        "حازم",
                        "محمد — التوصيل",
                        "مخبز الحارة",
                    ],
                    strict=True,
                )
            ):
                user = User(
                    name=name,
                    email=email,
                    phone=f"0100000010{index}",
                    role=role,
                    password_hash=hash_password(password),
                )
                db.add(user)
                users.append(user)
            db.flush()
            city = db.scalar(select(City).where(City.name == "أبو حماد"))
            if not city:
                city = City(name="أبو حماد")
                db.add(city)
                db.flush()
            db.add_all(
                [
                    Merchant(
                        id=users[1].id,
                        business_name="سوق البلد",
                        description="بقالة ومستلزمات البيت من قلب أبو حماد.",
                    ),
                    Merchant(
                        id=users[5].id,
                        business_name="مخبز الحارة",
                        description="مخبوزات طازة كل يوم.",
                    ),
                    Driver(id=users[2].id),
                    Driver(id=users[4].id),
                    Address(
                        customer_id=users[3].id,
                        title="المنزل",
                        street="شارع المحطة، بجوار السوق — عنوان تجريبي",
                        city_id=city.id,
                        latitude=Decimal("30.5385000"),
                        longitude=Decimal("31.6798000"),
                        is_default=True,
                    ),
                ]
            )
            db.flush()
            categories = [
                Category(merchant_id=users[1].id, name="مستلزمات البيت"),
                Category(merchant_id=users[5].id, name="مخبوزات"),
            ]
            db.add_all(categories)
            db.flush()
            items = [
                (0, "أرز مصري — كيلو", "حبّة كاملة، للطبخ اليومي.", "35.50"),
                (0, "زيت عباد الشمس — لتر", "اختيار مناسب لمطبخك.", "78.00"),
                (0, "سكر أبيض — كيلو", "عبوة كيلو لمستلزمات البيت.", "32.00"),
                (0, "شاي أسود — 250 جرام", "شاي بطعم غني لكل الأوقات.", "58.00"),
                (1, "عيش بلدي — 10 أرغفة", "طازة من الفرن كل صباح.", "20.00"),
                (1, "كرواسون بالجبنة", "مخبوز طازة بحشوة الجبنة.", "25.00"),
            ]
            for category_index, name, description, price in items:
                category = categories[category_index]
                db.add(
                    Product(
                        merchant_id=category.merchant_id,
                        category_id=category.id,
                        name=name,
                        description=description,
                        price=Decimal(price),
                        stock_quantity=100,
                    )
                )
        print(
            "Created development accounts, sample catalog and a customer address. No orders or driver locations were fabricated."
        )
        print("Accounts: " + ", ".join(emails))
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
