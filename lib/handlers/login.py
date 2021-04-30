#!/usr/bin/env python
import json
import traceback
import urllib

import tornado.gen
import tornado.web

from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError

from lib.handlers.base import BaseHandler
from lib.settings import Settings

from common.spark import Spark

class AuthHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        try:
            print(self.get_current_user())
            code = self.get_argument("code",None)
            state = self.get_argument("state",None)
            next = self.get_argument("next",None)
            print("Code: {0}".format(code))
            print("State: {0}".format(state))
            print("Next: {0}".format(next))
            ret_val = {"success":False, "code":500, "message":"Unknown Error"}
            if code != None:
                url = "https://api.ciscospark.com/v1/access_token"
                payload = "client_id={0}&".format(Settings.client_id)
                payload += "client_secret={0}&".format(Settings.client_secret)
                payload += "grant_type=authorization_code&"
                payload += "code={0}&".format(code)
                payload += "redirect_uri={0}".format(Settings.redirect_uri)
                headers = {
                    'cache-control': "no-cache",
                    'content-type': "application/x-www-form-urlencoded"
                    }
                request = HTTPRequest(url, method="POST", headers=headers, body=payload)
                http_client = AsyncHTTPClient()
                try:
                    response = yield http_client.fetch(request)
                    message = json.loads(response.body.decode("utf-8"))
                    print("AuthHandler message:{0}".format(message))
                    person = yield Spark(message["access_token"]).get_with_retries_v2('https://api.ciscospark.com/v1/people/me')
                    my_cookie = {"token":message["access_token"], "id":person.body.get('id'), "emails":person.body.get('emails')}
                    print("AuthHandler person.body:{0}".format(my_cookie))
                    self.set_secure_cookie("sessionId", json.dumps(my_cookie), expires_days=1, version=1)
                    print("login success, redirecting to Main Page")
                    self.redirect("/")
                    return
                except HTTPError as he:
                    print("AuthHandler HTTPError Code: {0}, {1}".format(he.code, he.message))
                    ret_val = {"success":False, "code":he.code, "message":he.message}
                except Exception as e:
                    traceback.print_exc()
                    message = "{0}".format(e)
                    ret_val = {"success":False, "code":500, "message":message}
            else:
                ret_val = {"success":False, "code":500, "message":"'code' cannot be null."}
            self.write(json.dumps(ret_val))
        except Exception as ex:
            traceback.print_exc()


class LoginHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        self.post()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        print(self.request.headers)
        print(self.request.body)
        if not self.get_current_user():
            print("Not authenticated.")
            print(self.request.full_url())
            next = self.get_argument("next", None)
            state_url = "{0}://{1}/auth?".format(self.request.protocol, self.request.host)
            if next is not None:
                state_url += "next={0}&".format(next)
            print("state_url:{0}".format(state_url))
            url = 'https://api.ciscospark.com/v1/authorize?client_id={0}'.format(Settings.client_id)
            url += '&response_type=code&redirect_uri={0}'.format(urllib.parse.quote(Settings.redirect_uri))
            url += '&scope=' + Settings.scopes
            url += '&state={0}'.format(urllib.parse.quote(state_url))
            print(url)
            self.redirect(url)
        else:
            print("Already authenticated.")
            print(self.request.full_url())
            #self.set_current_user(self.get_secure_cookie("sessionId"))
            print(self.get_argument("next", u"/"))
            self.redirect(self.get_argument("next", u"/"))
