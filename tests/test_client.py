import datetime

import pytest
import httmock

from lathermail_client import LathermailClient, LathermailError, InvalidStatus


def test_inboxes():
    user, password = "u1", "p1"
    resp = {"inbox_list": ["a", "b"]}
    client = LathermailClient(user, password)

    @httmock.all_requests
    def inboxes_mock(url, request):
        assert url.path == "/api/0/inboxes"
        assert request.headers["X-Mail-Password"] == password
        assert "X-Mail-Inbox" not in request.headers
        return json_response(resp)


    with httmock.HTTMock(inboxes_mock):
        assert client.get_inboxes() == resp["inbox_list"]
        password = "p2"
        assert client.get_inboxes(password) == resp["inbox_list"]


def test_single_message():
    user, password = "u1", "p1"
    resp = {"message_info": {"a": "b"}}
    client = LathermailClient(user, password)
    message_id = "aaaa"
    last_request = [None]

    @httmock.all_requests
    def messages_mock(url, request):
        assert url.path == "/api/0/messages/{0}".format(message_id)
        assert request.headers["X-Mail-Password"] == password
        assert request.headers["X-Mail-Inbox"] == user
        last_request[0] = request
        return json_response(resp)


    with httmock.HTTMock(messages_mock):
        assert client.get_single_message(message_id) == resp["message_info"]
        assert last_request[0].method == "GET"

        message_id = "bbb"
        client.delete_single_message(message_id)
        assert last_request[0].method == "DELETE"


def test_messages():
    user, password = "u1", "p1"
    resp = {"message_list": [{"a": "b"}, {"c": "d"}]}
    client = LathermailClient(user, password)

    last_request = [None]
    last_url = [None]

    @httmock.all_requests
    def messages_mock(url, request):
        assert url.path == "/api/0/messages/"
        assert request.headers["X-Mail-Password"] == password
        assert request.headers["X-Mail-Inbox"] == user
        last_url[0] = url
        last_request[0] = request
        return json_response(resp, 204 if request.method == "DELETE" else 200)


    with httmock.HTTMock(messages_mock):
        assert client.get_messages() == resp["message_list"]
        assert not last_url[0].query
        client.get_messages(recipients_address="tst@tst.tt")
        assert "tst.tt" in last_url[0].query
        assert "recipients.address" in last_url[0].query
        assert last_request[0].method == "GET"

        client.get_messages(recipients_address_contains="tst@tst.tt")
        assert "tst.tt" in last_url[0].query
        assert "recipients.address_contains" in last_url[0].query
        assert last_request[0].method == "GET"

        now = datetime.datetime.now()
        client.get_messages(created_at_lt=now)
        assert now.strftime("%Y-%m-%d") in last_url[0].query

        client.delete_messages(recipients_address="tst@tst.tt")
        assert last_request[0].method == "DELETE"
        assert "tst.tt" in last_url[0].query
        assert "recipients.address" in last_url[0].query


def test_attachment():
    user, password = "u1", "p1"
    resp = "data"
    client = LathermailClient(user, password)
    message_id = "aaaa"
    attachment_index = 1

    @httmock.all_requests
    def messages_mock(url, request):
        assert url.path == "/api/0/messages/{0}/attachments/{1}".format(message_id, attachment_index)
        assert request.headers["X-Mail-Password"] == password
        assert request.headers["X-Mail-Inbox"] == user
        return resp

    with httmock.HTTMock(messages_mock):
        assert client.get_attachment(message_id, attachment_index) == resp
        attachment_index = 2
        assert client.get_attachment(message_id, attachment_index) == resp


def test_exceptions():
    user, password = "u1", "p1"
    client = LathermailClient(user, password)
    resp = None

    @httmock.all_requests
    def req_mock(url, request):
        return resp

    with httmock.HTTMock(req_mock):
        for code in 400, 403, 500:
            resp = json_response({"a": "b"}, code)
            with pytest.raises(InvalidStatus) as e:
                client.get_inboxes()
            assert e.value.code == code

        content = b"<html>not json here </html>"
        resp = httmock.response(200, content=content)
        with pytest.raises(LathermailError) as e:
            client.get_inboxes()
        assert content.decode("utf8") in repr(e.value)


def json_response(data, code=200):
    return httmock.response(code, data, {'Content-Type': 'application/json'})
