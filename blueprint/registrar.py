import os
from flask import (
    Blueprint, render_template, request,
    session, redirect, abort, url_for, flash, jsonify
)
from sqlalchemy import func
from jdatetime import datetime
from extention import socketio
from extention import db, socketio
import config
from model.cart_m import Cart_m
from model.manzor_p import Manzor_p
from model.medicine import Medicine
from model.patient import Patient
from model.cart import Cart
from model.e_money import E_Money
from config import parse_int

app = Blueprint("registrar", __name__)


# =========================
# ACCESS CONTROL
# =========================
@app.before_request
def before_request():
    if (
            session.get("registrar_login") is None
            and request.endpoint not in (
            'registrar.registrar_login',
            'static'
    )
    ):
        abort(403)


# =========================
# LOGIN
# =========================
@app.route('/registrar/login', methods=["GET", "POST"])
def registrar_login():
    if request.method == "POST":
        password = request.form.get('password')
        if password == config.registrar_pass:
            session["registrar_login"] = password
            flash("ورد موفق", "success")
            return redirect(url_for("registrar.Registrar_page"))
        flash('ورد ناموفق', 'error')
        return redirect(url_for("registrar.registrar_login"))
    return render_template('registrar/login.html')


# =========================
# MAIN PAGE
# =========================
@app.route('/registrar/page', methods=['GET', 'POST'])
def Registrar_page():
    search = request.args.get('search')
    search_by = request.args.get('search_by')

    patients = Patient.query
    total_fee = 0
    u_s_total = 0
    iv_c = 0
    p_fee = 0
    type_1 = 0
    type_2 = 0
    type_3 = 0
    profit = 0
    p_profit = 0
    e =0
    e_total=0
    if search:
        if search_by == 'Name':
            patients = patients.filter(Patient.username.like(f'%{search}%'))
        elif search_by == 'date':
            patients = patients.filter(Patient.date.like(f'%{search}%'))
        elif search_by == 'id':
            patients = patients.filter(Patient.id.like(f'%{search}%'))
        elif search_by == 'address':
            patients = patients.filter(Patient.address.like(f'%{search}%'))
        elif search_by == 'type':
            if search == "D.Hedayatullah":
                search = 1
            elif search == "D.Enayt":
                search = 2
            elif search == "Nofee":
                search = 3
            patients = patients.filter(Patient.db_type.like(f'%{search}%'))

        a = db.session.query(func.sum(Patient.fee)) \
                .filter(Patient.date.like(f'%{search}%') if search_by == 'date' else True) \
                .scalar() or 0
        
        e = db.session.query(func.sum(E_Money.e_m)) \
                .filter(E_Money.date.like(f'%{search}%') if search_by == 'date' else True) \
                .scalar() or 0
        profit = db.session.query(func.sum(Patient.profit)) \
                     .filter(Patient.date.like(f'%{search}%') if search_by == 'date' else True) \
                     .scalar() or 0
        b = db.session.query(func.sum(Patient.m_f)) \
                .filter(Patient.date.like(f'%{search}%') if search_by == 'date' else True) \
                .scalar() or 0
        u = db.session.query(func.sum(Patient.u_s)).filter(Patient.u_s.isnot(None), Patient.date.like(
            f'%{search}%') if search_by == 'date' else True).scalar()
        iv_c = db.session.query(func.sum(Patient.iv_c)).filter(Patient.iv_c.isnot(None), Patient.date.like(
            f'%{search}%') if search_by == 'date' else True).scalar()
        p_fee = db.session.query(func.sum(Patient.p_fee)).filter(Patient.p_fee.isnot(None), Patient.date.like(
            f'%{search}%') if search_by == 'date' else True).scalar()

        type_1 = db.session.query(func.count(Patient.id)).filter(
            Patient.db_type == "1",
            Patient.date.like(f'%{search}%') if search_by == 'date' else True
        ).scalar()
        type_2 = db.session.query(func.count(Patient.id)).filter(
            Patient.db_type == "2",
            Patient.date.like(f'%{search}%') if search_by == 'date' else True
        ).scalar()
        type_3 = db.session.query(func.count(Patient.id)).filter(
            Patient.db_type == "3",
            Patient.date.like(f'%{search}%') if search_by == 'date' else True
        ).scalar()

        total_fee = a + b
        e_total =total_fee -e
        p_profit = a - profit
        u_s_total = u
    patients = patients.order_by(Patient.id.desc()).all()
    if request.method == "GET":
        return render_template(
            'registrar/page.html',
            patients=patients,
            search=search,
            total_fee=total_fee,
            u_s_total=u_s_total,
            iv_c=iv_c,
            p_fee=p_fee,
            type_1=type_1,
            type_2=type_2,
            type_3=type_3,
            profit=profit,
            p_profit=p_profit,
            e=e,
            e_total=e_total
        )

    # -------- POST (Add new patient) --------
    username = parse_int(request.form.get('username'))
    fathername = parse_int(request.form.get('fathername'))
    gender = parse_int(request.form.get('gender'))
    address = parse_int(request.form.get('address'))
    number = parse_int(request.form.get('number'))
    p_number = parse_int(request.form.get('p_number'))
    u_s = parse_int(request.form.get('u_s'))
    neb = parse_int(request.form.get('neb'))
    m_f = parse_int(request.form.get('m_f'))
    iv_c = parse_int(request.form.get('iv_c'))
    im = parse_int(request.form.get('im'))
    db_type = request.form.get('db_type')
    loan = parse_int(request.form.get('loan'))
    ePname = parse_int(request.form.get('ePname'))
    eFname = parse_int(request.form.get('eFname'))
    if not username or not fathername:
        flash("نام و نام پدر الزامی است", 'error')
        return redirect(request.url)
    H = "هدایت الله"
    E = "عنایت الله"
    NF = "بدون فیس"
    p = Patient(
        username=username,
        fathername=fathername,
        gender=gender,
        m_f=m_f,
        address=address,
        number=number,
        p_number=p_number,
        db_type=db_type,
        loan=loan,
        eFname=eFname,
        ePname=ePname
    )
    p.u_s = u_s
    p.neb = 'yas' if neb else 'no'
    p.iv_c = iv_c
    p.im = 'yas' if im else 'no'

    db.session.add(p)
    db.session.commit()

    flash('معلومات مریض موفقانه ثبت شد!', 'success')
    socketio.emit("reload_page", {"reload": True})
    return redirect(url_for("registrar.Registrar_page"))


