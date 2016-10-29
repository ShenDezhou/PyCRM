.. _index:



----------------------------------------------------------------
安装与配置
----------------------------------------------------------------


所有服务器的配置均为云系统中的Ubuntu 12.04的实例. 


Web服务器
================================================================

提供静态资源服务和负载均衡

安装Nginx
----------------------------------------------------------------

::
    
    sudo apt-get install nginx


配置Nginx处理转发和静态资源服务
----------------------------------------------------------------

::

    sudo vi /etc/nginx/nginx.conf

/marsweb/conf/nginx.conf 是例子. 

::

    upstream frontends {
            server 192.168.180.110:8888;
            server 192.168.180.110:8889;
            server 192.168.180.110:8890;
            server 192.168.180.110:8891;
    }

:: 

     server {
            listen 80;

            # Allow file uploads
            client_max_body_size 10M;

            location /static/ {
                     #   auth_basic off;
                    root /var/marsweb/web/;
                    if ($query_string) {
                            expires max;
                    }
            }
            location = /favicon.ico {
                    rewrite (.*) /static/favicon.ico;
            }
            location = /robots.txt {
                    rewrite (.*) /static/robots.txt;
            }


            location / {
                    #auth_basic "test_login";
                    #auth_basic_user_file /var/marsweb/htpasswd;
                    proxy_pass_header Server;
                    proxy_set_header Host $http_host;
                    proxy_redirect off;
                    proxy_set_header X-Real-IP $remote_addr;
                    proxy_set_header X-Scheme $scheme;
                    proxy_pass http://frontends;
            }
    }


重启Nginx
----------------------------------------------------------------

::
    
    sudo service nginx restart


部署静态资源到Nginx
----------------------------------------------------------------

::

    sudo mkdir /var/marsweb/

    sudo mkdir /var/marsweb/web/

    sudo chmod 755 -R /var/marsweb/

    sudo cp -R /home/ubuntu/static/ /var/marsweb/web/


采用Nginx模块实现文件上传和下载
----------------------------------------------------------------

1. 下载nginx 、pcre、zlib、nginx_upload_module-2.2.0

已经下载到

::
    
    demos/libs/nginx

2. 把下载的pcre、zlib、nginx_upload_module-2.2.0解压后都放到nginx解压后的主目录下

3. 修改.c文件

经过几次测试 用nginx-1.4.7 和 nginx-1.6.1 配合安装 nginx_upload_module-2.2.0 全部安装失败好像是不兼容

最后降到 nginx-1.3.0, 又改了 nginx_upload_module-2.2.0/ngx_http_upload_module.c

::

    //int          result;
    __attribute__((__unused__)) int result;    


4. 在nginx的解压目录下运行

::

    sudo ./configure --prefix=/usr --with-http_ssl_module --with-zlib=zlib-1.2.8 --with-pcre=pcre-8.32  --add-module=nginx_upload_module-2.2.0 --add-module=naxsi-master/naxsi_src

    make

    sudo make install

5. 更新nginx配置文件

::

    /usr/local/nginx/conf/nginx.conf


6. 建立临时目录

::

    /var/marsfile-sheets/tmp/mars/0 到 /var/marsfile-sheets/tmp/mars/9

    /var/marsfile-sheets/tmp/mars-state/0 到 /var/marsfile-sheets/tmp/mars-state/9

    chmod 777 /var/marsfile-sheets/tmp/ -R


7. 重启nginx服务


:: 

    service nginx restart


http://www.greenacorn-websolutions.com/nginx/securing-your-app-with-nginx-naxsi.php


利用Nginx限制后台目录访问
----------------------------------------------------------------

在Nginx的conf目录操作，例如：

::

    /usr/local/nginx/conf

::

    sudo apt-get install apache2-utils

    htpasswd -b -c admin_passwd marsweb 18911631389


::

    location ~ ^(/acm|/rest/mgr) {
        #if ($remote_addr = "106.37.18.107") {
        #   rewrite ^ /404;
        #}
        #allow 192.168.1.114;
        #allow 219.143.135.199;
        #allow 172.16.128.0/24;
        #deny all;
        auth_basic "auth";
        auth_basic_user_file admin_passwd;
        proxy_pass_header Server;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_pass http://frontends;
    }


