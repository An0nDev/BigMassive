assert __name__ == "__main__", "BigMassive dummy server must be run from command line"
import sys, functools, os, os.path
assert len (sys.argv) == 3, "need two args, path to BigMassive.js and path to app.bm"
path_to_bm_js = os.path.join (os.getcwd (), sys.argv [1])
path_to_app_bm = os.path.join (os.getcwd (), sys.argv [2])

import flask
app = flask.Flask (__name__)
bm_js_url = "/bm.js"
app_bm_url = "/app.bm"

@app.route ("/", defaults = {"url": ""})
@app.route ("/<string:url>")
def catch_all (url):
    url = "/" + url
    if url == "/":
        return f" \
            <html> \
                <head> \
                    <script src=\"{bm_js_url}\" bm-app-url=\"{app_bm_url}\"></script> \
                </head> \
            </html> \
        "
    elif url == bm_js_url:
        return flask.send_file (path_to_bm_js)
    elif url == app_bm_url:
        return flask.send_file (path_to_app_bm)
    else:
        flask.abort (404)

app.run ()
