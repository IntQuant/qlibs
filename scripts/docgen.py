import sys
import types
import inspect
from html import escape as nq_escape
import os
import re

extrasearchpath = os.path.realpath(os.path.join(__file__, os.pardir, os.pardir))
sys.path.append(extrasearchpath)


def escape(s):
    return nq_escape(s, quote=True)


def log(*args, **kwargs):
    return print("[LOG]", *args, file=sys.stderr, **kwargs)


def cut_and_strip(s, what):
    return s[len(what) :].lstrip(" ").rstrip(" ")


class DocsGenerator:
    def __init__(self):
        self.visited = list()
        self.excluded = [object, types.CodeType]
        self.restrict_module = None
        self.stat_all = 0
        self.stat_documented = 0

    def generate_module_docs(self, module):
        self.restrict_module = module
        self.visited = list()
        return self.gen_docs(module)

    def process_docstring(self, doc_string, res):
        self.stat_all += 1
        lines = doc_string.splitlines()
        if len(lines) > 0:
            self.stat_documented += 1
        for doc_line in lines:
            if doc_line:
                res.append(f"<p>{escape(doc_line)}</p>")

    def filter_function(self, func):
        res = (
            func.__name__.startswith("__")
            and func.__name__.endswith("__")
            and func.__name__ != "__init__"
        )
        return res

    def gen_docs(self, thing):

        if (
            inspect.isbuiltin(thing)
            or (thing in self.visited)
            or type(thing) in self.excluded
        ):
            return

        if self.restrict_module is not None:
            if (
                inspect.getmodule(thing) != self.restrict_module
                and thing is not self.restrict_module
            ):
                return

        self.visited.append(thing)

        doc_string = inspect.getdoc(thing)

        if doc_string is None:
            doc_string = ""

        res = []

        if thing is type:
            return

        # print(thing, thing.__name__)

        if inspect.ismodule(thing):
            res.append(f"<h2>Module {escape(thing.__name__)}</h2>")
            res.append("<blockquote>")
            self.process_docstring(doc_string, res)

            for next_thing in dir(thing):
                try:
                    nr = self.gen_docs(getattr(thing, next_thing))
                    if nr is not None:
                        res.extend(nr)
                except AttributeError as e:
                    pass
            res.append("</blockquote>")
        elif inspect.isclass(thing):
            res.append(
                f"<h3>Class {escape(thing.__name__ + str(inspect.signature(thing)))}</h3>"
            )
            res.append("<blockquote>")
            self.process_docstring(doc_string, res)

            for next_thing in dir(thing):
                try:
                    nr = self.gen_docs(getattr(thing, next_thing))
                    if nr is not None:
                        res.extend(nr)
                except AttributeError as e:
                    pass
            res.append("</blockquote>")
        elif inspect.isroutine(thing):
            if self.filter_function(thing):
                return

            res.append(
                f"<h4>Function {escape(thing.__name__ + str(inspect.signature(thing)))}</h4>"
            )
            res.append("<blockquote>")
            self.process_docstring(doc_string, res)
            res.append("</blockquote>")
        
        
        return res


def handle_formatting(s):
    s = re.sub(r"\*(.*?)\*", r"<b>\1</b>", s)
    # print(s, r)
    return s

with open("basedoc.html", "r") as f:
    HTML_CONSTRUCT = f.read()

if __name__ == "__main__":
    dg = DocsGenerator()

    from qlibs import util, matrix, vec, resource_loader

    from qlibs.net import connection, qpacket
    from qlibs.gui.window_provider import window_provider
    from qlibs.models import modelloader, modelrenderer

    libs = [
        matrix,
        vec,
        modelloader,
        modelrenderer,
        resource_loader,
        util,
        connection,
        qpacket,
        window_provider,
    ]

    libs.sort(key=lambda x: x.__name__)

    fullres = []

    for lib in libs:
        print(f"Generating docs for {lib.__name__}")
        fullres.extend(dg.generate_module_docs(lib))

    s = "\n      ".join(map(handle_formatting, fullres))

    with open("docs.html", "w") as f:
        print(HTML_CONSTRUCT % s, file=f)

    print("-"*20)
    prc = round(100*dg.stat_documented/dg.stat_all, 2)
    print(f"{dg.stat_documented} documented out of {dg.stat_all}, ({prc}%)")
