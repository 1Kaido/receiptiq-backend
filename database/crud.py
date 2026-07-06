#crud.py # 5:12PM 
from database.db import db
from database.models import (
    Receipt,
    ReceiptItem,
    Tax,
    CompanyRegistration
)
def value(field):
    return field.value if field else None
    
def save_receipt(data):
    receipt = Receipt(
        supplier_name=value(data.supplier_name),
        supplier_address=value(data.supplier_address),
        supplier_phone=value(data.supplier_phone_number),
        receipt_number=value(data.receipt_number),
        date=value(data.date),
        time=value(data.time),
        total_amount=value(data.total_amount),
        total_net=value(data.total_net),
        total_tax=value(data.total_tax),
        document_type=value(data.document_type),
        purchase_category=value(data.purchase_category),
        purchase_subcategory=value(data.purchase_subcategory),
        currency = value(data.locale.get_simple_field("currency")),
        country = value(data.locale.get_simple_field("country")),
        language = value(data.locale.get_simple_field("language"))
        
    )
    db.session.add(receipt)
    db.session.flush()
    for item in data.line_items.items:
        receipt_item = ReceiptItem(
            receipt_id=receipt.id,
            description=value(item.get_simple_field("description")),
            quantity=value(item.get_simple_field("quantity")),
            unit_price=value(item.get_simple_field("unit_price")),
            total_price=value(item.get_simple_field("total_price")),
        )
        db.session.add(receipt_item)
    for tax in data.taxes.items:
        receipt_tax = Tax(
            receipt_id=receipt.id,
            rate=value(tax.get_simple_field("rate")),
            base=value(tax.get_simple_field("base")),
            amount=value(tax.get_simple_field("amount")),
        )
        db.session.add(receipt_tax)
        
    for reg in data.supplier_company_registration.items:
        company_registration = CompanyRegistration(
            receipt_id=receipt.id,
            registration_type=value(reg.get_simple_field("type")),
            registration_number=value(reg.get_simple_field("number")),
        )
        db.session.add(company_registration)
    db.session.commit()
    return receipt

import requests

def convert_to_inr(amount, currency):
    if amount is None:
        return 0

    if not currency:
        currency = "INR"   # your MVP default
    
    if currency == "INR":
        return amount
    
    url = f"https://api.frankfurter.dev/v1/latest?base={currency}&symbols=INR"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()

    if "rates" not in data or "INR" not in data["rates"]:
        raise ValueError(f"Cannot convert {currency} to INR")

    rate = data["rates"]["INR"]

    return round(amount * rate, 2)
    
def get_receipts():
    receipts = Receipt.query.all()

    data = []
    for receipt in receipts:
        data.append({
            "id": receipt.id,
            "supplier": receipt.supplier_name,
            "receipt_date": receipt.date,
            "created_at": receipt.created_at,
            "amount": convert_to_inr(receipt.total_amount,receipt.currency),
            "category": receipt.purchase_category,
            "currency": receipt.currency
            
        })

    return data

def get_detailed_receipts():

    receipts = Receipt.query.all()

    data = []

    for receipt in receipts:

        receipt_data = {

            "id": receipt.id,

            "supplier_name": receipt.supplier_name,
            "supplier_address": receipt.supplier_address,
            "supplier_phone": receipt.supplier_phone,

            "receipt_number": receipt.receipt_number,

            "date": receipt.date,
            "time": receipt.time,

            "total_amount": convert_to_inr(receipt.total_amount,receipt.currency),
            "total_net": convert_to_inr(receipt.total_net, receipt.currency),
            "total_tax": convert_to_inr(receipt.total_tax, receipt.currency),

            

            "document_type": receipt.document_type,
            "purchase_category": receipt.purchase_category,
            "purchase_subcategory": receipt.purchase_subcategory,

            "currency": receipt.currency,
            "country": receipt.country,
            "language": receipt.language,

            "items": [],
            "taxes": [],
            "company_registrations": []

        }

        # Receipt Items
        items = ReceiptItem.query.filter_by(
            receipt_id=receipt.id
        ).all()

        for item in items:

            receipt_data["items"].append({

                "description": item.description,
                "quantity": item.quantity,
                "unit_price":convert_to_inr(item.unit_price,receipt.currency), 
                "total_price":convert_to_inr(item.total_price,receipt.currency)

            })

        # Taxes
        taxes = Tax.query.filter_by(
            receipt_id=receipt.id
        ).all()

        for tax in taxes:

            receipt_data["taxes"].append({

                "rate": tax.rate,
                "base": convert_to_inr(tax.base,receipt.currency),
                "amount": convert_to_inr(tax.amount,receipt.currency),

            })

        # Company Registration
        registrations = CompanyRegistration.query.filter_by(
            receipt_id=receipt.id
        ).all()

        for reg in registrations:

            receipt_data["company_registrations"].append({

                "type": reg.registration_type,
                "number": reg.registration_number

            })

        data.append(receipt_data)

    return data

