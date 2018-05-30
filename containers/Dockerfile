FROM registry.fedoraproject.org/fedora:28
RUN curl -LO https://github.com/strongswan/strongTNC/archive/master.tar.gz
RUN tar xvzf master.tar.gz
RUN dnf install -y python2-virtualenv gcc libxml2-devel libxslt-devel \
	&& dnf clean all
WORKDIR /strongTNC-master
RUN virtualenv --no-site-packages VIRTUAL
RUN source VIRTUAL/bin/activate \
	&& pip install -r requirements.txt
RUN cp config/settings.sample.ini config/settings.ini
RUN sed -i 's/^;*SECRET_KEY.*/SECRET_KEY = Change-this-for-production/' config/settings.ini
RUN sed -i 's/^;*ALLOWED_HOSTS.*/ALLOWED_HOSTS = */' config/settings.ini
RUN sed -i 's/^;*DEBUG\b.*/DEBUG = 1/' config/settings.ini
RUN source VIRTUAL/bin/activate \
	&& ./manage.py migrate --database meta \
	&& ./manage.py migrate
RUN source VIRTUAL/bin/activate \
	&& ( echo Secret123 ; echo demo ) | ./manage.py setpassword
RUN source VIRTUAL/bin/activate \
	&& ./manage.py createsuperuser --database meta --noinput --username admin --email admin@example.test \
	&& yes Secret123 | ./manage.py changepassword admin --database meta

EXPOSE 8000
ENTRYPOINT source VIRTUAL/bin/activate && ./manage.py runserver 0.0.0.0:8000
