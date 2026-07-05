from database.db import db

class Receipt(db.Model):
    __tablename__ = "receipts"
    id = db.Column(db.Integer, primary_key=True)
    supplier_name = db.Column(db.String(200))
    supplier_address = db.Column(db.String(300))
    supplier_phone = db.Column(db.String(20))  
    receipt_number = db.Column(db.String(100))  
    date = db.Column(db.String(50))  
    time = db.Column(db.String(50))
    total_amount = db.Column(db.Float)
    total_net = db.Column(db.Float)
    total_tax = db.Column(db.Float)
    document_type = db.Column(db.String(100))
    purchase_category = db.Column(db.String(100))
    purchase_subcategory = db.Column(db.String(100))
    currency = db.Column(db.String(10))
    country = db.Column(db.String(10))
    language = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships
    items = db.relationship("ReceiptItem", backref="receipt", lazy=True,cascade="all, delete-orphan")
    taxes = db.relationship("Tax", backref="receipt", lazy=True,cascade="all, delete-orphan")
    registrations = db.relationship("CompanyRegistration", backref="receipt", lazy=True,cascade="all ,delete-orphan")

class ReceiptItem(db.Model):
    __tablename__ = "receipt_items"
    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer,db.ForeignKey("receipts.id"),nullable=False)
    description = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Float)
    unit_price = db.Column(db.Float)
    total_price = db.Column(db.Float)

class Tax(db.Model):
    __tablename__ = "taxes"
    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer,db.ForeignKey("receipts.id"),nullable=False)
    rate = db.Column(db.Float)
    base = db.Column(db.Float)
    amount = db.Column(db.Float)
    
class CompanyRegistration(db.Model):
    __tablename__ = "company_registrations"
    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer,db.ForeignKey("receipts.id"),nullable=False)
    registration_type = db.Column(db.String(50))
    registration_number = db.Column(db.String(100))