应用服务器和计算节点服务器
================================================================

应用服务器和计算节点服务器共享相同的安装和部署步骤, 但运行方式不同

安装Python
----------------------------------------------------------------

::

    sudo apt-get install python-pip python-dev build-essential

    sudo pip install --upgrade pip 

    sudo pip install --upgrade virtualenv 

安装Git
----------------------------------------------------------------

::

    sudo apt-get install git


安装tornado
----------------------------------------------------------------

必须从git安装新版tornado, 否则AsyncTorndb会出错

::

    sudo pip install -Iv https://github.com/tornadoweb/tornado/archive/v4.0.0b1.tar.gz


安装tornado访问MySQL的异步Driver
----------------------------------------------------------------

官网: https://github.com/mayflaver/AsyncTorndb

::

    sudo pip install git+https://github.com/mayflaver/AsyncTorndb.git


安装tornado-celery的Driver
----------------------------------------------------------------

::

    sudo pip install tornado-celery


安装tornadomail发送邮件包
----------------------------------------------------------------

::

    sudo pip install git+https://github.com/equeny/tornadomail.git


安装Excel读取模块
----------------------------------------------------------------

::

    sudo pip install openpyxl

    sudo pip install xlrd


安装写Excel的包
----------------------------------------------------------------

::
    
    sudo pip install xlutils
    
    sudo pip install xlwt



安装ujson
----------------------------------------------------------------

::

    sudo pip install ujson


安装qrcode
----------------------------------------------------------------

::

    sudo pip install qrcode


短网址工具包
----------------------------------------------------------------

::

    sudo pip install short_url


安装mysqldb的driver
----------------------------------------------------------------

::

    sudo apt-get install python-mysqldb


安装torndb
----------------------------------------------------------------

这是同步连接MySQL的driver.

::

    sudo pip install torndb

安装pycrypto
----------------------------------------------------------------

::

    pip install pycrypto


安装Image
----------------------------------------------------------------

sudo apt-get install python-imaging


安装Redis的driver
----------------------------------------------------------------

与缓存服务器Redis server连接. 

::

    sudo pip install redis



NFS Client端安装和配置
----------------------------------------------------------------

使用共享的网络磁盘. 


1. 安装nfs client

::

    sudo apt-get install nfs-common

2. 查看nfs server上共享的目录

*先安装好NFS网络硬盘服务器*

::

    showmount -e 192.168.180.150

3. 创建共享挂载点，并执行挂载

::

    sudo mkdir /var/marsfile-sheets
    sudo chmod 777 -R /var/marsfile-sheets

    sudo mount -t nfs 192.168.180.150:/var/marsfile-sheets /var/marsfile-sheets

    注意:重启服务器后可能不会自动mount 请手动mount nfs

4. 修改/etc/fstab文件(*)

::

    192.168.35.17:/data3/nfsroot/data3/nfsroot nfs defaults 0 0

    10.122.72.36:/var/marsfile-sheets /var/marsfile-sheets nfs defaults 0 0


安装rarfile
----------------------------------------------------------------

::

    sudo pip install rarfile

    sudo apt-get install unrar


安装Java
----------------------------------------------------------------

::

    sudo apt-get install openjdk-6-jdk


安装pyjnius
----------------------------------------------------------------

A Python module to access Java classes as Python classes using JNI.

::

    sudo pip install cython
	
	sudo pip install git+https://github.com/kivy/pyjnius

	
安装supervisor 
----------------------------------------------------------------

用来将tornado和celer task作为后台运行的service, 并且遇到问题重启

::

    sudo pip install supervisor


例子:

::

    ; ==================================
    ; celery worker supervisor 
    ; ==================================

    [program:marsweb8888]
    ; Set full path to celery program if using virtualenv
    command=python /var/marsweb/index.py --port=8888
    directory=/var/marsweb/
    user=nobody
    numprocs=1
    stdout_logfile=/var/log/supervisord/marsweb_8888.log
    stderr_logfile=/var/log/supervisord/marsweb_8888.log
    autostart=true
    autorestart=true
    startsecs=10
    ; Need to wait for currently executing tasks to finish at shutdown.
    ; Increase this if you have very long running tasks.
    stopwaitsecs = 600
    ; When resorting to send SIGKILL to the program to terminate it
    ; send SIGKILL to its whole process group instead,
    ; taking care of its children as well.
    killasgroup=true
    ; if rabbitmq is supervised, set its priority higher
    ; so it starts first
    priority=998
    stdout_logfile_maxbytes = 20MB
    stdoiut_logfile_backups = 20


