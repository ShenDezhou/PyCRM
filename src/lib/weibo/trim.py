# encoding:utf-8
import json
import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

print 30 * '*'
in_folder = r'E:\weibocontent2'
out_folder = r'E:\weibocontent3'
def get_calc(name):
    for output_dir, _, output_files in os.walk(out_folder):
        for of in output_files:
            if name in of:
                return True
    return False

def trim_dict(dic,keep_p_or_c):
    if not dic:
        return {}
    to_depth = "parents" if keep_p_or_c else "children"
    to_pop = "children" if keep_p_or_c else "parents"
    for item in dic:
        if item.get(to_pop):
            item.pop(to_pop)
        if item.get(to_depth):
            item[to_depth] = trim_dict(item[to_depth],keep_p_or_c)
    return dic

def check_existence(item,rlist):
    for r_item in rlist:
        if item["name"] == r_item["name"]:
            r_item["count"] += item["count"]
            if item.get("parents"):
                for pi in item["parents"]:
                    r_item["parents"].append(pi)
            if item.get("children"):
                for pi in item["children"]:
                    r_item["children"].append(pi)
            return rlist
    rlist.append(item)
    return rlist

for dir, _, files in os.walk(in_folder):
    for f in files:
        file_input = os.path.join(in_folder, f)
        file_output = os.path.join(out_folder, f)
        #check
        if get_calc(f.rstrip(".txt")):
            print f,"------------calculated--------------"
            continue
        print 30 * '-'
        print file_input
        with open(file_input, 'r') as f:
            raw_json = f.read()
            print raw_json
            treedata = dict(json.loads(raw_json))
            print treedata
            if treedata.get('parents'):
                treedata['parents'] = trim_dict(treedata['parents'],keep_p_or_c=True)
            if treedata.get('children'):
                treedata['children'] = trim_dict(treedata['children'], keep_p_or_c=False)


        with open(file_output, 'w') as f:
            f.write(json.dumps(treedata)    )


print 'job done'