# =========================
# EDIT PATIENT
# =========================
@app.route('/registrar/page-edit/<int:id>', methods=['GET', 'POST'])
def page_edit(id):
    patient = Patient.query.get_or_404(id)
    STATIC_UPLOADS = os.path.join("static", "uploads")
    os.makedirs(STATIC_UPLOADS, exist_ok=True)

    if request.method == "GET":
        return render_template('doctor/page-edit.html', patient=patient)

    username = parse_int(request.form.get('username'))
    fathername = parse_int(request.form.get('fathername'))
    gender = parse_int(request.form.get('gender'))
    address = parse_int(request.form.get('address'))
    number = parse_int(request.form.get('number'))
    p_number = parse_int(request.form.get('p_number'))
    u_s = parse_int(request.form.get('u_s'))
    neb = parse_int(request.form.get('neb'))
    m_f = parse_int(request.form.get('m_f'))
    iv_c = parse_int(request.form.get('iv_c'))
    im = parse_int(request.form.get('im'))
    db_type = request.form.get('db_type')
    loan = parse_int(request.form.get('loan'))
    ePname = parse_int(request.form.get('ePname'))
    eFname = parse_int(request.form.get('eFname'))
    patient.username = username
    patient.fathername = fathername
    patient.gender = gender
    patient.address = address
    patient.number = number
    patient.p_number = p_number
    patient.m_f = m_f
    patient.u_s = u_s
    patient.neb = 'yas' if neb else 'no'
    patient.iv_c = iv_c
    patient.im = 'yas' if im else 'no'
    patient.db_type = db_type
    if patient.loan != None:
        patient.fee += patient.loan
    patient.loan = loan
    if patient.loan == None:
        patient.loan = 0
    patient.fee -= patient.loan
    patient.ePname = ePname
    patient.eFname = eFname
    db.session.commit()


    flash('دیتا موفقانه ایدیت شد', 'success')
    socketio.emit("reload_page", {"reload": True})
    return redirect(url_for("registrar.Registrar_page"))


