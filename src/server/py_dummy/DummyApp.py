import flask

class DummyApp (flask.Flask):
    def __init__ (self, *, path_to_onedef_js, path_to_app_onedef, onedef_js_url = "/onedef.js", app_onedef_url = "/app.onedef"):
        self.path_to_onedef_js = path_to_onedef_js
        self.path_to_app_onedef = path_to_app_onedef
        self.onedef_js_url = onedef_js_url
        self.app_onedef_url = app_onedef_url

        super ().__init__ (__name__)
        self.route ("/", defaults = {"url": ""}) (self.catch_all)
        self.route ("/<string:url>") (self.catch_all)
    def catch_all (self, *, url):
        url = "/" + url
        if url == "/":
            return f" \
                <html> \
                    <head> \
                        <script src=\"{self.onedef_js_url}\" onedef-app-url=\"{self.app_onedef_url}\"></script> \
                    </head> \
                </html> \
            "
        elif url == self.onedef_js_url:
            return flask.send_file (self.path_to_onedef_js)
        elif url == self.app_onedef_url:
            return flask.send_file (self.path_to_app_onedef)
        else:
            flask.abort (404)