配置文件在

::

    /var/marsweb/web/app-serverd.conf

::

    /var/marsweb/web/task-workerd.conf

配置service supervisord restart

http://notebk.sinaapp.com/topic/39/%E6%8A%8Asupervisord-%E5%8A%A0%E5%85%A5ubuntu%E7%B3%BB%E7%BB%9F%E6%9C%8D%E5%8A%A1


部署可执行程序
----------------------------------------------------------------

将代码包复制到 

::

    sudo cp -R /home/ubnutu/marsweb/ /var/marsweb/web/

    sudo chomod 755 -R /var/marsweb/


运行应用服务器
----------------------------------------------------------------


全部运行

::

    sudo supervisord -c /var/marsweb/web/supervisord.conf


::

    sudo supervisord -c /var/marsweb/web/app-serverd.conf


如果想单独运行(不带supervisord), 请运行:

::
    
    cd /var/marsweb/web/

    python index.py --port=8888
    

运行计算节点服务器
----------------------------------------------------------------

::

    sudo supervisord -c /var/marsweb/web/task-workerd.conf

如果想单独运行(不带supervisord), 请运行:

::
    
    cd /var/marsweb/web/

    celery worker -A tasks


缓存服务器
================================================================


安装Redis Server
----------------------------------------------------------------

::

    sudo apt-get install redis-server

/etc/redis/redis.conf 注释掉下面一行:

::

    # bind 127.0.0.1


restart

::

    /etc/init.d/redis-server restart


任务调度服务器
================================================================

安装RabbitMQ Server
----------------------------------------------------------------

::

    sudo apt-get install rabbitmq-server


数据库服务器
================================================================


安装MySQL
----------------------------------------------------------------

::

    sudo apt-get install mysql-server mysql-client

可使用Oracle的MySQLWorkbench连接使用MySQL(可以选SSH方式)


在mysql里面建一个数据库, 名为 marsweb, 编码为UTF-8.

将备份文件导入.


::

    sudo vi /etc/mysql/my.cnf

修改绑定地址为任意IP

::

    bind-address = 0.0.0.0

max_connections        = 2000
group_concat_max_len = 4294967295
wait_timeout=2147483
interactive_timeout=2147483

授权其他server能访问MySQL

::

    grant all PRIVILEGES on *.* to root@'192.168.180.110' identified by 'asiencredit';

    GRANT ALL PRIVILEGES ON *.* TO root@'%' IDENTIFIED BY 'root';   
    FLUSH PRIVILEGES; 


设置并发量支持为1000

::

    set GLOBAL max_connections = 1000


重启MySQL

::

    sudo restart mysql


采用青云的RDB MySQL
----------------------------------------------------------------

可自动主从节点和备份. 直接连接. 

192.168.180.6/5


网络存储服务器
================================================================

采用NFS做网络存储服务. 

NFS Server端的安装和配置如下:

安装nfs server
----------------------------------------------------------------

::

    sudo apt-get install nfs-kernel-server nfs-common


设置nfs共享目录
----------------------------------------------------------------

::

    sudo vim /etc/exports

在文件末尾添加一行

::

    /var/marsfile-sheets      *(rw,sync)     

::

    sudo mkdir /var/marsfile-sheets

    sudo chmod 777 -R /var/marsfile-sheets


重启nfs server
----------------------------------------------------------------

::

    sudo service nfs-kernel-server restart


pip install numpy


pip install requests

pip install selenium

pip install beautifulsoup4

pip install wechat_sdk

pip install tormysql

pip install jinja2

pip install python-docx

apt-get install python-lxml

pip install  pyquery

### sudo pip install -i http://pypi.douban.com/simple/ saltTesting

----------------------------------------------------------------
发布与运行
----------------------------------------------------------------

本机编译和发布
================================================================

在本机上安装sshpass
----------------------------------------------------------------

::

    apt-get install sshpass

运行自动编译和发布命令
----------------------------------------------------------------

::

    ./web/build/auto_deploy_local.sh ./web
