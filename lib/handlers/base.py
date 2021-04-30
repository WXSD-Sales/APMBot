import json
import tornado.web

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        cookie = self.get_secure_cookie("sessionId", max_age_days=1, min_version=1)
        if cookie != None:
            cookie = cookie.decode('utf-8')
            cookie = json.loads(cookie)
        return cookie
