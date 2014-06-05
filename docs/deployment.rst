strongTNC Production Deployment
###############################

Due to security- and performance-considerations, strongTNC should never be
deployed into production using the ``./manage.py runserver`` command. Instead, a
proper WSGI webserver should be used, and all debug settings should be turned
off.

**Warning: Never deploy strongTNC in production without using SSL/TLS to secure
your connections, especially if you use the API.**

The following how-to assumes you're using Ubuntu or a similar Linux
distribution, but the basic concepts can be applied to any Linux distribution.

(Note: If you just want to try strongTNC, you can also use the automatially
configured testing VMs. See ``vagrant/README.rst`` for more information.)


1. Install the base system
==========================

Set up your base Ubuntu system. Make sure all the packages are up to date.


2. Install required packages
============================

Install the dependencies for strongTNC::

    sudo apt-get install wget build-essential apache2 libapache2-mod-wsgi python2.7 \
        python2.7-dev python-pip python-virtualenv libxml2-dev libxslt1-dev

If you want to use MySQL instead of SQLite, you need a few additional
dependencies::

    sudo apt-get install mysql-server mysql-client libmysqlclient-dev


3. Create directories
=====================

::

    sudo mkdir /var/www/strongTNC /etc/strongTNC
    sudo chown $(whoami):www-data /var/www/strongTNC /etc/strongTNC
    sudo chmod 775 /var/www/strongTNC /etc/strongTNC


4. Download current strongTNC release
=====================================

