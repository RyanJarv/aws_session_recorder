import typing

import IPython
import typer

import aws_session_recorder

app = typer.Typer(name='aws_session_recorder')

if typing.TYPE_CHECKING:
    from mypy_boto3_iam import service_resource as r

sess: aws_session_recorder.Session = aws_session_recorder.Session()


@app.callback()
def session(profile: str = typer.Option(None)):
    global sess
    sess = aws_session_recorder.Session(profile_name=profile)


@app.command()
def shell():
    # Import these for use in the shell
    from aws_session_recorder.lib import schema  # noqa: F401
    iam: 'r.IAMServiceResource' = sess.resource('iam')  # noqa: F841
    IPython.embed()
