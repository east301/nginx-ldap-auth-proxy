#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
#
# `nginx-ldap-auth-proxy` is intended to be used with NGINX's `ngx_http_auth_request_module`.
# The module implements client authorization based on the result of subrequest.
# This proxy intermediates NGINX and LDAP server using standard Basic authorization mechanism.
#

import contextlib
import os

import flask
import ldap


SERVER_ADDRESS = os.environ['NLAP_SERVER_ADDRESS']          # e.g. ldap://ldap.example.com
BASE_DN = os.environ['NLAP_BASE_DN']                        # e.g. ou=Peopele,dc=example,dc=com
UID_TEMPLATE = os.environ.get('NLAP', 'uid={username}')     # e.g. uid={username}
SERVICE_ATTRIBUTE = os.environ.get('NLAP_SERVICE_ATTRIBUTE', 'host')

application = flask.Flask(__name__)


@application.route('/<path:path>')
def process_request(path):
    #
    auth = flask.request.authorization
    if auth:
        service = flask.request.headers.get('X-SB-SERVICE')
        if _verify_user(auth.username, auth.password, service):
            return 'OK'

    #
    return flask.Response(
        'Authentication Required',
        401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def _verify_user(username, password, service):
    with _using_ldap_server_connection() as server:
        #
        if not _try_to_bind_to_ldap_server(server, username, password):
            return False

        #
        if service:
            if not _is_service_available_for_user(server, username, service):
                return False

        #
        return True


@contextlib.contextmanager
def _using_ldap_server_connection():
    server = ldap.initialize(SERVER_ADDRESS)
    yield server

    try:
        server.unbind_s()
    except:
        pass


def _try_to_bind_to_ldap_server(server, username, password):
    try:
        user_dn = UID_TEMPLATE.format(username=username) + ',' + BASE_DN
        server.simple_bind_s(user_dn, password)
        return True
    except:
        return False


def _is_service_available_for_user(server, username, service):
    filter = '(&({uid})({service_key}={service_value}))'.format(
        uid=UID_TEMPLATE.format(username=username),
        service_key=SERVICE_ATTRIBUTE,
        service_value=service)

    response = server.search_s(BASE_DN, ldap.SCOPE_SUBTREE, filter)
    return len(response) > 0


if __name__ == '__main__':
    application.run(debug=True, port=5000)
