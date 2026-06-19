from sqlalchemy import *
from extention import db


class Payment(db.Model):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey('patient.id'), nullable=False)
    cart = db.relationship('Cart', backref='payments')
