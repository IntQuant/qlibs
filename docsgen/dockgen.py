import os
import os.path

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

def compile_index(indexname, resname, backlink=None):
    indexpath = os.path.join("./docsgen/", indexname)
    resfile = os.path.join("./docs/", resname)
    
    index = dict()
    additional_index_files = set()

    print(f"Parsing index {indexname}...")
    with open(indexpath, "r") as f:
        for line in f:
            cmd, *data = line.split()
            if cmd == "LINK":
                path, file = data
                index[path] = file
            if cmd == "INDEX":
                opath, dpath = data
                compile_index(
                    opath, dpath,
                    backlink=indexname,
                )
                index[opath] = dpath
                additional_index_files.add(opath)

    resindex = list()

    print(f"Generating index for {indexpath}")
    if backlink is not None:
        resindex.append(f'<p><a href="{backlink}.html">[LINK] Back</a></p>')

    for key in index:
        if key in additional_index_files:
            resindex.append(f'<p><a href="{index[key]}">[LINK] {key}</a></p>')
        else:
            resindex.append(f'<p><a href="#{key}">{key}</a></p>')

    resindex = "\n".join(resindex)

    resdata = list()

    print("Parsing files...")
    for key, value in index.items():
        if value.endswith(".md"):
            path = os.path.join("./docsgen/data", value)
            print(f"Parsing {path}")
            with open(path) as f:
                html = highlight(f.read())
            resdata.append(f"<h1 id={key}>{key}</h2>")
            resdata.append(html)

    resdata = "\n".join(resdata)

    print(f"Writing file {resfile}...")
    with open(resfile, "w") as f:
        data = patterndata % (resindex, resdata)
        f.write(data)



    print("Done!")


compile_index("index", "index.html")