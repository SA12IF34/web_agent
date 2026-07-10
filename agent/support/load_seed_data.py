import json
from pathlib import Path

from sqlmodel import SQLModel, Session, create_engine

from .db import Account, Product, Order, Payment

from datetime import date
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR.parents[1] / "db.sqlite3"
SEED_DATA_PATH = BASE_DIR / "seed_data.json"
DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"


def load_seed_data():
    with SEED_DATA_PATH.open("r", encoding="utf-8") as fh:
        seed_data = json.load(fh)

    engine = create_engine(DATABASE_URL)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        for item in seed_data.get("accounts", []):
            account = session.get(Account, item["id"])
            if account is None:
                account = Account(**item)
                session.add(account)
            else:
                for key, value in item.items():
                    setattr(account, key, value)

        for item in seed_data.get("products", []):
            product = session.get(Product, item["id"])
            if product is None:
                product = Product(**item)
                session.add(product)
            else:
                for key, value in item.items():
                    setattr(product, key, value)

        for item in seed_data.get("orders", []):
            order = session.get(Order, item["id"])
            if order is None:
                date_str = item['deliver_at']
                item['deliver_at'] = date(
                    int(date_str.split('-')[0]), 
                    int(date_str.split('-')[1]),
                    int(date_str.split('-')[2])
                )
                order = Order(**item)
                session.add(order)
            else:
                for key, value in item.items():
                    setattr(order, key, value)

        for item in seed_data.get("payments", []):
            payment = session.get(Payment, item["id"])
            if payment is None:
                payment = Payment(**item)
                session.add(payment)
            else:
                for key, value in item.items():
                    setattr(payment, key, value)

        session.commit()

    print(f"Seed data loaded into {DB_PATH}")


