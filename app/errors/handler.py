from flask import render_template
from app.errors import bp
from app import db


@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html', title='Oops..'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html', title='Oops..'), 500


@bp.app_errorhandler(401)
def unauthorized(error):
    return render_template('errors/401.html', title='Unauthorized'), 401
