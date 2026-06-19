from sqlalchemy import *
from extention import db


class Cart_item(db.Model):
    __tablename__ = "cart-items"
    id = Column(Integer, primary_key=True, index=True)
    medicine_id = Column(Integer, ForeignKey('medicine.id'), nullable=False)
    cart_id = Column(Integer, ForeignKey('cart.id'), nullable=False)
    medicine = db.relationship('Medicine', backref='cart-items')
    cart = db.relationship('Card', backref='cart-items')
