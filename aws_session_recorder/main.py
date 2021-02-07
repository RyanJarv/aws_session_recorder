import typing

import IPython
import sqlalchemy
import typer

from aws_session_recorder import lib, settings
from aws_session_recorder.lib.schema.base import Base

app = typer.Typer(name='aws_session_recorder')

if typing.TYPE_CHECKING:
    from mypy_boto3_iam import service_resource as r

sess: lib.Session = lib.Session()

@app.callback()
def session(profile: str = typer.Option(None)):
    global sess
    sess = lib.Session(profile_name=profile)

@app.command()
def setup():
    engine = sqlalchemy.create_engine(settings.DATABASE_CONNECTION_PATH, echo=False)
    Base.metadata.create_all(engine)

@app.command()
def shell():
    from aws_session_recorder.lib import schema
    r: 'r.IAMServiceResource' = sess.resource('iam')
    IPython.embed()
