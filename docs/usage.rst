=====
Usage
=====

___
Cli
___

Make sure you installed with the cli extra and then run aws-session-recorder.::

	$ pip install 'aws-session-recorder[cli]'
	$ aws-session-recorder --profile <profile_name> shell

This will drop you into an IPython shell with access to an already created IAM object with the name `iam`. A SQLite DB named `sqlite.db` will be created in the current directory by default.::

	$ aws-session-recorder --profile  <profile_name> shell
	Python 3.9.1 (default, Jan  8 2021, 17:17:43) 
	Type 'copyright', 'credits' or 'license' for more information
	IPython 7.20.0 -- An enhanced Interactive Python. Type '?' for help.

	In [1]: iam
	Out[1]: iam.ServiceResource()

	In [2]: list(iam.users.all())
	Out[2]: 
	[ iam.User(name='power-user'),
	 iam.User(name='test'),
	 iam.User(name='test_admin')]

	In [3]:                                                                                                                                           
	Do you really want to exit ([y]/n)? y

	$ datasette -o sqlite.db 

The last command will your browser to view the contents of the SQLiteDB. Anything that was enumerated in the session you'll be able to see here.

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
