# encoding: utf-8
import json
import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

print '---'
def parse(in_folder):
    print in_folder
    _ = dict()
    for root,dir,files in os.walk(in_folder):
        if not _.get("children"):
            _["children"] = list()
            _["name"]= os.path.split(in_folder)[-1]
        for subdir in dir:
            if subdir.startswith("."):
                continue
            sub_path = os.path.join(root,subdir)
            dd = parse(sub_path)
            if dd:
                _["children"].append(dd)
        for subfile in files:
            if os.path.splitext(subfile)[1] in [".js", ".html", ".css",".scss",".md",".yml"]:
                subf_path = os.path.join(root, subfile)

                ff = dict()
                ff["name"] = subfile
                with open(subf_path, "r") as handle:
                    ff["size"] = sum(1 for line in handle)
                if ff:
                    _["children"].append(ff)
        if len(_.get("children"))==0:
            _.pop("children")
        break
    return _

print 30 * '*'
input_folder = u'E:\ShenDezhou.github.io'
out_folder = u'E:\ShenDezhou.github.io1'
ddd = parse(input_folder)
ddd["name"] = os.path.split(input_folder)[-1]
print ddd
file_output = os.path.join(out_folder, "github.json")
with open(file_output, 'w') as f:
    f.write(json.dumps(ddd).decode("unicode-escape"))
print 'job done'