from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.records.models import Record

records_bp = Blueprint('records', __name__)

@records_bp.route('/list')
@login_required
def list():
    srp = current_app.srp  # ← Obtén srp desde current_app
    records = list(srp.load_all(Record))
    user_records = [r for r in records if r.user_email == current_user.email]
    return render_template('records/list.html', records=user_records)

@records_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    srp = current_app.srp  # ← Obtén srp desde current_app
    
    if request.method == 'POST':
        record = Record(
            request.form['title'],
            request.form['artist'],
            int(request.form['year']),
            request.form['genre'],
            request.form['condition'],
            current_user.email
        )
        srp.save(record)
        flash('Disco añadido!', 'success')
        return redirect(url_for('records.list'))
    return render_template('records/add.html')