=====
Usage
=====

___
cli
___

asr --profile <profile name>

This will drop you into an IPython shell with access to an already created IAM object with the name `iam`. A SQLite DB named `sqlite.db` will be created in the current directory by default.


_______
Library
_______

To use aws-session-recorder in a project::

    import aws_session_recorder
    sess: aws_session_recorder.Session = aws_session_recorder.Session()
    iam = sess.resource('iam')
    list(iam.users.all())


`aws_session_recorder.Session()` takes all the same arguments as `boto3.Session`.

Same as with the CLI sqlite DB is created in the current directory by default. This can be overridden by using the connection_string keyword when creating the Session object.

Web Console
___________

You can browse easily browse the sqlite.db using datasette. For example this will open the web console in your browser::

    datasette serve -o sqlite.db
