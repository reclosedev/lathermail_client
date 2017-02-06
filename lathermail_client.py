# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import datetime
import posixpath

import requests

try:
    from pytz import utc
    from dateutil.tz import tzlocal
    tz_available = True
except ImportError:
    utc = tzlocal = None
    tz_available = False


class LathermailError(Exception):
    """ Base lathermail exception
    """


class InvalidStatus(LathermailError):
    def __init__(self, response):
        super(LathermailError, self).__init__("Invalid status {0}.\n{1}".format(response.status_code, response.text))
        self.response = response
        self.code = response.status_code


class LathermailClient(object):
    def __init__(self, user, password, url="http://localhost:5000/", api_version=0, logger=None):
        self.user = user
        self.password = password
        self.url = url
        self.url_api = posixpath.join(self.url, "api/{0}/".format(api_version))
        self.logger = logger or logging.getLogger("lathermail_client")
        self._session = requests.Session()
        self._session.headers = self._auth_headers(user, password)

    def get_inboxes(self, password=None):
        return self._get("inboxes", headers=self._auth_headers(user=None, password=password))["inbox_list"]

    def get_single_message(self, message_id):
        return self._get("messages/{0}".format(message_id))["message_info"]

    def get_messages(self, recipients_address=None, recipients_name=None, subject=None,
                     read=None, created_at_lt=None, created_at_gt=None,
                     sender_address=None, sender_name=None,
                     recipients_address_contains=None, recipients_name_contains=None,
                     subject_contains=None,
                     sender_address_contains=None, sender_name_contains=None):
        params = {
            "recipients_address": recipients_address, "recipients_name": recipients_name, "subject": subject,
            "subject_contains": subject_contains, "read": read,
            "created_at_gt": created_at_gt, "created_at_lt": created_at_lt,
            "sender_address": sender_address, "sender_name": sender_name,
            "recipients_address_contains": recipients_address_contains,
            "recipients_name_contains": recipients_name_contains,
            "sender_address_contains": sender_address_contains, "sender_name_contains": sender_name_contains,
        }
        params = _prepare_params(params)
        messages = self._get("messages/", params=params)["message_list"]
        self.logger.debug("Searching emails: %s, found %d messages", params, len(messages))
        return messages

    def get_attachment(self, message_id, attachment_index):
        return self._get("messages/{0}/attachments/{1}".format(message_id, attachment_index), parse_json=False)

    def delete_single_message(self, message_id):
        self._delete("messages/{0}".format(message_id))

    def delete_messages(self, **params):
        params = _prepare_params(params)
        self._delete("messages/", params=params)

    def _get(self, resource, **kwargs):
        return self._request_api("GET", resource, **kwargs)

    def _delete(self, resource, **kwargs):
        return self._request_api("DELETE", resource, **kwargs)

    def _request_api(self, method, resource, params=None, data=None, parse_json=True, raise_error=True, **kwargs):
        if resource.startswith("http"):
            url = resource
        else:
            url = posixpath.join(self.url_api, resource)

        response = self._session.request(method, url, params=params, data=data, **kwargs)
        if raise_error and response.status_code >= 400:
            raise InvalidStatus(response)

        if not parse_json:
            return response.content
        if response.status_code == 204:
            return None
        try:
            data = response.json()
            js = str(data)[:500]
            self.logger.debug("lathermail: url: %s, status: %s, response: %s", response.url, response.status_code, js)
        except ValueError:
            msg = "lathermail: url: %s, status: %s, response: %s" % (
                response.url, response.status_code, response.text
            )
            self.logger.warning(msg)
            raise LathermailError(msg)
        return data

    def _auth_headers(self, user, password=None):
        return {"X-Mail-Inbox": user, "X-Mail-Password": password or self.password}


def _prepare_params(params):
    for date_param in "created_at_gt", "created_at_lt":
        value = params.get(date_param)
        if value is not None:
            if isinstance(value, datetime.datetime):
                value = _to_utc(value)
                params[date_param] = value.isoformat()

    for name, value in list(params.items()):
        if value is None:
            del params[name]
        else:
            proper_name = _params_remap.get(name)
            if proper_name:
                params[proper_name] = params.pop(name)
    return params


def _to_utc(dt):
    if not tz_available:
        return dt

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tzlocal())
    return utc.normalize(dt)


_params_remap = {
    "recipients_address": "recipients.address",
    "recipients_address_contains": "recipients.address_contains",
    "recipients_name": "recipients.name",
    "recipients_name_contains": "recipients.name_contains",
    "sender_address": "sender.address",
    "sender_address_contains": "sender.address_contains",
    "sender_name": "sender.name",
    "sender_name_contains": "sender.name_contains",
}
