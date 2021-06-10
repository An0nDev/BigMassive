import flask as flask

app = flask.Flask (__name__)

@app.route ("/")
def root ():
    return """
    <head>
        <script src="/supplementary.js"></script>
        <script src="/test.js"></script>    
    </head>
    """

@app.route ("/<string:script_name>.js")
def test_js (script_name):
    return flask.send_file (f"{script_name}.js", max_age = -1) # note, can be used to access any file on the system, so only use locally!

app.run ()