Download the current snapshot of the master branch from Github::

    cd /tmp
    wget https://github.com/strongswan/strongTNC/archive/master.tar.gz
    tar xfvz master.tar.gz
    mv strongTNC-master/* /var/www/strongTNC/

If you want you could also use git to clone the repository.


5. Install Python dependencies
==============================

The recommended way to install the Python dependencies is to put them in a
`Virtualenv <http://virtualenv.readthedocs.org/en/latest/>`_.

::

    cd /var/www/strongTNC
    virtualenv --no-site-packages VIRTUAL
    VIRTUAL/bin/pip install -U -r requirements.txt

If you use MySQL, you need an additional Python package::

    VIRTUAL/bin/pip install -U MySQL-python


6. strongTNC configuration
==========================

Copy the sample configuration to /etc::

    cp /var/www/strongTNC/config/settings.sample.ini /etc/strongTNC/settings.ini
    cd /etc/strongTNC/
    sudo chown $(whoami):www-data settings.ini
    sudo chmod 640 settings.ini

Now edit the configuration file with your favorite text editor. First of all,
update the database configuration. If you want to use SQLite, set them to the
following values::

    DJANGO_DB_URL = sqlite:////var/www/strongTNC/django.db
    STRONGTNC_DB_URL = sqlite:////var/www/strongTNC/ipsec.config.db

For MySQL, use the following values::

    DJANGO_DB_URL = mysql://strongtnc:<mysql-password>@127.0.0.1/strongtnc_django
    STRONGTNC_DB_URL = mysql://strongtnc:<mysql-password>@127.0.0.1/strongtnc_data

(Choose a secure password and remember it for later, when we create the MySQL
user!)

Now you need to set a value for ``SECRET_KEY``, which is used by Django to
encrypt all kinds of stuff. A way to generate such a key is the following code
snippet::

    dd if=/dev/urandom bs=128 count=1 2>/dev/null | base64 -w 175

Then set ``ALLOWED_HOSTS`` to a list of hostnames that will be allowed to serve
strongTNC, e.g. ::

    ALLOWED_HOSTS = 127.0.0.1,strongtnc.example.org

If you enable SSL/TLS for your setup (you really should!), enable secure CSRF
cookies::

    CSRF_COOKIE_SECURE = 1

You should also take a look at the ``[admins]`` section and add your name and
e-mail address there.


7a. Set up SQLite
=================

If you're using SQLite, all you need to do is changing the database
permissions::

    cd /var/www/strongTNC/
    sudo chgrp www-data django.db ipsec.config.db
    sudo chmod 660 django.db ipsec.config.db


7b. Set up MySQL
================

First, log in to the MySQL console with the root user::

    mysql -u root -p

Create the required databases:

.. code:: sql

    mysql> CREATE DATABASE strongtnc_django CHARACTER SET utf8 COLLATE utf8_unicode_ci;
    mysql> CREATE DATABASE strongtnc_data CHARACTER SET utf8 COLLATE utf8_unicode_ci;

Create a new user (make sure to replace ``<password>`` with the previously
chosen MySQL password):

.. code:: sql

    mysql> GRANT ALL PRIVILEGES ON strongtnc_django.* TO strongtnc@localhost
    -> IDENTIFIED BY '<password>';
    mysql> GRANT ALL PRIVILEGES ON strongtnc_django.* TO strongtnc@localhost
    -> IDENTIFIED BY '<password>';

Create the necessary schema in your database::

    cd /var/www/strongTNC/
    VIRTUAL/bin/python manage.py syncdb --database=meta --noinput
    VIRTUAL/bin/python manage.py syncdb --database=default --noinput


8. Collect static files
=======================

Run the following command to collect all static files in a single directory::

    cd /var/www/strongTNC/
    VIRTUAL/bin/python manage.py collectstatic --noinput


9. Apache configuration
=======================

Write the following configuration to ``/etc/apache2/sites-available/strongTNC``

.. code:: apache

    WSGIPythonPath /var/www/strongTNC:/var/www/strongTNC/VIRTUAL/lib/python2.7/site-packages

    NameVirtualHost *:80
    <VirtualHost *:80>
        RewriteEngine On
        RewriteCond %{HTTPS} off
        RewriteRule (.*) https://%{HTTP_HOST}%{REQUEST_URI} [R=301]
    </VirtualHost>

    <VirtualHost _default_:443>
        # The ServerName directive sets the request scheme, hostname and port that
        # the server uses to identify itself. This is used when creating
        # redirection URLs. In the context of virtual hosts, the ServerName
        # specifies what hostname must appear in the request's Host: header to
        # match this virtual host. For the default virtual host (this file) this
        # value is not decisive as it is used as a last resort host regardless.
        # However, you must set it for any further virtual host explicitly.
        #ServerName strongtnc.example.com

        SSLEngine on
        SSLCertificateFile /etc/apache2/ssl/strongtnc.crt
        SSLCertificateKeyFile /etc/apache2/ssl/strongtnc.key
        SSLProtocol all -SSLv2 -SSLv3
        SSLHonorCipherOrder on
        SSLCompression off
        SSLCipherSuite "EECDH+ECDSA+AESGCM EECDH+aRSA+AESGCM EECDH+ECDSA+SHA384 \
            EECDH+ECDSA+SHA256 EECDH+aRSA+SHA384 EECDH+aRSA+SHA256 EECDH+aRSA+RC4 \
            EECDH EDH+aRSA RC4 !aNULL !eNULL !LOW !3DES !MD5 !EXP !PSK !SRP !DSS"
        Header add Strict-Transport-Security "max-age=15768000"

        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/strongTNC

        <Directory /var/www/strongTNC>
            <Files wsgi.py>
                Order deny,allow
                Allow from all
            </Files>
            Options -Indexes
        </Directory>
        
        WSGIScriptAlias / /var/www/strongTNC/config/wsgi.py
        Alias /static/ /var/www/strongTNC/static/	

        WSGIPassAuthorization On
        
        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined
    </VirtualHost>

Then disable the default configuration and enable strongTNC::

    sudo a2dissite 000-default
    sudo a2ensite strongTNC

Enable necessary plugins and create ssl directory::

    sudo a2enmod ssl rewrite headers
    sudo mkdir /etc/apache2/ssl

Copy your TLS certificate and the private key to ``/etc/apache2/ssl``. If you
want to create self-signed certificates, execute the following command::

    sudo openssl req -x509 -nodes -sha256 -days 365 -newkey rsa:3072 -utf8 \
        -keyout /etc/apache2/ssl/strongtnc.key -out /etc/apache2/ssl/strongtnc.crt

Make sure the permissions are restrictive::

    sudo chown root:root /etc/apache2/ssl/*
    sudo chmod 400 /etc/apache2/ssl/*

Now restart Apache and strongTNC should be up and running! ::

    sudo service apache2 restart


10. Create default users
========================

In order to be able to login into strongTNC, you need to set a password for a
readonly user and an admin user. ::

    cd /var/www/strongTNC/
    VIRTUAL/bin/python manage.py setpassword

Visit ``https://yourserver/`` to log in.
