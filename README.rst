strongTNC
=========

.. image:: https://travis-ci.org/strongswan/strongTNC.png?branch=master
   :target: https://travis-ci.org/strongswan/strongTNC
   :alt: Build status

.. image:: https://coveralls.io/repos/github/strongswan/strongTNC/badge.svg?branch=master
   :target: https://coveralls.io/github/strongswan/strongTNC?branch=master
   :alt: Test coverage

.. image:: https://landscape.io/github/strongswan/strongTNC/master/landscape.png
   :target: https://landscape.io/github/strongswan/strongTNC/master
   :alt: Code Health

strongTNC is a Trusted Network Connect (TNC) extension for the strongSwan VPN
solution. It allows the definition and enforcement of TNC policies that apply
to all VPN clients and must be fulfilled with each connection attempt.


Development Setup
-----------------

strongTNC uses Django (currently version 1.8.x). It is recommended to use the
pip_ and virtualenv_ tools to ease the dependency management. They can be
installed via your package manager on most Linux distributions.

If you're new to these tools: Pip is the de-facto Python package manager
(similar to apt-get or yum). And virtualenv is a tool that allows you to have
multiple Python installations side-by-side, inside a directory. A quickstart
guide can be found `here
<https://blog.dbrgn.ch/2012/9/18/virtualenv-quickstart/>`__.

**Non-Python Dependencies**

You need to install the following packages in order to be able to build all the
needed Python dependencies:

- python headers (Debian: ``python-dev``)
- libxml (Debian: ``libxml2-dev``)
- libxslt (Debian: ``libxslt-dev``)

**Environment, Dependencies**

First, create a virtualenv::

    cd /path/to/strongTNC/
    virtualenv --no-site-packages VIRTUAL
    source VIRTUAL/bin/activate

Then install the dependencies::

    pip install -r requirements.txt

**Configuration**

Create a local `settings.ini` file::

    cp config/settings.sample.ini config/settings.ini
    $EDITOR config/settings.ini

If this is not a production setup, change the ``DEBUG`` setting in
``settings.ini`` from 0 to 1.

Create the databases::

    ./manage.py migrate --database meta
    ./manage.py migrate

Set the default passwords::

    ./manage.py setpassword

If you want to use the Django-Admin view (``/admin``), create a superuser account::

    ./manage.py createsuperuser --database meta

In case you want to change the password of a user::

    ./manage.py changepassword admin-user --database meta

**Development**

Now you can start the development server. ::

    ./manage.py runserver

The web interface should be available on ``http://localhost:8000/``.

**Debugging**

If you want to use the django debug toolbar, install it via pip::

    pip install django-debug-toolbar

Then start the server with the setting ``[debug] DEBUG_TOOLBAR = 1`` (in
``settings.ini``).

To print all executed SQL queries to stdout, start the server with the setting
``[debug] SQL_DEBUG = 1`` (in ``settings.ini``).


Testing
-------

Install pytest & dependencies::

    pip install -r requirements-tests.txt

Run the tests::

    ./runtests.py

Run a specific test file::

    ./runtests.py tests/<filename>

Run only tests matching a specific pattern::

    ./runtests.py -k <pattern>

Run only tests that failed the last time::

    ./runtests.py --lf

Run tests without coverage::

    ./runtests.py --no-cov

Setup a database with test data::

    $ ./manage.py shell
    >>> execfile('tests/create_test_db.py')


XMPP-Grid Publishing Interface
------------------------------

strongTNC can publish SWID tag and SWIMA event information in JSON format to an
XMPP-Grid by setting ``[xmpp] USE_XMPP = 1`` and configuring various parameters
(in ``settings.ini``). Here is an example configuration::

    [xmpp]
    USE_XMPP = 1
    jid: tnc@strongswan.org
    password: <password>
    pubsub_server: pubsub.strongswan.org
    cacert: /etc/swanctl/x509ca/strongswanCaCert.pem
    use_ipv6: 0
    node_events: sacm/events
    node_swidtags: sacm/swidtags
    rest_uri: https://tnc.strongswan.org


License
-------

::

    Copyright (C) 2013 Marco Tanner, Stefan Rohner
    Copyright (C) 2014 Christian Fässler, Danilo Bargen, Jonas Furrer
    HSR University of Applied Sciences Rapperswil

    This file is part of strongTNC.  strongTNC is free software: you can
    redistribute it and/or modify it under the terms of the GNU Affero General
    Public License as published by the Free Software Foundation, either version
    3 of the License, or (at your option) any later version.

    strongTNC is distributed in the hope that it will be useful, but WITHOUT ANY
    WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
    FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
    more details.

    You should have received a copy of the GNU Affero General Public License
    along with strongTNC.  If not, see <http://www.gnu.org/licenses/>.

TLDR: This project is distributed under the AGPLv3, see ``LICENSE`` file.


.. _pip: https://github.com/pypa/pip
.. _virtualenv: http://www.virtualenv.org/en/latest/
