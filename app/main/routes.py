import os
import secrets
from PIL import Image

from app import db
from app.main import bp
from app.models import Users, Source, UsersRegex
from app.main.forms import EditProfileForm, TwitterAccountsForm, DeleteForm, RegexForm
from app.parse import scrap

from flask import render_template, url_for, flash, redirect, request, jsonify, abort, json
from flask_login import login_required, current_user


@bp.route('/process', methods=['GET'])
def parser():
    tweeter_accounts = current_user.user_tweeter_accounts_for_p()
    regs = current_user.user_regs()
    parsed_tweets = scrap(tweeter_accounts, regs)
    return jsonify({'output': parsed_tweets})


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = TwitterAccountsForm()
    if form.validate_on_submit():
        if not current_user.accounts.filter_by(account=form.accounts.data).first():
            source = Source(account=form.accounts.data, author=current_user)
            db.session.add(source)
            db.session.commit()
            flash('Accs been saved')
            return redirect(url_for('main.index'))
        else:
            flash('That Account Is Already There')
    form3 = RegexForm()
    if form3.validate_on_submit():
        if len(current_user.regs.all()) <= 9:
            regex = UsersRegex(regex=form3.regex.data, author=current_user)
            db.session.add(regex)
            db.session.commit()
            flash('Regex has been saved')
            return redirect(url_for('main.index'))
        else:
            flash('You cant add more than 10 keys')
    return render_template(
        'index.html', title='Home page', form=form, form3=form3)


@bp.route('/user/<username>')
@login_required
def user_page(username):
    form = EditProfileForm()
    user = Users.query.filter_by(username=username).first_or_404()
    if current_user.username != username:
        abort(401)
    image_file = url_for('static', filename='profile_files/profile_pics/' + user.image_file)
    return render_template('user_page.html', user=user, image=image_file, title=current_user.username, form=form)


def save_pic(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(os.getcwd(), 'app/static', 'profile_files', 'profile_pics', picture_fn)
    size = (300, 300)
    i = Image.open(form_picture)
    i.thumbnail(size)
    i.save(picture_path)
    return picture_fn


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_pic(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('main.user_page', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@bp.route('/delete_accounts', methods=['GET', 'POST'])
def delete():
    id = request.args.get('id')
    print(id)
    if current_user.accounts.filter_by(id=id).first():
        current_user.remove_tweeter_account(id)
        db.session.commit()
        flash('Account has been deleted!')
    tweeter_accounts = current_user.user_tweeter_accounts()
    return jsonify({'output': id})


@bp.route('/get_accounts', methods=['GET', 'POST'])
def get_accounts():
    result = current_user.user_tweeter_accounts()
    accounts_dict = [{'id': i.id, 'account': i.account} for i in result]
    print(accounts_dict)
    return json.dumps(accounts_dict)


@bp.route('/get_keys', methods=['GET', 'POST'])
def get_keys():
    result = current_user.user_regs()
    keys_dict = [{'id': i.id, 'regex': i.regex} for i in result]
    print(keys_dict)
    return json.dumps(keys_dict)


