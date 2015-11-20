.. image:: https://travis-ci.org/reclosedev/lathermail_client.svg?branch=master
    :target: https://travis-ci.org/reclosedev/lathermail_client

.. image:: https://coveralls.io/repos/reclosedev/lathermail_client/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/reclosedev/lathermail_client?branch=master

lathermail_client
=================

Python API client for `lathermail <https://github.com/reclosedev/lathermail>`_ SMTP server.

Usage:

.. code-block:: python

    from lathermail_client import LathermailClient


    user, password = "user", "password"
    url = "http://127.0.0.0:5000/"

    client = LathermailClient(user, password, url)
    print(client.get_inboxes())
    print(client.get_messages(recipients_address="to@example.com"))
    print(client.get_single_message("some_id"))
