.. highlight:: shell

============
Installation
============


Stable release
--------------

To install aws-session-recorder, run this command in your terminal:

.. code-block:: console

    $ python3 -m venv venv
    $ . venv/bin/activate
    $ pip install aws_session_recorder

You can also optionally install the cli extras for easy testing.

.. code-block:: console

    $ pip install 'aws_session_recorder[cli]'

This is the preferred method to install aws-session-recorder, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for aws-session-recorder can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/RyanJarv/aws_session_recorder

Or download the `tarball`_:

.. code-block:: console

    $ curl -OJL https://github.com/RyanJarv/aws_session_recorder/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python install .


.. _Github repo: https://github.com/RyanJarv/aws_session_recorder
.. _tarball: https://github.com/RyanJarv/aws_session_recorder/tarball/master
