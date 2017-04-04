一键安装:
sudo apt-get update
sudo apt-get install python-pip python-dev build-essential git python-mysqldb unrar openjdk-8-jdk redis-server mysql-server  mysql-client sshpass  
sudo pip install Cython
sudo pip install openpyxl xlrd xlutils xlwt ujson qrcode short_url torndb pycrypto redis rarfile supervisor -Iv https://github.com/tornadoweb/tornado/archive/v4.4.3.tar.gz git+https://github.com/mayflaver/AsyncTorndb.git git+https://github.com/equeny/tornadomail.git git+https://github.com/kivy/pyjnius.git
sudo pip install numpy requests pinyin urllib datetime pillow wechatpy wechat_sdk selenium bs4
curl -O https://raw.githubusercontent.com/ShenDezhou/PyCRM/master/sql/marsapp.sql
mysql -uroot -pwwwsto < marsapp.sql
set GLOBAL sql_mode='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION';
set GLOBAL max_connections = 1000
service mysql restart
mkdir /var/local/marsapp
git clone https://github.com/ShenDezhou/PyCRM.git
ln -s /var/local/marsapp /search
supervisord -c /search/conf/supervisord.conf

文件系统:
/var文件系统 
　　/var 包括系统一般运行时要改变的数据.每个系统是特定的，即不通过网络与其他计算机共享.  

/var/catman   
　　当要求格式化时的man页的cache.man页的源文件一般存在/usr/man/man* 中；有些man页可能有预格式化的版本，存在/usr/man/cat* 中.而其他的man页在第一次看时需要格式化，格式化完的版本存在/var/man 中，这样其他人再看相同的页时就无须等待格式化了. (/var/catman 经常被清除，就象清除临时目录一样.)  

/var/lib   
　　系统正常运行时要改变的文件.  

/var/local   
　　/usr/local 中安装的程序的可变数据(即系统管理员安装的程序).注意，如果必要，即使本地安装的程序也会使用其他/var 目录，例如/var/lock .  

/var/lock   
　　锁定文件.许多程序遵循在/var/lock 中产生一个锁定文件的约定，以支持他们正在使用某个特定的设备或文件.其他程序注意到这个锁定文件，将不试图使用这个设备或文件.  

