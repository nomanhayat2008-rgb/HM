from flask import Blueprint, session, abort, request, redirect, render_template, url_for, Flask, flash
from extention import db, socketio
import config
from model.patient import Patient
from jdatetime import datetime
import os
from config import parse_int
app = Blueprint("doctor", __name__)


@app.before_request
def before_request():
    print()
    if session.get("doctor_login", None) is None and request.endpoint != 'doctor.doctor_login':
        flash('please login ', 'error')
        abort(403)


@app.route('/doctor/login', methods=["POST", "GET"])
def doctor_login():  # put application's code here
    if request.method == "POST":
        password = request.form.get('password', None)

        if password == config.doctor_pass:
            session["doctor_login"] = password
            flash('ورد موفق', 'success')
            return redirect("/doctor/page")
        else:
            flash('ورد ناموفق', 'error')
            return redirect("/doctor/login")
    else:
        return render_template('doctor/login.html')


@app.route("/doctor/page", methods=["POST", "GET"])
def Doctor_page():
    search = request.args.get('search', None)
    search_by = request.args.get('search_by', None)
    patients = Patient.query
    if search != None and search_by == 'Name':
        patients = patients.filter(Patient.username.like(f'%{search}%'))
    elif search != None and search_by == 'date':
        patients = patients.filter(Patient.date.like(f'%{search}%'))
    elif search != None and search_by == 'id':
        patients = patients.filter(Patient.id.like(f'%{search}%'))
    elif search != None and search_by == 'address':
        patients = patients.filter(Patient.address.like(f'%{search}%'))

    patients = patients.all()

    if request.method == "GET":
        return render_template('doctor/page.html', patients=patients, search=search)
    else:
        return "post"


@app.route('/doctor/page-edit/<id>', methods=['POST', 'GET'])
def page_edit(id):
    patient = Patient.query.filter(Patient.id == id).first_or_404()
    STATIC_UPLOADS = os.path.join("static", "uploads")
    os.makedirs(STATIC_UPLOADS, exist_ok=True)

    if request.method == "GET":
        return render_template('doctor/page-edit.html', patient=patient)

    else:
        username = parse_int(request.form.get('username', None))
        fathername = parse_int(request.form.get('fathername', None))
        gender = parse_int(request.form.get('gender', None))
        fee = parse_int(request.form.get('fee', None))
        address = parse_int(request.form.get('address', None))
        number = parse_int(request.form.get('number', None))
        p_number = parse_int(request.form.get('p_number', None))
        u_s = parse_int(request.form.get('u_s', None))
        neb = parse_int(request.form.get('neb', None))
        m_f = parse_int(request.form.get('m_f', None))
        iv_c = parse_int(request.form.get('iv_c', None))
        im = parse_int(request.form.get('im', None))
        file = request.files.get('prescription', None)
        db_type = parse_int(request.form.get('db_type', None))
        # ذخیره تغییرات معلومات مریض
        patient.username = username
        patient.fathername = fathername
        patient.gender = gender
        patient.fee = fee
        patient.address = address
        patient.number = number
        patient.p_number = p_number
        patient.m_f = m_f
        patient.u_s =u_s
        patient.neb = 'yas' if neb else 'no'
        patient.iv_c =iv_c
        patient.im = 'yas' if im else 'no'
        patient.db_type = db_type
        db.session.commit()

        # فولدر مریض
        patient_folder = os.path.join(STATIC_UPLOADS, str(patient.id))
        os.makedirs(patient_folder, exist_ok=True)

        # --------------------------
        # ذخیره فایل فقط اگر فایل انتخاب شده باشد
        # --------------------------
        if file and file.filename.strip() != "":
            today = datetime.now().strftime("%Y-%m-%d")
            ext = os.path.splitext(file.filename)[1]

            # شمارش فایل‌های تاریخی امروز
            counter = len([f for f in os.listdir(patient_folder) if f.startswith(today)])
            filename = f"{today}_{counter}{ext}"

            save_path = os.path.join(patient_folder, filename)
            file.save(save_path)
        # --------------------------
        flash('دیتا موفقانه ایدیت شد', 'success')
        socketio.emit("reload_page", {"reload": True})
        return redirect(url_for("doctor.page_edit", id=id))


@app.route('/doctor/page-delete/<id>', methods=['POST', 'GET'])
def Page_delete(id):
    patient = Patient.query.filter(Patient.id == id).first_or_404()
    STATIC_UPLOADS = os.path.join("static", "uploads")
    os.makedirs(STATIC_UPLOADS, exist_ok=True)
    db.session.delete(patient)
    db.session.commit()
    flash('معلومات حذف شد', 'success')
    return redirect(url_for('doctor.Doctor_page', id=id))


@app.route('/doctor/pre', methods=['POST', 'GET'])
def Pre():
    return render_template('doctor/pre.html')
