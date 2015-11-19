###
### nginx-ldap-auth-proxy container
###

FROM python:2.7
MAINTAINER Shu Tadaka <tadaka@sb.ecei.tohoku.ac.jp>

RUN apt-get update
RUN apt-get install -y libldap2-dev libsasl2-dev

RUN mkdir /opt/nginx-ldap-auth-proxy
ADD ./nginx-ldap-auth-proxy.py /opt/nginx-ldap-auth-proxy/nginx-ldap-auth-proxy.py
ADD ./requirements.txt /opt/nginx-ldap-auth-proxy/requirements.txt
RUN pip install -r/opt/nginx-ldap-auth-proxy/requirements.txt

EXPOSE 80
CMD ["uwsgi", "--chdir", "/opt/nginx-ldap-auth-proxy", "--http-socket", "0.0.0.0:80", "--wsgi-file", "nginx-ldap-auth-proxy.py"]
