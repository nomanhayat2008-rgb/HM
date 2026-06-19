import os
from flask import Blueprint, render_template, request, flash, redirect, url_for
from extention import db, socketio
from model.medicine import Medicine
from model.cart import Cart

app = Blueprint('medicine', __name__)

IMG_PATH = os.path.join('static', 'img')
os.makedirs(IMG_PATH, exist_ok=True)


def safe_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


@app.route('/medicine/page', methods=['GET', 'POST'])
def Medicine_page():
    medicines = Medicine.query.all()

    if request.method == "GET":
        return render_template('medicine/medicine.html', medicine=medicines)

    # POST
    m_name = request.form.get('m_name', '')
    mc_name = request.form.get('mc_name', '')
    sell_p = safe_int(request.form.get('sell_p'))
    c_p = safe_int(request.form.get('c_p'))
    d_m = request.form.get('d_m', '')  # متن است، safe_int حذف شد
    quantity = safe_int(request.form.get('q'))
    file = request.files.get('file', None)

    m = Medicine(
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

    # Emit فقط به دستگاه‌های دیگر
    socketio.emit("new_medicine", {
        "id": m.id,
        "m_name": m.m_name,
        "mc_name": m.mc_name,
        "sell_p": m.sell_p,
        "c_p": m.c_p,
        "d_m": m.d_m,
        "quantity": m.quantity
    }, namespace='/', to=None)

    flash('معلومات موفقانه ثبت شد!', 'success')
    return redirect(url_for('medicine.Medicine_page'))


@app.route('/medicine/page-edit/<int:id>', methods=['GET', 'POST'])
def Page_edit(id):

    medicine = Medicine.query.get_or_404(id)

    if request.method == "GET":
        return render_template('medicine/edit.html', medicine=medicine)

    m_name = request.form.get('m_name', '')
    mc_name = request.form.get('mc_name', '')
    sell_p = safe_int(request.form.get('sell_p'))
    c_p = safe_int(request.form.get('c_p'))
    d_m = request.form.get('d_m', '')
    quantity = safe_int(request.form.get('q'))
    file = request.files.get('file', None)

    medicine.m_name = m_name
    medicine.mc_name = mc_name
    medicine.sell_p = sell_p
    medicine.c_p = c_p
    medicine.d_m = d_m
    medicine.quantity = quantity

    db.session.commit()

    if file:
        file.save(os.path.join(IMG_PATH, f'{medicine.id}.jpg'))

    socketio.emit("update_medicine", {
        "id": medicine.id,
        "m_name": medicine.m_name,
        "mc_name": medicine.mc_name,
        "sell_p": medicine.sell_p,
        "c_p": medicine.c_p,
        "d_m": medicine.d_m,
        "quantity": medicine.quantity
    }, namespace='/', to=None)

    flash('دیتا موفقانه ایدیت شد!', 'success')
    return redirect(url_for('medicine.Medicine_page'))


@app.route('/medicine/page-delete/<int:id>', methods=['POST', 'GET'])
def Page_delete(id):
    medicine = Medicine.query.get_or_404(id)

    carts = Cart.query.filter(Cart.medicine_id == id).all()
    for cart in carts:
        db.session.delete(cart)

    db.session.delete(medicine)
    db.session.commit()

    img_file = os.path.join(IMG_PATH, f'{id}.jpg')
    if os.path.exists(img_file):
        os.remove(img_file)

    socketio.emit("delete_medicine", {"id": id}, namespace='/', to=None)

    flash('معلومات حذف شد', 'success')
    return redirect(url_for('medicine.Medicine_page'))