from sqlalchemy import *
from extention import db


class Cart_m(db.Model):
    __tablename__ = 'cart_ms'   # ✅ درست شد

    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey('patients.id'),
        nullable=False
    )

    manzor_p_id = db.Column(
        db.Integer,
        db.ForeignKey('manzor_p.id'),
        nullable=False
    )

    patient = db.relationship(
        'Patient',
        backref=db.backref('cart_ms', cascade='all, delete')
    )

    manzor_p = db.relationship(
        'Manzor_p',
        backref=db.backref('cart_ms', cascade='all, delete')
    )

    unit_price = db.Column(db.Integer, nullable=False, default=0)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Integer, nullable=False, default=0)