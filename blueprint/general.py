from flask import Blueprint, render_template, jsonify
import os
from model.patient import Patient
from model.medicine import Medicine
from extention import db
from sqlalchemy import func

app = Blueprint("general", __name__)


@app.route("/patients_count")
def patients_count():
    count = Patient.query.count()
    return jsonify({'count': count})


@app.route('/chart')
def chart():
    result = db.session.query(
        Patient.date,
        func.count(Patient.id)
    ).group_by(Patient.date).order_by(Patient.date).all()

    labels = [r[0] for r in result]  # تاریخ‌ها
    counts = [r[1] for r in result]  # تعداد مریض هر روز

    return render_template(
        'chart.html',
        labels=labels,
        counts=counts
    )
    print(result)


@app.route('/')
def main():  # put application's code here
    return render_template('main.html')


@app.route('/patient<id>')
def patient_page(id):
    patient = Patient.query.filter(Patient.id == id).first_or_404()

    return render_template("patients/patient.html", patient=patient)
