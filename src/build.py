# coding=utf-8

__author__ = 'karldoenitz'

import py_compile
import os
import os.path
import tarfile
import time
import sys


def get_css_js_list(path):
    css_list = []
    js_list = []
    for root, dirs, files in os.walk(path):
        for file_name in files:
            file_full_path = root+'/'+file_name
            if file_full_path.endswith(".css"):
                css_list.append(file_full_path)
            if file_full_path.endswith(".js"):
                js_list.append(file_full_path)
    return list(set(css_list)), list(set(js_list))


def get_minus_list(first_list, second_list):
    for i in first_list:
        if i in second_list:
            first_list.remove(i)
    return first_list


if __name__ == '__main__':
    compressed_css_list = [
        ""
    ]
    compressed_js_list = [
        "/build/project_build/static/cav/js/comingsoon.js",
        "/build/project_build/static/cav/js/common_articles.js",
        "/build/project_build/static/cav/js/common_events.js",
        "/build/project_build/static/cav/js/common_usercenter.js",
        "/build/project_build/static/cav/js/common.js",
        "/build/project_build/static/cav/js/mgr_activity_list.js",
        "/build/project_build/static/cav/js/mgr_activity_new.js",
        "/build/project_build/static/cav/js/mgr_authorized_list.js",
        "/build/project_build/static/cav/js/mgr_form_list.js",
        "/build/project_build/static/cav/js/mgr_form_normal.js",
        "/build/project_build/static/cav/js/mgr_manager_list.js",
        "/build/project_build/static/cav/js/mgr_member_app_links.js",
        "/build/project_build/static/cav/js/mgr_member_app_list.js",
        "/build/project_build/static/cav/js/mgr_member_org_list.js",
        "/build/project_build/static/cav/js/mgr_member_person_list.js",
        "/build/project_build/static/cav/js/mgr_news_list.js",
        "/build/project_build/static/cav/js/mgr_news_new.js",
        "/build/project_build/static/cav/js/mgr_org_form_list.js",
        "/build/project_build/static/cav/js/mgr_org_form_normal.js",
        "/build/project_build/static/cav/js/mgr_person_detail.js",
        "/build/project_build/static/cav/js/mgr_upload_image.js",
        "/build/project_build/static/cav/js/simple_appform_activity_detail.js",
        "/build/project_build/static/cav/js/simple_appform_vote_detail_modal.js",
        "/build/project_build/static/cav/js/simple_appform_vote.js",
    ]
    root_path = os.path.dirname(os.path.abspath(__file__))
    print root_path, type(root_path)
    d_l = [
        'rm -rf '+root_path+'/build/project_build',
        'mkdir '+root_path+'/build/project_build',
        'mkdir '+root_path+'/build/web',
        'cp '+root_path+'/__init__.py '+root_path+'/build/project_build',
        'cp '+root_path+'/config.py '+root_path+'/build/project_build',
        'cp '+root_path+'/config_web.py '+root_path+'/build/project_build',
        'cp '+root_path+'/index.py '+root_path+'/build/project_build',
        'cp -r '+root_path+'/com '+root_path+'/build/project_build',
        'cp -r '+root_path+'/conf '+root_path+'/build/project_build',
        'cp -r '+root_path+'/lib '+root_path+'/build/project_build',
        'cp -r '+root_path+'/res '+root_path+'/build/project_build',
        'cp -r '+root_path+'/static '+root_path+'/build/project_build',
        'cp -r '+root_path+'/tpl '+root_path+'/build/project_build',
        'cp -r '+root_path+'/util '+root_path+'/build/project_build',
        'cp -r '+root_path+'/views '+root_path+'/build/project_build',
        # 'mkdir '+root_path+'/build/project_build/util/asien_excel/tools/lib/export',
        # 'cp -rf '+root_path+'/java/AsienExcel/build/* '+root_path+'/build/project_build/util/asien_excel/tools/lib/export'
    ]
    for command in d_l:
        os.popen(command)
        print command
    try:
        product = sys.argv[1]
        debug = sys.argv[2]
    except:
        product = 'production = True'
        debug = 'debug = False'
    path = './build/project_build'
    # 处理css和js文件,获取需要处理的css和js文件路径
    css_list, js_list = get_css_js_list(path)
    css_list = get_minus_list(css_list, compressed_css_list)
    js_list = get_minus_list(js_list, compressed_js_list)
    # 开始处理css文件
    for css_path in css_list:
        print 'Compressing', css_path
        os.system("python -m csscompressor -o " + css_path + " " + css_path)
    # 开始处理js文件
    for js_path in compressed_js_list:
        print 'Compiling', root_path+str(js_path)
        os.system("java -jar "+root_path+"/java/closure.jar --js " + root_path+str(js_path) + " --js_output_file " + root_path+str(js_path).replace(".js", ".compress.js"))
        os.system("mv " + root_path+str(js_path).replace(".js", ".compress.js") + " " + root_path+str(js_path))
    os.popen("rm -if "+root_path+"/build/static.tar.gz")
    os.popen("rm -if "+root_path+"/build/project_src.tar.gz")
    os.popen("rm -if "+root_path+"/build/project_pyc.tar.gz")
    time.sleep(1)
    pyc_dir_list = []
    src_dir_list = []
    sta_dir_list = []
    for root, dirs, files in os.walk(path):
        for file_name in files:
            file_full_path = root+'/'+file_name
            judge = '.idea' in file_full_path \
                    or 'zzz-config.py' in file_full_path \
                    or '.svn' in file_full_path \
                    or '/test/' in file_full_path \
                    or '/depends/' in file_full_path
            if judge:
                continue
            elif '.idea' in file_full_path:
                continue
            # elif "dc/" in file_full_path:
            #     continue
            elif file_full_path.endswith('/build/project_build/config.py'):
                content = open(''+root_path+'/build/project_build/config.py', 'rb').read()
                fp = open(''+root_path+'/build/project_build/config.py', 'w+')
                fp.write(content.replace('DEBUG = True', 'DEBUG = False'))
                fp.close()
                py_compile.compile(file_full_path)
                pyc_dir_list.append(file_full_path[2:len(file_full_path)]+'c')
                src_dir_list.append(file_full_path[2:len(file_full_path)])
            elif 'static' in file_full_path:
                sta_dir_list.append(file_full_path[2:len(file_full_path)])
                pyc_dir_list.append(file_full_path[2:len(file_full_path)])
                src_dir_list.append(file_full_path[2:len(file_full_path)])
                continue
            elif file_full_path.endswith('.py'):
                py_compile.compile(file_full_path)
                pyc_dir_list.append(file_full_path[2:len(file_full_path)]+"c")
                src_dir_list.append(file_full_path[2:len(file_full_path)])
            else:
                pyc_dir_list.append(file_full_path[2:len(file_full_path)])
                if ".pyc" not in file_full_path:
                    src_dir_list.append(file_full_path[2:len(file_full_path)])
    pyc_dir_list = list(set(pyc_dir_list))
    src_dir_list = list(set(src_dir_list))
    sta_dir_list = list(set(sta_dir_list))
    pyc_dir_list.sort()
    src_dir_list.sort()
    sta_dir_list.sort()
    file_name1 = ""+root_path+"/build/web/project_pyc.tar.gz"
    file_name2 = ""+root_path+"/build/web/project_src.tar.gz"
    file_name3 = ""+root_path+"/build/web/static.tar.gz"
    mode = 'w:gz'
    pyc_file_tar = tarfile.open(file_name1, mode)
    for path in pyc_dir_list:
        if "tar.gz" in path:
            continue
        arc_name = str(path).replace("build/project_build", "")
        pyc_file_tar.add(path, arcname=arc_name)
    pyc_file_tar.close()
    src_file_tar = tarfile.open(file_name2, mode)
    for path in src_dir_list:
        if "tar.gz" in path:
            continue
        arc_name = str(path).replace("build/project_build", "")
        src_file_tar.add(path, arcname=arc_name)
    src_file_tar.close()
    sta_file_tar = tarfile.open(file_name3, mode)
    for path in sta_dir_list:
        if "tar.gz" in path:
            continue
        arc_name = str(path).replace("build/project_build", "")
        sta_file_tar.add(path, arcname=arc_name)
    sta_file_tar.close()
    
    print "Packaging compiled"