from flask import render_template, url_for, flash, redirect, request
from parkingTickets import app, db, bcrypt
from parkingTickets.forms import LoginForm, SearchByDateForm, SearchByPlateForm, SearchBySummonsForm
from parkingTickets.models import User, Global_violations
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
import requests


@app.route("/")
def default():
    return redirect(url_for('login'))


@app.route("/home", methods=['GET', 'POST'])
def home():
    summons_form = SearchBySummonsForm()
    plate_form = SearchByPlateForm()
    date_form = SearchByDateForm()
    plate = None
    summons_num = None
    start_date = None
    end_date = None
    if date_form.validate_on_submit():
        pass

    print('Plate:', plate)
    print('summons:', summons_num)
    print('start:', start_date)
    print('end:', end_date)



    search_by = request.args.get('search_by', 'all', type=str)
    return render_template('home.html', title='search', summons_form=summons_form, plate_form=plate_form, date_form=date_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('home')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('search'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    items_per_page = 10
    boroughs = {1: "MANHATTAN", 2: "BRONX", 3: "BROOKLYN", 4: "QUEENS", 5: "STATEN ISLAND"}
    summons_form = SearchBySummonsForm()
    plate_form = SearchByPlateForm()
    date_form = SearchByDateForm()

    page = request.args.get('page', 1, type=int)
    if date_form.validate_on_submit():
        records = Global_violations.query.filter(Global_violations.issue_date >= date_form.start_date.data).filter(Global_violations.issue_date <= date_form.end_date.data).order_by(Global_violations.issue_date).paginate(page=1, per_page=items_per_page)
        return render_template('search.html', title='search', records=records, summons_form=summons_form, plate_form=plate_form, date_form=date_form, boroughs=boroughs)
    if summons_form.validate_on_submit():
        records = Global_violations.query.filter_by(summons_number=summons_form.summons_num.data).paginate(page=1, per_page=items_per_page)
        return render_template('search.html', title='search', records=records, summons_form=summons_form,
                               plate_form=plate_form, date_form=date_form, boroughs=boroughs)
    if plate_form.validate_on_submit():
        records = Global_violations.query.filter_by(plate=plate_form.plate.data).paginate(page=1, per_page=items_per_page)
        return render_template('search.html', title='search', records=records, summons_form=summons_form,
                               plate_form=plate_form, date_form=date_form, boroughs=boroughs)

    records = Global_violations.query.order_by(Global_violations.issue_date).paginate(page=page,
                                                                                      per_page=items_per_page)
    return render_template('search.html', title='search', records=records, summons_form=summons_form, plate_form=plate_form, date_form=date_form, boroughs=boroughs)


@app.route('/search/<summons_number>')
def summons(summons_number):
    boroughs = {1: "MANHATTAN", 2: "BRONX", 3: "BROOKLYN", 4: "QUEENS", 5: "STATEN ISLAND"}
    summons_info = Global_violations.query.filter_by(summons_number=summons_number).first()
    borough = boroughs[summons_info.county]
    print(summons_info.county)
    return render_template('summons.html', title='Summons', summons_info=summons_info, borough=borough)
