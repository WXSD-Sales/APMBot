# -*- coding: utf-8 -*-
#!/usr/bin/env python
import json
import os
import traceback

import tornado.gen
import tornado.httpserver
import tornado.ioloop
import tornado.web

from common.spark import Spark

from lib.settings import Settings
from lib.mongo_controller import MongoController
from lib.handlers.base import BaseHandler
from lib.handlers.login import AuthHandler, LoginHandler

from tornado.options import define, options, parse_command_line
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError
from datetime import datetime
from pymongo import ASCENDING

define("debug", default=False, help="run in debug mode")

#TODO:
#3 - Adjust sizing so half width page looks good (demoing next to teams client)

class MainHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        try:
            person = self.get_current_user()
            print(person)
            if not person:
                self.redirect('/login')
            else:
                app = self.application.settings['db'].get_comments(person['id'])
                print(app)
                self.render("index.html", app=app)
        except Exception as e:
            traceback.print_exc()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        try:
            secret_equal = Spark.compare_secret(self.request.body, self.request.headers.get('X-Spark-Signature'), Settings.secret_phrase)
            if secret_equal or Settings.secret_phrase.lower()=="none":
                webhook = json.loads(self.request.body)
                if webhook['data']['personId'] != Settings.bot_id:
                    print("MainHandler Webhook Received:")
                    print(webhook)
                    reply_msg = self.help_msg()
                    yield self.application.settings['spark'].post_with_retries('https://api.ciscospark.com/v1/messages', {'markdown':reply_msg, 'roomId':webhook['data']['roomId']})
            else:
                print("CardsHandler Secret does not match")
        except Exception as e:
            print("CardsHandler General Error:{0}".format(e))
            traceback.print_exc()

    def help_msg(self):
        msg = "To use this bot, login with your Webex account [here](https://webex-apm-demo.herokuapp.com/).\n\n"
        msg += "If you toggle the status of your mock server on that page, this bot will send you a card.   \n"
        msg += "You can interact with the card to see real time updates on the mock server page.\n\n"
        msg += "Any actions you take on the mock server page or with this bot will only be visible to you (from the account you used to sign in).\n\n"
        msg += "You can find a walkthrough for this demo, along with the code at: https://github.com/WXSD-Sales/APMBot  \n"
        msg += "If you have any questions or ideas for features you would like to see added, please reach out to wxsd@external.cisco.com"
        return msg

class CardsHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        try:
            secret_equal = Spark.compare_secret(self.request.body, self.request.headers.get('X-Spark-Signature'), Settings.secret_phrase)
            if secret_equal or Settings.secret_phrase.lower()=="none":
                webhook = json.loads(self.request.body)
                print("CardsHandler Webhook Attachment Action Received:")
                print(webhook)
                attachment = yield self.application.settings['spark'].get_with_retries_v2('https://api.ciscospark.com/v1/attachment/actions/{0}'.format(webhook['data']['id']))
                print("attachment.BODY:{0}".format(attachment.body))
                message_id = attachment.body['messageId']
                room_id = attachment.body['roomId']
                person_id = attachment.body['personId']
                inputs = attachment.body.get('inputs', {})
                print("messageId:{0}".format(message_id))
                print("roomId:{0}".format(room_id))
                print("inputs:{0}".format(inputs))
                room = yield self.application.settings['spark'].get_with_retries_v2('https://api.ciscospark.com/v1/rooms/{0}'.format(room_id))
                room_type = room.body.get('type')
                person = "you"
                if room_type == "group":
                    person = "<@personId:{0}|>".format(person_id)
                reply_msg = ''
                person_obj = yield self.application.settings['spark'].get_with_retries_v2('https://api.ciscospark.com/v1/people/{0}'.format(person_id))
                display_name = person_obj.body.get('displayName')
                if inputs.get('submit') in ["ack","ack_res"] and inputs.get('id') not in [None, ""]:
                    message = "Incident ID: <b>{0}</b> has been acknowledged by ".format(inputs.get('id'))
                    comment = {"author":"System", "message":message + display_name}
                    result = self.application.settings['db'].insert(person_id, comment=comment)
                    reply_msg = message + person + ". View it [here]({0}).".format(inputs["url"])
                elif inputs.get('submit') == "inc":
                    if inputs.get('comment') in [None, ""]:
                        reply_msg = "Comment cannot be blank."
                    else:
                        comment = {"author":display_name, "message":inputs.get('comment')}
                        result = self.application.settings['db'].insert(person_id, comment=comment)
                        reply_msg = "Comment added.  View it at {0}".format(inputs["url"])
                if reply_msg != '':
                    yield self.application.settings['spark'].post_with_retries('https://api.ciscospark.com/v1/messages', {'markdown':reply_msg, 'roomId':room_id})
            else:
                print("CardsHandler Secret does not match")
        except Exception as e:
            print("CardsHandler General Error:{0}".format(e))
            traceback.print_exc()

class CommentsHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        try:
            person = self.get_current_user()
            if not person:
                self.redirect('/login')
            else:
                timestamp = self.get_argument("timestamp")
                print(timestamp)
                comments = self.application.settings['db'].get_comments(person['id'], float(timestamp))
                print(comments)
                self.write({"comments":comments})
        except Exception as e:
            traceback.print_exc()

class ToggleHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        try:
            person = self.get_current_user()
            if not person:
                self.redirect('/login')
            else:
                print(self.get_current_user())
                webhook = json.loads(self.request.body)
                print("ToggleHandler Post Received:")
                print(webhook)
                message = "Server went down. Check your Webex Messages."
                if webhook["isRunning"]:
                    message = "Server restored. Check your Webex Messages."
                comment = {"author":"System", "message":message, "type":"system"}
                result = self.application.settings['db'].insert(person["id"], webhook["isRunning"], comment)
                yield self.sendCard(webhook["isRunning"], self.get_current_user()["id"])
                print("result:{0}".format(result))
                resp = {"timestamp_float":result["timestamp_float"], "comment":comment}
        except Exception as e:
            traceback.print_exc()
            resp = {"error":e}
        self.write(resp)

    @tornado.gen.coroutine
    def sendCard(self, is_running, toPersonId):
        if is_running:
            card_json = self.load_card('lib/cards/resolved_card.json')
        else:
            card_json = self.load_card('lib/cards/alert_card.json')
        #id = self.get_current_user()["id"]
        id = "SI_A1234"
        url = Settings.base_uri
        card_json["body"][1]["facts"][0]["value"]= id #set the card Id
        card_json["body"][3]["text"] = card_json["body"][3]["text"].format(datetime.utcnow().strftime("%H:%M:%S")) #set the timestamp
        card_json["body"][4]["actions"][0]["data"]["id"] = id #set the card Id
        card_json["body"][4]["actions"][0]["data"]["url"] = url #set the event url
        card_json["body"][4]["actions"][1]["url"]= url #set the event url
        card_json["body"][4]["actions"][2]["card"]["body"][1]["actions"][0]["data"]["url"]= url #set the event url
        card_json["body"][4]["actions"][2]["card"]["body"][1]["actions"][0]["data"]["id"]= id #set the card Id
        card_json = self.finalize_card_json(toPersonId, card_json)
        yield self.application.settings['spark'].post_with_retries('https://api.ciscospark.com/v1/messages', card_json)

    def load_card(self, filepath):
        card_json = {}
        with open(filepath, "r") as f:
            msg = f.read()
            card_json = json.loads(msg)
        return card_json

    def finalize_card_json(self, destination, card_json, direct=True):
        card = {
                "markdown": "APMBot Demo Card",
                "attachments": [
                    {
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "content": card_json
                    }
                ]
            }
        if direct:
            card.update({"toPersonId": destination})
        else:
            card.update({"roomId": destination})
        return card


@tornado.gen.coroutine
def main():
    try:
        parse_command_line()
        static_dir = os.path.join(os.path.dirname(__file__), "static")
        app = tornado.web.Application(
            [   (r"/", MainHandler),
                (r"/auth", AuthHandler),
                (r"/cards", CardsHandler),
                (r"/comments", CommentsHandler),
                (r"/login", LoginHandler),
                (r"/toggle", ToggleHandler),
                (r"/css/(.*)", tornado.web.StaticFileHandler, {'path': os.path.join(static_dir, "css")}),
                (r"/fonts/(.*)", tornado.web.StaticFileHandler, {'path': os.path.join(static_dir, "fonts")}),
                (r"/images/(.*)", tornado.web.StaticFileHandler, {'path': os.path.join(static_dir, "images")}),
                (r"/js/(.*)", tornado.web.StaticFileHandler, {'path': os.path.join(static_dir, "js")}),
            ],
            cookie_secret="asdfuerhkcxcuqwena;fsdiaxwuejadls",
            xsrf_cookies=False,
            debug=options.debug,
            template_path=static_dir
            )
        app.settings['db'] = MongoController()
        app.settings['db'].comments.create_index([("timestamp", 1)], expireAfterSeconds=14400)#14400 == 4 hours
        app.settings['db'].issues.create_index([("timestamp", 1)], expireAfterSeconds=14400)#14400 == 4 hours
        app.settings['debug'] = options.debug
        app.settings['settings'] = Settings
        app.settings['spark'] = Spark(Settings.token)
        server = tornado.httpserver.HTTPServer(app)
        print("Serving... on port {0}".format(Settings.port))
        server.bind(Settings.port)  # port
        print("Debug: {0}".format(app.settings["debug"]))
        server.start()
        tornado.ioloop.IOLoop.instance().start()
        print('Done')
    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    main()
