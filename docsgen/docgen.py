import os
import os.path
import importlib
import inspect
import pyclbr

from markdown_code_blocks import highlight

if not os.path.exists("./setup.py"):
    print("setup.py not found, probably launched in wrong folder")
    exit(1)

patternpath = "./docsgen/pattern.html"
print("Loading pattern...")
with open(patternpath) as f:
    patterndata = f.read()

print("Copying styles...")
stylepath = "./docs/style.css"
if os.path.exists(stylepath):
    os.unlink(stylepath)
os.link("./docsgen/style.css", stylepath)

def quotesplit(s):
    def stripquotes(s):
        return s.strip("\n").strip('"').strip("'")
    
    res = []
    left = 0
    quote_found = False
    for i, e in enumerate(s):
        if e == " " and not quote_found:
            res.append(stripquotes(s[left:i]))
            left = i+1
        if e in ['"', "'"]:
            quote_found = not quote_found
    res.append(stripquotes(s[left:]))
    return res


def gen_docs_for_module(module):
    def safe_highlight(data):
        return highlight(str(data))
    def get_desc(thing):
        if inspect.isclass(thing):
            return "Class"
        if inspect.ismethod(thing):
            return "Method"        
        if inspect.ismemberdescriptor(thing):
            return "Member"
        
        if inspect.isfunction(thing):
            return "Function"
        return ""
    def get_sig(thing):
        if inspect.isfunction(thing):
            source = list(map(lambda x:x.split("#", maxsplit=1)[0].strip(), inspect.getsource(thing).splitlines()))
            for i in range(len(source)):
                if source[i].endswith(":"):
                    return " ".join(source[:i+1]).strip(" ")[4:-1]
            return " ".join(source)
        return getattr(thing, "__name__", None)

    res = []
    res.append(safe_highlight(inspect.getdoc(module)))
    #keys = getattr(module, "__all__", dir(module))
    keys = pyclbr.readmodule_ex(module.__name__)
    for key in keys:
        value = getattr(module, key)
        if key.startswith("_"):
            continue
        res.append(f"<h2 id={module.__name__+key}>{get_desc(value)} {get_sig(value)}</h2>")
        res.append(safe_highlight(inspect.getdoc(value)))
        res.append('<div class="classmethods">')
        for skey in dir(value):
            if skey.startswith("_") and skey != "__init__":
                continue
            svalue = getattr(value, skey)
            if inspect.isbuiltin(svalue):
                continue
            res.append(f"<h3 id={module.__name__+skey}>{get_desc(svalue)} {get_sig(svalue)}</h3>")
            doc = inspect.getdoc(svalue)
            if doc is not None:
                val = safe_highlight(doc)
                res.append(val)
        res.append('</div>')
            
    return "\n".join(res)

class DataHeader:
    def __init__(self, text):
        self.text = text

def compile_index(indexname, resname, backlink=None):
    indexpath = os.path.join("./docsgen/index", indexname)
    resfile = os.path.join("./docs/", resname)
    
    index = dict()
    additional_index_files = set()
    modules = list()

    print(f"Parsing index {indexname}...")
    with open(indexpath, "r") as f:
        for line in f:
            if len(line) < 2:
                continue
            cmd, *data = quotesplit(line)
            if cmd == "INCLUDE":
                path, file = data
                index[path] = file
            elif cmd == "INDEX":
                opath, dpath = data
                compile_index(
                    opath, dpath,
                    backlink=indexname,
                )
                index[opath] = dpath
                additional_index_files.add(opath)
            elif cmd == "MODULE":
                path = data[0]
                print(f"Importing module {path}")
                module = importlib.import_module(path)
                modules.append(module)
                index[path] = module
            elif cmd == "HEADER":
                path = data[0]
                index[path] = DataHeader(path)
            else:
                print("!!! Unrecognized command:", cmd)

    resindex = list()

    print(f"Generating index for {indexpath}")
    if backlink is not None:
        resindex.append(f'<p><a href="{backlink}.html">🔗 Back</a></p>')

    for key in index:
        if key in additional_index_files:
            resindex.append(f'<p><a href="{index[key]}">🔗 {key}</a></p>')
        else:
            if isinstance(index[key], DataHeader):
                resindex.append(f'<h1><a href="#{key.replace(" ", "-")}">{key}</a></h1>')
            else:
                resindex.append(f'<p><a href="#{key.replace(" ", "-")}">{key}</a></p>')
                if inspect.ismodule(index[key]):
                    keys = pyclbr.readmodule_ex(key)
                    tmp = []
                    for sk, sv in keys.items():
                        tmp.append(f'<li><a href=#{key+sk}>{sv.__class__.__name__} {sk}</a></li>')
                    resindex.append(f'<ul class="modulelist">{"".join(tmp)}</ul>')

    resindex = "\n".join(resindex)

    resdata = list()

    print("Parsing files...")
    for key, value in index.items():
        if key in additional_index_files:
            continue
        
        elif isinstance(value, DataHeader):
            resdata.append(f'<h1 id={key.replace(" ", "-")}>{key}</h1><hr>')

        elif not isinstance(value, str):
            html = gen_docs_for_module(value)
            resdata.append(f'<h1 id={key.replace(" ", "-")}>{key}</h1>')
            resdata.append(html)

        elif value.endswith(".md"):
            path = os.path.join("./docsgen/data", value)
            print(f"Parsing {path}")
            with open(path) as f:
                html = highlight(f.read())
            resdata.append(f'<h1 id={key.replace(" ", "-")}>{key}</h1>')
            resdata.append(html)
        else:
            print(f"Unknown extension of {value}")

    resdata = "\n".join(resdata)

    print(f"Writing file {resfile}...")
    with open(resfile, "w") as f:
        data = patterndata % (resindex, resdata)
        f.write(data)

    print("Done!")

if __name__ == "__main__":
    compile_index("index", "index.html")