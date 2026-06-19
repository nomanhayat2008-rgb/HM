from sqlalchemy import *
from extention import db


class Cart(db.Model):
    __tablename__ = "carts"

    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.id"),
        nullable=False
    )

    medicine_id = db.Column(
        db.Integer,
        db.ForeignKey("medicine.id"),
        nullable=False
    )
    price = db.Column(db.Integer, nullable=False ,default=0)
    unit_price =  db.Column(db.Integer, nullable=False ,default=0)
    quantity = db.Column(db.Integer, nullable=False ,default=0)
    patient = db.relationship("Patient", backref="carts")
    medicine = db.relationship("Medicine", backref="carts")
