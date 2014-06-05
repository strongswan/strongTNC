strongTNC Test VM
#################

Deployment Docs
===============

This VM is only for testing purposes. Please refer to ``/docs/deployment.rst``
for information on how to deploy strongTNC in a production environment.

Vagrant Test VM
===============

In this directory, we provide a ready-to-go Vagrant_ configuration that allows
you to set up a strongTNC test VM within minutes.

With a single command, Vagrant downloads an Ubuntu 12.04 LTS image, configures
a Virtualbox VM to run it, and starts the VM.

After the VM has started for the first time, it is automatically provisioned
using Ansible_. The configuration uses Apache2 and mod_wsgi to run strongTNC.
The provisioning can be parametrized to use either SQLite or MySQL.

Requirements
------------

- Vagrant_ (For the VM automation)
- Virtualbox_ (You could also change the Vagrantfile to use VMware instead)
- Ansible_ (For the provisioning)

You should install Vagrant and Virtualbox via your regular package manager.
Because Ansible has a fast development cycle, it is often outdated in the
regular package sources, therefore installing it via pip might be the better
solution::

    $ sudo pip install -U ansible

Deploying
---------

To deploy the test VM using the default database (SQLite)::

    $ vagrant up

If you want to use MySQL instead of SQLite (recommended!), set the `DATABASE`
env variable::

    $ DATABASE=mysql vagrant up

If the VM already exists and you want to re-run the provisioning script::

    $ DATABASE=mysql vagrant provision 

Usage
-----

The strongTNC instance should now automatically be available at the following
URL on your host system::

    http://localhost:8080/

This works because in the background, Vagrant redirects the following ports
from the host system to the VM::

    8080 => 80
    4343 => 443

The default passwords are as follows:

- Read/Write: ``admin``
- Readonly: ``readonly``

To SSH into the VM::

    $ vagrant ssh

If you want to shutdown the VM::

    $ vagrant halt

To start it again::

    $ vagrant up

And to destroy it::

    $ vagrant destroy

.. _Vagrant: http://www.vagrantup.com/
.. _Ansible: http://www.ansible.com/
.. _Virtualbox: https://www.virtualbox.org/
