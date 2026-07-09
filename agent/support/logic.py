from pathlib import Path
from sqlmodel import SQLModel, select, or_
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from .db import Account, Product, Order, Payment, SupportComplaint, SupportRequest

import json
from functools import reduce

DB_PATH = Path(__file__).resolve().parents[2] / "db.sqlite3"
sqlite_url = f"sqlite+aiosqlite:///{DB_PATH}"
engine = create_async_engine(sqlite_url)


async def create_db_and_tables():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


def _serialize_data(data):
    if data is None:
        return "None"
    if isinstance(data, str):
        return data
    if isinstance(data, (dict, list, int, float, bool)):
        return json.dumps(data, default=str)
    if hasattr(data, "model_dump"):
        return json.dumps(data.model_dump(), default=str)
    if hasattr(data, "json"):
        return data.json()
    return json.dumps(data, default=str)


async def create_product(data):
    await create_db_and_tables()
    async with AsyncSession(engine) as session:
        product = Product(**data)
        session.add(product)
        await session.commit()
        await session.refresh(product)

    return _serialize_data(product)


async def search_products(search_terms):
    await create_db_and_tables()
    terms = [term.strip() for term in str(search_terms).replace(", ", ",").split(",") if term.strip()]

    if not terms:
        return None
    
    async with AsyncSession(engine) as session:
        conditions = []
        for term in terms:
            pattern = f"%{term}%"
            conditions.append(Product.name.ilike(pattern))
            conditions.append(Product.description.ilike(pattern))

        statement = select(Product).where(or_(*conditions))
        result = await session.exec(statement)
        products = result.all()

    return _serialize_data(list(products))


async def get_product(product_id=None, name=None):
    await create_db_and_tables()

    async with AsyncSession(engine) as session:
        if product_id:
            product = await session.get(Product, product_id)
        else:
            product = None

        if not product and name:
            result = await session.exec(select(Product).where(Product.name.ilike(f"%{name}%")))
            product = result.first()

    return _serialize_data(product)


async def search_order(order_id=None, account=None):
    await create_db_and_tables()

    async with AsyncSession(engine) as session:
        statement = None
        if order_id:
            statement = select(Order).where(Order.id == order_id)
        elif account:
            statement = select(Order).where(Order.account == account)

        if statement is None:
            return None

        result = await session.exec(statement)
        orders = result.all()

    return _serialize_data(list(orders))


async def search_account(account_id=None, email=None, phone=None):
    await create_db_and_tables()

    async with AsyncSession(engine) as session:
        if account_id:
            account = await session.get(Account, account_id)
            return _serialize_data(account)

        conditions = []
        if email:
            conditions.append(Account.email.ilike(f"%{email}%"))
        if phone:
            conditions.append(Account.phone.ilike(f"%{phone}%"))

        if conditions:
            result = await session.exec(select(Account).where(or_(*conditions)))
            accounts = result.all()
            return _serialize_data(list(accounts))

    return "[]"


async def update_order(order_id=None, products=None):
    await create_db_and_tables()
    if not order_id:
        return "Please provide an order id"

    async with AsyncSession(engine) as session:
        order = await session.get(Order, order_id)
        if not order:
            return "None"

        update_data = {}

        if products:
            if isinstance(products, str):
                products = [item.strip() for item in products.split(",") if item.strip()]
            update_data["products"] = products

            products = await session.exec(select(Product).where(or_(*[Product.id == product for product in products])))
            products = products.all()[0]
            prices = list(map(lambda p: p.price, products))
            total_price = reduce(lambda x, y: x+y, prices)

            update_data['total_price'] = total_price
        

        if not update_data:
            return "No fields were provided to update"

        order.sqlmodel_update(update_data)
        session.add(order)
        await session.commit()
        await session.refresh(order)

    return _serialize_data(order)


async def cancel_order(order_id=None):
    await create_db_and_tables()
    if not order_id:
        return "Please provide an order id"

    async with AsyncSession(engine) as session:
        order = await session.get(Order, order_id)
        if not order:
            return "Order does not exist, it may be already cancelled."
        await session.delete(order)
        await session.commit()

    return f"Cancelled order {order_id}"


async def update_account(account_id=None, email=None, phone=None, password=None):
    await create_db_and_tables()
    if not account_id:
        return "Please provide an account id"

    async with AsyncSession(engine) as session:
        account = await session.get(Account, account_id)
        if not account:
            return "Account not found"

        update_data = {}
        for field_name, field_value in (("email", email), ("phone", phone), ("password", password)):
            if field_value:
                update_data[field_name] = field_value

        if not update_data:
            return "No fields were provided to update"

        account.sqlmodel_update(update_data)
        session.add(account)
        await session.commit()
        await session.refresh(account)

    return _serialize_data(account)


async def reset_password(account_id=None, email=None, new_password=None):
    await create_db_and_tables()

    async with AsyncSession(engine) as session:
        if account_id:
            account = await session.get(Account, account_id)
        elif email:
            result = await session.exec(select(Account).where(Account.email.ilike(f"%{email}%")))
            account = result.first()
        else:
            account = None

        if not account:
            return "None"

        account.password = new_password
        session.add(account)
        await session.commit()
        await session.refresh(account)

    return {"status": "password_reset", "account_id": account.id}


async def delete_account(account_id=None):
    await create_db_and_tables()

    async with AsyncSession(engine) as session:
        if account_id:
            account = await session.get(Account, account_id)
        else:
            account = None

        if not account:
            return "Account not found"

        await session.delete(account)
        await session.commit()

    return f"Deleted account {account_id}"


async def create_payment(order_id=None, status='pending'):
    await create_db_and_tables()

    if not order_id:
        return "Please provide an order id"

    async with AsyncSession(engine) as session:
        payment = Payment(order=order_id, status=status)
        session.add(payment)
        await session.commit()
        await session.refresh(payment)

    return _serialize_data(payment)


async def refund_payment(payment_id=None, order_id=None):
    await create_db_and_tables()

    async with AsyncSession(engine) as session:
        if payment_id:
            payment = await session.get(Payment, payment_id)
        elif order_id:
            result = await session.exec(select(Payment).where(Payment.order == order_id))
            payment = result.first()
        else:
            payment = None

        if not payment:
            return "None"

        session.delete(payment)        
        await session.commit()

    return "Refunded payment"



async def create_complain(account=None, description=None):
    await create_db_and_tables()
    if not description:
        return "Please provide a complaint description"

    async with AsyncSession(engine) as session:
        complaint = SupportComplaint(account=account, description=description)
        session.add(complaint)
        await session.commit()
        await session.refresh(complaint)

    return _serialize_data(complaint)


async def create_request(account=None, description=None):
    await create_db_and_tables()
    if not description:
        return "Please provide a request description"

    async with AsyncSession(engine) as session:
        request = SupportRequest(account=account, description=description)
        session.add(request)
        await session.commit()
        await session.refresh(request)

    return _serialize_data(request)