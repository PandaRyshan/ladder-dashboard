import click

from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext


db = SQLAlchemy()


def init_db(app):
    db.init_app(app)
    app.cli.add_command(init_db_command)

    @app.teardown_request
    def session_commit(exception=None):
        if exception:
            db.session.rollback()
        db.session.commit()


@click.command("init-db")
@click.option("--drop", is_flag=True, help="Create after drop.")
@with_appcontext
def init_db_command(drop):

    """Clear existing data and create new tables."""
    if drop:
        click.confirm("This operation will delete the database, do you want to continue?", abort=True)
        db.drop_all()
        click.echo("Droped all tables.")

    # if define models in submodules must import them so that
    # SQLAlchemy knows about them before calling create_all
    from src import models
    db.create_all()
    click.echo("Initialized the database.")

    if testdata:
        from src.models.role import Role
        role = Role(name="admin")
        db.session.add(role)
        role = Role(name="user")
        db.session.add(role)

        from src.models.verification_codes import VerificationCodes
        verification_code = VerificationCodes(
            code="123456", used=False, created_at=datetime.now(), expires_at=datetime.now() + timedelta(days=1))
        db.session.add(verification_code)
