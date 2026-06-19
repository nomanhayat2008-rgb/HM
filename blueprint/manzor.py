import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from extention import db, socketio
from model import patient
from model.manzor_p import Manzor_p
from model.cart_m import Cart_m as Cart, Cart_m
from model.medicine import Medicine
from model.patient import Patient
from config import parse_int

app = Blueprint('manzor', __name__)
# ===============================
# show medicines for patient
# ===============================
@app.route('/manzor_p/show/<int:patient_id>')
def manzor_p_show(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    manzor_p = Manzor_p.query.all()

    return render_template(
        'manzor/manzor_p_show.html',
        manzor_p=manzor_p,
        patient_id=patient.id
    )

# ===============================
# image path
# ===============================
IMG_PATH = os.path.join('static', 'mimg')
os.makedirs(IMG_PATH, exist_ok=True)

# ===============================
# add medicine
# ===============================
@app.route('/manzor_p/page', methods=['GET', 'POST'])
def Manzor_p_page():

    if request.method == "GET":
        manzor_p = Manzor_p.query.all()
        return render_template('manzor/manzor_p.html', manzor_p=manzor_p)

    # POST
    m_name = request.form.get('m_name')
    mc_name = request.form.get('mc_name')
    sell_p = parse_int(request.form.get('sell_p'))
    c_p = parse_int(request.form.get('c_p'))
    d_m = request.form.get('d_m')
    quantity = parse_int(request.form.get('q'))
    file = request.files.get('file')

    m = Manzor_p(
        m_name=m_name,
        mc_name=mc_name,
        sell_p=sell_p,
        c_p=c_p,
        d_m=d_m,
        quantity=quantity
    )

    db.session.add(m)
    db.session.commit()

    if file:
        file.save(os.path.join(IMG_PATH, f'{m.id}.jpg'))

    # Flash برای خود دستگاه
    flash('معلومات موفقانه ثبت شد!', 'success')

    # Emit فقط به سایر کلاینت‌ها
    socketio.emit("manzor_added", {
        "id": m.id,
        "m_name": m.m_name,
        "mc_name": m.mc_name,
        "sell_p": m.sell_p,
        "c_p": m.c_p,
        "d_m": m.d_m,
        "quantity": m.quantity,
        "date": m.date.strftime("%Y-%m-%d") if hasattr(m.date, 'strftime') else str(m.date)
    })

    return redirect(url_for('manzor.Manzor_p_page'))

# ===============================
# edit medicine
# ===============================
@app.route('/manzor_p/page-edit/<int:id>', methods=['GET', 'POST'])
def Manzor_p_Page_edit(id):
    manzor_p = Manzor_p.query.get_or_404(id)

    if request.method == "GET":
        return render_template('manzor/edit.html', manzor_p=manzor_p)

    manzor_p.m_name = request.form.get('m_name')
    manzor_p.mc_name = request.form.get('mc_name')
    manzor_p.sell_p = parse_int(request.form.get('sell_p'))
    manzor_p.c_p = parse_int(request.form.get('c_p'))
    manzor_p.d_m = request.form.get('d_m')
    manzor_p.quantity = parse_int(request.form.get('q'))

    file = request.files.get('file')

    db.session.commit()

    if file:
        file.save(os.path.join(IMG_PATH, f'{manzor_p.id}.jpg'))

    flash('دیتا موفقانه ایدیت شد!', 'success')
    socketio.emit("reload_page", {"reload": True})

    return redirect(url_for('manzor.Manzor_p_page'))

# ===============================
# delete medicine
# ===============================
@app.route("/manzor_p/page-delete/<int:id>", methods=['POST', 'GET'])
def Page_delete(id):
    manzor_p = Manzor_p.query.get_or_404(id)

    # حذف cart های مربوطه
    carts = Cart.query.filter_by(manzor_p_id=id).all()
    for cart in carts:
        patient = Patient.query.get(cart.patient_id)
        if patient and patient.p_fee:
            patient.p_fee -= cart.price
        db.session.delete(cart)

    db.session.delete(manzor_p)
    db.session.commit()

    img_file = os.path.join(IMG_PATH, f'{id}.jpg')
    if os.path.exists(img_file):
        os.remove(img_file)

    flash('معلومات حذف شد!', 'success')

    # اطلاع به سایر کلاینت‌ها
    socketio.emit("manzor_deleted", id)

    return redirect(url_for('manzor.Manzor_p_page'))

# =========================
# ADD TO CART
# =========================
@app.route('/cart/add', methods=['POST'])
def cart_add():

    data = request.get_json()

    patient_id = int(data['patient_id'])
    manzor_p_id = int(data['manzor_p_id'])
    quantity = int(data['quantity'])
    price = data.get('price')

    patient = Patient.query.get_or_404(patient_id)
    manzor_p = Manzor_p.query.get_or_404(manzor_p_id)

    if quantity < 1:
        return {"status": "error", "message": "تعداد نامعتبر است"}, 400

    if quantity > manzor_p.quantity:
        return {"status": "error", "message": "موجودی کافی نیست"}, 400

    unit_price = int(price) if price else manzor_p.sell_p
    total_price = unit_price * quantity

    cart = Cart(
        patient_id=patient_id,
        manzor_p_id=manzor_p_id,
        quantity=quantity,
        unit_price=unit_price,
        price=total_price
    )

    db.session.add(cart)

    manzor_p.quantity -= quantity

    if patient.p_fee is None:
        patient.p_fee = 0

    patient.p_fee += total_price

    db.session.commit()

    return {
        'status': 'success',
        'total_price': total_price,
        'unit_price': unit_price,
        'patient_fee': patient.p_fee
    }

# =========================
# CART SHOW
# =========================
@app.route('/cart_p/show/<int:patient_id>')
def cart_show(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    carts = (
        db.session.query(Cart, Manzor_p)
        .join(Manzor_p, Cart.manzor_p_id == Manzor_p.id)
        .filter(Cart.patient_id == patient_id)
        .all()
    )

    total_price = sum(c.price for c, _ in carts)

    return render_template(
        'cart/cart_p_show.html',
        patient=patient,
        carts=carts,
        total_price=total_price
    )

# =========================
# CART UPDATE
# =========================
@app.route('/cart_p/update', methods=['POST'])
def update_cart():

    data = request.get_json()

    cart = Cart.query.get_or_404(data['cart_id'])
    new_qty = int(data['quantity'])

    if new_qty < 1:
        return {"status": "error", "message": "تعداد نامعتبر است"}, 400

    manzor_p = Manzor_p.query.get_or_404(cart.manzor_p_id)
    patient = Patient.query.get_or_404(cart.patient_id)

    diff = new_qty - cart.quantity

    if diff > 0 and diff > manzor_p.quantity:
        return {"status": "error", "message": "موجودی کافی نیست"}, 400

    unit_price = cart.unit_price
    total_diff_price = unit_price * diff

    manzor_p.quantity -= diff

    cart.quantity = new_qty
    cart.price = unit_price * new_qty

    if patient.p_fee is None:
        patient.p_fee = 0

    patient.p_fee += total_diff_price

    db.session.commit()

    socketio.emit("reload_cart", {"message": "cart updated"})

    return {"status": "success"}

# =========================
# CART REMOVE
# =========================
@app.route('/cart_p/remove/<int:cart_id>', methods=['POST'])
def cart_remove(cart_id):

    cart = Cart.query.get_or_404(cart_id)

    manzor_p = Manzor_p.query.get_or_404(cart.manzor_p_id)
    patient = Patient.query.get_or_404(cart.patient_id)

    manzor_p.quantity += cart.quantity

    if patient.p_fee is None:
        patient.p_fee = 0

    patient.p_fee -= cart.price

    db.session.delete(cart)
    db.session.commit()

    return {"status": "success"}

# =========================
# CART CLEAR
# =========================
@app.route('/cart_p/clear/<int:patient_id>', methods=['POST'])
def cart_clear(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    cart_m = Cart_m.query.filter_by(patient_id=patient_id).all()

    for cart in cart_m:
        manzor_p = Manzor_p.query.get(cart.manzor_p_id)
        manzor_p.quantity += cart.quantity
        patient.p_fee -= cart.price
        db.session.delete(cart)

    db.session.commit()
    return {"status": "success"}