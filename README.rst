strongTNC
=========

strongTNC is a Trusted Network Connect (TNC) extension for the strongSwan VPN
solution. It allows the definition and enforcement of TNC policies that apply
to all VPN clients and must be fulfilled with each connection attempt.


Development Setup
-----------------

strongTNC uses Django (currently version 1.6.x). It is recommended to use the
pip_ and virtualenv_ tools to ease the dependency management. They can be
installed via your package manager on most Linux distributions.

If you're new to these tools: Pip is the de-facto Python package manager
(similar to apt-get or yum). And virtualenv is a tool that allows you to have
multiple Python installations side-by-side, inside a directory. A quickstart
guide can be found `here
<https://blog.dbrgn.ch/2012/9/18/virtualenv-quickstart/>`__.

First, create a virtualenv::

    cd /path/to/strongTNC/
    virtualenv --no-site-packages VIRTUAL
    source VIRTUAL/bin/activate

Then install the dependencies::

    pip install -r requirements.txt

Now you can start the development server. ::

    ./manage.py runserver

The web interface should be available on ``http://localhost:8000/``. The
default password is ``password``.


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
