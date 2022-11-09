import os
import secrets
from PIL import Image

from app import db
from app.main import bp
from app.models import Users, Source
from app.main.forms import EditProfileForm, TwitterAccountsForm
from app.parse import scrap

from flask import render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_required, current_user


@bp.route('/process', methods=['GET'])
def parser():
    tweeter_accounts = current_user.user_tweeter_accounts()
    parsed_tweets = scrap(tweeter_accounts)
    for i in parsed_tweets:
        return jsonify({'output': i['content']})


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    form = TwitterAccountsForm()
    if form.validate_on_submit():
        source = Source(account=form.accounts.data, author=current_user)
        db.session.add(source)
        db.session.commit()
        flash('Accs been saved')
        return redirect(url_for('main.index'))
    tweeter_accounts = current_user.user_tweeter_accounts()
    return render_template(
        'index.html', title='Home page', form=form, tweeter_accounts=tweeter_accounts)


@bp.route('/user/<username>')
@login_required
def user_page(username):
    form = EditProfileForm()
    user = Users.query.filter_by(username=username).first_or_404()
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


