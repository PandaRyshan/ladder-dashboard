import os

from flask import Flask, redirect,  url_for
from flask.cli import load_dotenv
from flask_login import login_required
from flask_wtf.csrf import CSRFProtect


def create_app(test_config=None):
    # shell env -> .env -> .flaskenv -> os.environ
    load_dotenv()

    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # csrf protection lazily
    csrf = CSRFProtect()
    csrf.init_app(app)

    from src import config
    if not test_config:
        # load the instance .env
        match os.environ['FLASK_ENV']:
            case 'prod':
                app.config.from_object(config.ProductionConfig)
            case 'test':
                app.config.from_object(config.TestingConfig)
            case 'dev':
                app.config.from_object(config.DevelopmentConfig)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # logging configuration
    from logger import LoggerConfigurator
    LoggerConfigurator.setup_app_logger(app)

    # register the database commands (sqlalchemy)
    from src.utils import db
    db.init_app(app)

    from src.views.auth import login_manager
    login_manager.init_app(app)

    # mail
    from src.utils import mail, celery
    mail.init_mail(app)
    celery.init_celery(app)

    @app.route("/index")
    @app.route("/", endpoint='index')
    @login_required
    def hello():
        return redirect(url_for("user.dashboard"))

    @app.route("/signup", methods=["GET"], endpoint="signup")
    def register():
        return redirect(url_for("auth.signup"))

    @app.route("/login", methods=["GET"], endpoint="login")
    def login():
        return redirect(url_for("auth.login"))

    from src.route_manager import RouteManager
    
    # register flask admin & blueprint
    RouteManager.register_admin(app)
    RouteManager.register_security(app, db.db)
    RouteManager.register_routes(app)

    return app
