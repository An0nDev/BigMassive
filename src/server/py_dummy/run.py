import DummyApp
import os, os.path
def resolve_path (path): return os.path.abspath (os.path.join (os.getcwd (), path))
path_to_onedef_js = resolve_path ("../../client/js_interpreted/onedef.js")
path_to_app_onedef = resolve_path ("../../../example_no_annotations.onedef")

DummyApp.DummyApp (path_to_onedef_js = path_to_onedef_js, path_to_app_onedef = path_to_app_onedef).run ()