# =========================
# DELETE PATIENT
# =========================
@app.route('/registrar/page-delete/<int:id>', methods=['GET'])
def Page_delete(id):
    patient = Patient.query.get_or_404(id)
    carts = Cart.query.filter_by(patient_id=patient.id).all()
    for cart in carts:
        med = Medicine.query.get(cart.medicine_id)
        med.quantity += cart.quantity
        patient.fee -= cart.price
        db.session.delete(cart)
    cart_m = Cart_m.query.filter_by(manzor_p_id=id).all()

    for cart_m in cart_m:
        manzor_p = Manzor_p.query.get(cart_m.manzor_p_id)
        manzor_p.quantity += cart_m.quantity
        patient.p_fee -= cart_m.price
        db.session.delete(cart_m)
    db.session.delete(patient)
    db.session.commit()
    flash('معلومات حذف شد', 'success')
    return redirect(url_for('registrar.Registrar_page'))


# =========================
# CART ADD
# =========================
@app.route('/registrar/cart/add', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    patient_id = int(data['patient_id'])
    medicine_id = int(data['medicine_id'])
    quantity = int(data['quantity'])
    price = data.get('price')

    medicine = Medicine.query.get_or_404(medicine_id)
    patient = Patient.query.get_or_404(patient_id)

    if quantity > medicine.quantity:
        return jsonify({'status': 'error', 'message': 'موجودی کافی نیست'}), 400

    unit_price = int(price) if price else medicine.sell_p
    total_price = unit_price * quantity
    c_p = medicine.c_p * quantity
    cart = Cart(
        patient_id=patient_id,
        medicine_id=medicine_id,
        quantity=quantity,
        unit_price=unit_price,
        price=total_price
    )

    db.session.add(cart)
    medicine.quantity -= quantity
    if patient.fee is None:
        patient.fee = 0
    patient.fee += total_price
    patient.profit += c_p
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': 'به سبد خرید اضافه شد',
        'total_price': total_price,
        'unit_price': unit_price,
        'patient_fee': patient.fee
    })