/var/log   
　　各种程序的Log文件，特别是login  (/var/log/wtmp log所有到系统的登录和注销) 和syslog (/var/log/messages 里存储所有核心和系统程序信息. /var/log 里的文件经常不确定地增长，应该定期清除.  

/var/run   
　　保存到下次引导前有效的关于系统的信息文件.例如， /var/run/utmp 包含当前登录的用户的信息. 

/var/spool   
　　mail, news, 打印队列和其他队列工作的目录.每个不同的spool在/var/spool 下有自己的子目录，例如，用户的邮箱在/var/spool/mail 中.  

/var/tmp   
　　比/tmp 允许的大或需要存在较长时间的临时文件. (虽然系统管理员可能不允许/var/tmp 有很旧的文件.)  

::supervisor:

[unix_http_server]
file=/tmp/supervisor.sock   ; (the path to the socket file)
;chmod=0700                 ; socket file mode (default 0700)
;chown=nobody:nogroup       ; socket file uid:gid owner
;username=user              ; (default is no username (open server))
;password=123               ; (default is no password (open server))

;[inet_http_server]         ; inet (TCP) server disabled by default
;port=127.0.0.1:9001        ; (ip_address:port specifier, *:port for all iface)
;username=user              ; (default is no username (open server))
;password=123               ; (default is no password (open server))

[supervisord]
logfile=/tmp/supervisord.log ; (main log file;default $CWD/supervisord.log)
logfile_maxbytes=50MB        ; (max main logfile bytes b4 rotation;default 50MB)
logfile_backups=10           ; (num of main logfile rotation backups;default 10)
loglevel=info                ; (log level;default info; others: debug,warn,trace)
pidfile=/var/run/supervisord.pid ; (supervisord pidfile;default supervisord.pid)
nodaemon=false               ; (start in foreground if true;default false)
minfds=1024                  ; (min. avail startup file descriptors;default 1024)
minprocs=200                 ; (min. avail process descriptors;default 200)
;umask=022                   ; (process file creation umask;default 022)
;user=chrism                 ; (default is current user, required if root)
;identifier=supervisor       ; (supervisord identifier, default is 'supervisor')
;directory=/tmp              ; (default is not to cd during start)
;nocleanup=true              ; (don't clean up tempfiles at start;default false)
;childlogdir=/tmp            ; ('AUTO' child log dir, default $TEMP)
;environment=KEY="value"     ; (key value pairs to add to environment)
;strip_ansi=false            ; (strip ansi escape codes in logs; def. false)

; the below section must remain in the config file for RPC
; (supervisorctl/web interface) to work, additional interfaces may be
; added by defining them in separate rpcinterface: sections
[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix:///tmp/supervisor.sock ; use a unix:// URL  for a unix socket

; ==================================
; app-server superviord
; ==================================

[program:marsweb8890]
command=python /search/index.py --port=8890
directory=/search/
user=root
numprocs=1
redirect_stderr=false		; redirect proc stderr to stdout (default false)
stdout_logfile=/var/log/marsweb_std.log
stderr_logfile=/var/log/marsweb_error.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs = 600
killasgroup=true
priority=998
stdout_logfile_maxbytes = 20MB
stdoiut_logfile_backups = 20

[program:marsweb8891]
command=python /search/index.py --port=8891
directory=/search/
user=root
numprocs=1
redirect_stderr=false        ; redirect proc stderr to stdout (default false)
stdout_logfile=/var/log/marsweb_std.log
stderr_logfile=/var/log/marsweb_error.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs = 600
killasgroup=true
priority=998
stdout_logfile_maxbytes = 20MB
stdoiut_logfile_backups = 20

[program:marsweb8892]
command=python /search/index.py --port=8892
directory=/search/
user=root
numprocs=1
redirect_stderr=false        ; redirect proc stderr to stdout (default false)
stdout_logfile=/var/log/marsweb_std.log
stderr_logfile=/var/log/marsweb_error.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs = 600
killasgroup=true
priority=998
stdout_logfile_maxbytes = 20MB
stdoiut_logfile_backups = 20

[program:marsweb8893]
command=python /search/index.py --port=8893
directory=/search/
user=root
numprocs=1
redirect_stderr=false        ; redirect proc stderr to stdout (default false)
stdout_logfile=/var/log/marsweb_std.log
stderr_logfile=/var/log/marsweb_error.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs = 600
killasgroup=true
priority=998
stdout_logfile_maxbytes = 20MB
stdoiut_logfile_backups = 20

[program:marsweb8894]
command=python /search/index.py --port=8894
directory=/search/
user=root
numprocs=1
redirect_stderr=false        ; redirect proc stderr to stdout (default false)
stdout_logfile=/var/log/marsweb_std.log
stderr_logfile=/var/log/marsweb_error.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs = 600
killasgroup=true
priority=998
stdout_logfile_maxbytes = 20MB
stdoiut_logfile_backups = 20

[program:marsweb8895]
command=python /search/index.py --port=8895
directory=/search/
user=root
numprocs=1
redirect_stderr=false        ; redirect proc stderr to stdout (default false)
stdout_logfile=/var/log/marsweb_std.log
stderr_logfile=/var/log/marsweb_error.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs = 600
killasgroup=true
priority=998
stdout_logfile_maxbytes = 20MB
stdoiut_logfile_backups = 20

[program:marsweb8896]
command=python /search/index.py --port=8896
directory=/search/
user=root
numprocs=1
redirect_stderr=false        ; redirect proc stderr to stdout (default false)
stdout_logfile=/var/log/marsweb_std.log
stderr_logfile=/var/log/marsweb_error.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs = 600
killasgroup=true
priority=998
stdout_logfile_maxbytes = 20MB
stdoiut_logfile_backups = 20

[program:marsweb8897]
command=python /search/index.py --port=8897
directory=/search/
user=root
numprocs=1
redirect_stderr=false        ; redirect proc stderr to stdout (default false)
stdout_logfile=/var/log/marsweb_std.log
stderr_logfile=/var/log/marsweb_error.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs = 600
killasgroup=true
priority=998
stdout_logfile_maxbytes = 20MB
stdoiut_logfile_backups = 20

[program:marsweb8898]
command=python /search/index.py --port=8898
directory=/search/
user=root
numprocs=1
redirect_stderr=false        ; redirect proc stderr to stdout (default false)
stdout_logfile=/var/log/marsweb_std.log
stderr_logfile=/var/log/marsweb_error.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs = 600
killasgroup=true
priority=998
stdout_logfile_maxbytes = 20MB
stdoiut_logfile_backups = 20

[program:marsweb8899]
command=python /search/index.py --port=8899
directory=/search/
user=root
numprocs=1
redirect_stderr=false       ; redirect proc stderr to stdout (default false)
stdout_logfile=/var/log/marsweb_std.log
stderr_logfile=/var/log/marsweb_error.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs = 600
killasgroup=true
priority=998
stdout_logfile_maxbytes = 20MB
stdoiut_logfile_backups = 20

::nginx:

user www-data;
worker_processes  4;
pid /var/run/nginx.pid; 

events {
    worker_connections 1024;
#    use epoll;
}


http {

    upstream frontends {
        server 114.215.129.145:8890;
        server 114.215.129.145:8891;
        server 114.215.129.145:8892;
        server 114.215.129.145:8893;
        server 114.215.129.145:8894;
        server 114.215.129.145:8895;
        server 114.215.129.145:8896;
        server 114.215.129.145:8897;
        server 114.215.129.145:8898;
        server 114.215.129.145:8899;
    }

    server_names_hash_bucket_size 64;
    include       mime.types;
    default_type  application/octet-stream;
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    sendfile       on;
    tcp_nopush     on;
    tcp_nodelay    on;
    
    keepalive_timeout  60;
    types_hash_max_size 2048;

    ##
    # Gzip Settings
    ##
  
    gzip on;
    gzip_disable "msie6";
 
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_buffers 16 8k;
    gzip_http_version 1.1;
    gzip_types text/plain text/css application/json application/x-javascript text/xml application/xml application/xml+rss text/javascript;


    # Only retry if there was a communication error, not a timeout
    # on the Tornado server (to avoid propagating "queries of death"
    # to all frontends)
    #proxy_next_upstream error;

    #---http config ---
    server {
        listen       80;
        client_max_body_size 100M;
        server_name wwwsto.com;        
        location  /static/ {
            root /var/local/marsapp/;
            expires max;
        }
        location = /favicon.ico {

            rewrite (.*) /static/favicon.ico;
        }
        location = /robots.txt {
            rewrite (.*) /static/robots.txt;
        }
   
        location /filedownload/ {
            internal;   
            limit_rate 2000k; 
            alias /var/marsfile-sheets;
            error_page 404 =200 @backend; 
        }
           
        location @backend {
            rewrite ^/filedownload/(.*)$  /filedownloadbynginx/$1;  
            proxy_pass http://frontends;  
            proxy_redirect  off;  
            proxy_set_header  Host $host;  
            proxy_set_header  X-Real-IP $remote_addr;  
            proxy_set_header  X-Forwarded-For $proxy_add_x_forwarded_for;  
        }  

        location /assets/ {
            internal;   
            limit_rate 2000k; 
            alias /var/local/marsapp/static/;
            error_page 404 =200 @backend_assets; 
        }
           
        location @backend_assets {
            rewrite ^/assets/(.*)$  /filedownloadbynginx/$1;  
            proxy_pass http://frontends;  
            proxy_redirect  off;  
            proxy_set_header  Host $host;  
            proxy_set_header  X-Real-IP $remote_addr;  
            proxy_set_header  X-Forwarded-For $proxy_add_x_forwarded_for;  
        }
  
	location / {
                proxy_pass_header Server;
                proxy_set_header Host $http_host;
                proxy_redirect off;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Scheme $scheme;
                proxy_pass http://frontends;
        }

    }

}

::crontab:

00 00  * * * truncate --size 0 /var/log/marsweb_std.log
* * * * 1 truncate --size 0 /var/log/nginx/error.log
* * * * 1 truncate --size 0 /var/log/nginx/access.log


