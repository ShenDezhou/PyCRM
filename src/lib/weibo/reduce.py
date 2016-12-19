# encoding:utf-8
import json
import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

print 30 * '*'
in_folder = r'E:\weibocontent3'
out_folder = r'E:\weibocontent4'
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


def check(item,rlist):
    print item
    for r_item in rlist:
        if item.get("name") == r_item.get("name"):
            return True
    return False

def reduce_list(dlist):
    if not dlist:
        return []
    rlist = list()
    for d_item in dlist:
        if check(d_item,rlist):
            for r_item in rlist:
                if not r_item:
                    continue
                if d_item.get("name") == r_item.get("name"):
                    r_item["count"] += d_item.get("count")
                    if d_item.get("parents"):
                        if not r_item.get("parents"):
                            r_item["parents"] = list()
                        for pi in d_item["parents"]:
                            r_item["parents"].append(pi)
                    if d_item.get("children"):
                        if not r_item.get("children"):
                            r_item["children"] = list()
                        for pi in d_item["children"]:
                            r_item["children"].append(pi)
        else:
            rlist.append(d_item)
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
            if treedata['parents']:
                treedata['parents'] = reduce_list(treedata['parents'])
            if treedata['children']:
                treedata['children'] = reduce_list(treedata['children'])

        with open(file_output, 'w') as f:
            f.write(json.dumps(treedata).decode('unicode-escape'))


print 'job done'