# =========================
# CART SHOW
# =========================
@app.route('/cart/show/<int:patient_id>')
def cart_show(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    carts = (
        db.session.query(Cart, Medicine)
            .join(Medicine, Cart.medicine_id == Medicine.id)
            .filter(Cart.patient_id == patient_id)
            .all()
    )

    total_price = sum(c.price for c, _ in carts)

    return render_template(
        'cart/cart-show.html',
        patient=patient,
        carts=carts,
        total_price=total_price
    )


@app.route('/cart/update', methods=['POST'])
def cart_update():
    data = request.get_json()

    cart = Cart.query.get_or_404(data['cart_id'])
    new_qty = int(data['quantity'])

    if new_qty < 1:
        return {"status": "error", "message": "تعداد نامعتبر است"}, 400

    medicine = Medicine.query.get_or_404(cart.medicine_id)
    patient = Patient.query.get_or_404(cart.patient_id)

    diff = new_qty - cart.quantity

    # اگر افزایش تعداد باشد، موجودی بررسی شود
    if diff > 0 and diff > medicine.quantity:
        return {"status": "error", "message": "موجودی کافی نیست"}, 400

    unit_price = cart.unit_price
    total_diff_price = unit_price * diff

    # آپدیت موجودی دوا
    medicine.quantity -= diff
    print(diff)
    # آپدیت سبد
    cart.quantity = new_qty
    cart.price = unit_price * new_qty

    # آپدیت فیس مریض
    if patient.fee is None:
        patient.fee = 0
    patient.fee += total_diff_price

    db.session.commit()

    socketio.emit("reload_cart", {"message": "cart updated"})
    print(medicine.quantity)
    return {"status": "success"}


# =========================
# CART REMOVE
# ==========================
@app.route('/cart/remove/<int:cart_id>', methods=['POST'])
def cart_remove(cart_id):
    cart = Cart.query.get_or_404(cart_id)
    medicine = Medicine.query.get(cart.medicine_id)
    patient = Patient.query.get(cart.patient_id)

    medicine.quantity += cart.quantity
    patient.fee -= cart.price

    db.session.delete(cart)
    db.session.commit()
    return {"status": "success"}


# =========================
# CART CLEAR
# ==========================
@app.route('/cart/clear/<int:patient_id>', methods=['POST'])
def cart_clear(patient_id):
    carts = Cart.query.filter_by(patient_id=patient_id).all()
    patient = Patient.query.get_or_404(patient_id)

    for cart in carts:
        med = Medicine.query.get(cart.medicine_id)
        med.quantity += cart.quantity
        patient.fee -= cart.price
        db.session.delete(cart)

    db.session.commit()
    return {"status": "success"}


# =========================
# SHOW MEDICINE
# =========================
@app.route('/medicine/show/<int:patient_id>')
def medicine_show(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    search = request.args.get('search')
    search_by = request.args.get('search_by')
    medicine = Medicine.query
    if search:
        if search_by == 'Name':
            medicine = medicine.filter(Medicine.m_name.like(f'%{search}%'))
    medicines = medicine.order_by(Medicine.id.desc()).all()
    return render_template(
        'medicine/medicine-show.html',
        medicines=medicines,
        patient_id=patient.id
    )

#=================================
#==add_expend_money
#=================================
@app.route('/registrar/e_money', methods=['GET', 'POST'])
def e_money():
    search = request.args.get('search')
    search_by = request.args.get('search_by')
    e=0
    e_moneys = E_Money.query

    if search:
        if search_by == "name":
            condition = E_Money.e_r.like(f"%{search}%")
        else:
            condition = E_Money.date.like(f"%{search}%")

        e_moneys = e_moneys.filter(condition)

        e = db.session.query(func.sum(E_Money.e_m)).filter(condition).scalar() or 0
    else:
        e = db.session.query(func.sum(E_Money.e_m)).scalar() or 0

    e_moneys = e_moneys.order_by(E_Money.id.desc()).all()
    
    if request.method == "GET":
        return render_template(
            'registrar/e_money.html',e_moneys=e_moneys,e_total=e)
    e_m =parse_int(request.form.get('e_m'))
    e_r =parse_int(request.form.get('e_r'))
    if not e_m or not e_r:
        flash("دلیل مصرف و مقدار مصرف زروری است", 'error')
        return redirect(request.url)
    e =E_Money (e_m= e_m,
                e_r=e_r)
    db.session.add(e)
    db.session.commit()

    flash('معلومات موفقانه ثبت شد!', 'success')
    socketio.emit("reload_page", {"reload": True})
    return redirect(url_for("registrar.e_money"))
@app.route('/registrar/e_money-delete/<int:id>', methods=['GET'])
def e_money_delete(id):
    e_money = E_Money.query.get_or_404(id)

    db.session.delete(e_money)
    db.session.commit()
    flash('معلومات حذف شد', 'success')
    return redirect(url_for('registrar.e_money'))