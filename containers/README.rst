
strongTNC Test Container
########################

Deployment Docs
===============

This VM is only for testing purposes. Please refer to
`Production Deployment document <../docs/deployment.rst>`_
for information on how to deploy strongTNC in a production environment.

Container Images for Test Purposes
==================================

This directory contains definition of container image which allows
starting containerized strongTNC test server within minutes.

On system with ``docker`` command available, running the container
ought to be a matter of building the container image and running the
container. The container image does not support persistence of the
data.

Requirements
------------

Docker engine / daemon and working ``docker`` command.

Building the image
------------------

In this directory, running

::

    $ sudo docker build -t strongtnc .

will fetch the master branch from strongTNC GitHub repo and build
the container image, tagging it as ``strongtnc``.

Running the container
---------------------

With

::

    $ sudo docker run --name strongtnc --rm -ti strongtnc

container named ``strongtnc`` will be created and started and the
command should print out something like

::

    Performing system checks...
    System check identified no issues (0 silenced).
    May 30, 2018 - 12:01:45
    Django version 1.8.19, using settings 'config.settings'
    Starting development server at http://0.0.0.0:8000/
    Quit the server with CONTROL-C.

In different terminal, get the IP address of the container::

    $ sudo docker inspect --format '{{ .NetworkSettings.IPAddress }}' strongtnc

Assuming the command prints out ``172.17.0.2``, the strongTNC server
can be accessed on the local machine on URL http://172.17.0.2:8000/.

The container port can also be exposed on the host interface. For
example, when started as

::

    $ sudo docker run -p 8000:8000 --rm -ti strongtnc

the server can be accessed on http://localhost:8000/.

The default passwords are

- Read/Write: ``Secret123``
- Readonly: ``demo``
- User ``admin`` at the ``/admin`` interface: ``Secret123``

