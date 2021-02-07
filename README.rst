====================
aws-session-recorder
====================


.. image:: https://img.shields.io/pypi/v/aws_session_recorder.svg
        :target: https://pypi.python.org/pypi/aws_session_recorder

.. image:: https://github.com/RyanJarv/aws_session_recorder/workflows/Python%20package/badge.svg
        :target: https://github.com/RyanJarv/aws_session_recorder/actions

.. image:: https://readthedocs.org/projects/aws-session-recorder/badge/?version=latest
        :target: https://aws-session-recorder.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




AWS session that records discovered resources to a database

NOTE: This project is still a work in progress.


* Free software: BSD license
* Documentation: https://aws-session-recorder.readthedocs.io.


Features
--------

* Works just like a normal boto3 session, so you can use it for any library that allows you to set the boto3 session..
* Records IAM related Get/List requests to a local sqlite.db.
* Use datasette to view recorded data.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
