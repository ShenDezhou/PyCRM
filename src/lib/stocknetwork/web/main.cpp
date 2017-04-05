/*
Copyright (c) 2017-2018 Dezhou Shen, Sogou Inc.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/

#include <string.h>
#include <signal.h>
#include <mcheck.h>
#include <iconv.h>
#include <netinet/tcp.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <memory>

#include "ace/OS_NS_string.h"
#include "ace/OS_NS_sys_stat.h"
#include "ace/Message_Block.h"
#include "ace/INET_Addr.h"
#include "ace/SOCK_Acceptor.h"
#include "ace/SOCK_Stream.h"
#include "ace/Auto_Ptr.h"

static const int no_delay = 1;
static const long PAGESIZE = 4096;
/* Converts a hex character to its integer value */
inline char from_hex(char ch) {
  return isdigit(ch) ? ch - '0' : tolower(ch) - 'a' + 10;
}

/* Converts an integer value to its hex character*/
inline char to_hex(char code) {
  static char hex[] = "0123456789abcdef";
  return hex[code & 15];
}

/* Returns a url-encoded version of str */
/* IMPORTANT: be sure to free() the returned string after use */
inline char *url_encode(char *str) {
  mtrace();
  char *pstr = str, *buf = reinterpret_cast<char*>(malloc(strlen(str) * 3 + 1)), *pbuf = buf;
  while (*pstr) {
    if (isalnum(*pstr) || *pstr == '-' || *pstr == '_' || *pstr == '.' || *pstr == '~') 
      *pbuf++ = *pstr;
    else if (*pstr == ' ') 
      *pbuf++ = '+';
    else 
      *pbuf++ = '%', *pbuf++ = to_hex(*pstr >> 4), *pbuf++ = to_hex(*pstr & 15);
    pstr++;
  }
  *pbuf = '\0';
  mtrace();
  return buf;
}

/* Returns a url-decoded version of str */
/* IMPORTANT: be sure to free() the returned string after use */
inline char *url_decode(char *str) {
  mtrace();
  char *pstr = str, *buf = reinterpret_cast<char*>(malloc(strlen(str) + 1)), *pbuf = buf;
  while (*pstr) {
    if (*pstr == '%') {
      if (pstr[1] && pstr[2]) {
        *pbuf++ = from_hex(pstr[1]) << 4 | from_hex(pstr[2]);
        pstr += 2;
      }
    } else if (*pstr == '+') { 
      *pbuf++ = ' ';
    } else {
      *pbuf++ = *pstr;
    }
    pstr++;
  }
  *pbuf = '\0';
  mtrace();
  return buf;
}

const char* getMimeType(const char* fileName)
{
    mtrace();
    const char* extPos = strrchr(fileName,'.');
    const char* extension;
    const char* mimeType = "text/plain, charset=us-ascii";

    if (extPos == NULL){
        extension =  "";
    }else{
        extension = extPos + 1;
    }

    /* Compare and return mimetype */
    switch(extension[0]){
        case 'b':
            if (strncmp(extension, "bmp", 3) == 0)
                mimeType =  "image/bmp";
            if (strncmp(extension, "bin", 3) == 0)
                mimeType =  "application/octet-stream";

            break;
        case 'c':
            if (strncmp(extension, "csh", 3) == 0)
                mimeType =  "application/csh";
            if (strncmp(extension, "css", 3) == 0)
                mimeType =  "text/css";

            break;
        case 'd':
            if (strncmp(extension, "doc", 3) == 0)
                mimeType =  "application/msword";
            if (strncmp(extension, "dtd", 3) == 0)
                mimeType =  "application/xml-dtd";
            break;
        case 'e':
            if (strncmp(extension, "exe", 3) == 0)
                mimeType =  "application/octet-stream";
            break;
        case 'h':
            if (strncmp(extension, "html", 4) == 0 || strncmp(extension, "htm", 3) == 0)
                mimeType =  "text/html";
            break;
        case 'i':
            if (strncmp(extension, "ico", 3) == 0)
                mimeType =  "image/x-icon";
            break;
        case 'g':
            if (strncmp(extension, "gif", 3) == 0)
                mimeType =  "image/gif";
            break;
        case 'j':
            if (strncmp(extension, "jpeg", 4) == 0 || strncmp(extension, "jpg", 3) == 0)
                mimeType =  "image/jpeg";
            break;
        case 'l':
            if (strncmp(extension, "latex", 5) == 0)
                mimeType =  "application/x-latex";
            break;
        case 'p':
            if (strncmp(extension, "png", 3) == 0)
                mimeType =  "image/png";
            if (strncmp(extension, "pgm", 3) == 0)
                mimeType =  "image/x-portable-graymap";
            break;  
        case 'r':
            if (strncmp(extension, "rtf", 3) == 0)
                mimeType  =  "text/rtf";
            break;
        case 's':
            if (strncmp(extension, "svg", 3) == 0)
                mimeType =  "image/svg+xml";
            if (strncmp(extension, "sh", 2) == 0)
                mimeType =  "application/x-sh";
            break;
        case 't':
            if (strncmp(extension, "tar", 3) == 0)
                mimeType =  "application/x-tar";
            if (strncmp(extension, "tex", 3) == 0)
                mimeType =  "application/x-tex";
            if (strncmp(extension, "tif", 3) == 0 || strncmp(extension, "tiff", 4) == 0)
                mimeType =  "image/tiff";
            if (strncmp(extension, "txt", 3) == 0)
                mimeType =  "text/plain";
            break;
        case 'u':
            if (strncmp(extension, "utf8", 4) == 0)
                mimeType =  "text/plain, charset=utf8";
            break;
        case 'x':
            if (strncmp(extension, "xml", 3) == 0)
                mimeType =  "application/xml";
            break;
        default:
            break;
    }
    mtrace();
    return mimeType;
}

#ifndef BOOST_AUTO_TEST_MAIN
int
ACE_TMAIN (int argc, ACE_TCHAR *argv[]) {
    mtrace();
    signal(SIGPIPE, SIG_IGN);

    ACE_INET_Addr server_addr;
    ACE_SOCK_Acceptor acceptor;
    ACE_SOCK_Stream peer;
    int buffer_size = 2048;
    
    int port = 80;
    if (argc>1) {
        ACE::write_n(ACE_STDOUT,argv[1],strlen(argv[1]));
        port = atoi(argv[1]);
    }
    if (server_addr.set(port) == -1) {
        ACE::write_n(ACE_STDOUT,"Fail to set port: 80",13);
        return 1;
    }
    if (acceptor.open(server_addr) == -1) {
        ACE::write_n(ACE_STDOUT,"Fail to open server_addr",24);
        goto acceptor_error;
    }
    for (;;) {
        ACE::write_n(ACE_STDOUT,"waiting to connect",18);
        if (acceptor.accept(peer) == -1)
            goto acceptor_error;
        // strace shows next line is of no use.
        peer.disable(ACE_NONBLOCK);
        // disable Nagle's Algorithm (Ste93).
        peer.set_option(ACE_IPPROTO_TCP,TCP_NODELAY,
                        (void*)&no_delay,sizeof(int));
        ACE_Message_Block mb (buffer_size);
        char *head = mb.rd_ptr();
        for (;;) {
            // ACE::write_n(ACE_STDOUT,"waiting to recv",15);
            // recv data
            int result = peer.recv (mb.wr_ptr (),
                                    buffer_size-(mb.wr_ptr ()-mb.rd_ptr ()));
            if (result > 0) {
                mb.wr_ptr (result);
                ACE::write_n(ACE_STDOUT, mb.wr_ptr() - result, result);
                if (ACE_OS::strchr (mb.rd_ptr (), '\n') > 0) {
                    if (ACE_OS::strncmp(mb.rd_ptr(), "GET", 3) == 0) {
                        mb.rd_ptr (4);
                        head = mb.rd_ptr ();
                        char* ptr = ACE_OS::strchr (head, ' ');
                        *ptr = '\0';
                        
                        char* filename = 0;
                        // remove / to make file under current folder
                        filename = ACE_OS::strdup (head + 1);
                        std::unique_ptr<char> auto_filename (filename);
                        ACE::write_n(ACE_STDOUT, (const char *)filename, ptr - head - 1);
                        ACE::write_n(ACE_STDOUT, "\n", 1);
                        char* dec_filename = url_decode(filename);
                        std::unique_ptr<char> auto_url_decode (dec_filename);
                        char* sec_dec_filename = url_decode(dec_filename);
                        std::unique_ptr<char> auto_sec_dec_filename (sec_dec_filename);
                        ACE::write_n(ACE_STDOUT, (const char *)sec_dec_filename, strlen(sec_dec_filename));
                        filename = sec_dec_filename;
                        
                        // Is this a query?
                        if (strchr(filename,'?') != NULL) {
                            ACE::write_n(ACE_STDOUT, "it is a query", 13);
                            ACE::write_n(ACE_STDOUT, (const char *)filename, strlen(filename));
                            
                            // append?file=xxx/yyy/zz&key=value&key2=value2
                            if (strncmp(filename,"append",6) == 0) {
                                ACE::write_n(ACE_STDOUT, "append request", 14);
                                char* keyvalue = strchr(filename,'?');
                                
                                // skep ? mark
                                keyvalue = keyvalue + 1;
                                ACE_HANDLE handle = ACE_INVALID_HANDLE;
                                for (;;) {
                                    char* key = keyvalue;
                                    char* value = strchr(keyvalue,'=');
                                    *value = '\0';
                                    value = value + 1;
                                    if (strchr(value,'&') == NULL) {
                                        // Is this key value last one?
                                        keyvalue = NULL;

                                    } else {
                                        keyvalue = strchr(value,'&');
                                        *keyvalue = '\0';
                                        keyvalue = keyvalue + 1;
                                    }
                                    ACE_OS::write_n (ACE_STDOUT, "\n", 1);
                                    ACE_OS::write_n (ACE_STDOUT, key, strlen(key));
                                    ACE_OS::write_n (ACE_STDOUT, ",", 1);
                                    ACE_OS::write_n (ACE_STDOUT, value, strlen(value));
                                    ACE_OS::write_n (ACE_STDOUT, "\n", 1);
                                    
                                    if ( strncmp(key, "file", 4) == 0) {
                                        char* appendfile = value;
                                        ACE_stat stat;
                                        // Can we stat the file?
                                        if (ACE_OS::stat (appendfile, &stat) == -1) {
                                            ACE::write_n(ACE_STDOUT,"stat fail",9);
                                            goto file_error;
                                        }
                                        ssize_t size = stat.st_size;
                                        // Can we open the file?
                                        handle = ACE_OS::open (appendfile, O_CREAT | O_RDWR | O_APPEND);
                                        if (handle == ACE_INVALID_HANDLE) {
                                            ACE::write_n(ACE_STDOUT,"open fail",9);
                                            goto file_error;
                                        }
                                    } else {
                                        // Can we write the file?
                                        if (handle == ACE_INVALID_HANDLE) {
                                            ACE::write_n(ACE_STDOUT,"write fail",9);
                                            goto file_error;
                                        }
                                        ACE_OS::write_n (handle, value, strlen(value));
                                        
                                        if (keyvalue != NULL) {
                                            ACE_OS::write_n (handle, "\t", 1);
                                        }

                                        // ACE_OS::write_n (ACE_STDOUT, value, strlen(value));
                                        // ACE_OS::write_n (ACE_STDOUT, "\t", 1);                                        
                                    }

                                    // Is there more keyvalue?
                                    if (keyvalue == NULL) {
                                        ACE_OS::write_n (handle, "\n", 1);
                                        goto file_error;
                                    }
                                } // end for
                            file_error:
                                if (handle != ACE_INVALID_HANDLE) {
                                    ACE_OS::close(handle);
                                }
                                peer.send_n("HTTP/1.0 200 OK\n", 16);
                                ACE::write_n(ACE_STDOUT,"HTTP/1.0 200 OK\n", 16);
                            } // end if 
                        
                            goto peer_error;
                        } // end if it is a query

                        // It is not a query
                        if (strlen(filename)==0) {
                            // ACE::write_n(ACE_STDOUT,"filename length error",21);
                            // goto peer_error;
                            filename = const_cast<char*>("index.html");
                        }
                        ACE_stat stat;
                        // Can we stat the file?
                        if (ACE_OS::stat (filename, &stat) == -1) {
                            ACE::write_n(ACE_STDOUT,"stat fail",9);
                            peer.send_n("\n", 1);
                            ACE::write_n(ACE_STDOUT,"\n", 1);
                            goto peer_error;
                        }
                        ssize_t size = stat.st_size;
                        if (size == 0) {
                            ACE::write_n(ACE_STDOUT,"file size error",15);
                            goto peer_error;
                        }
                        // Can we open the file?
                        ACE_HANDLE handle = ACE_OS::open (filename, O_RDONLY | O_DIRECT);
                        if (handle == ACE_INVALID_HANDLE) {
                            ACE::write_n(ACE_STDOUT,"open fail",9);
                            goto peer_error;
                        }
                       
                        int ret = posix_fadvise(handle,0,0, POSIX_FADV_SEQUENTIAL);
                        void* mm_file = mmap(NULL, size, PROT_READ, MAP_SHARED, handle, 0);

                        peer.send_n("HTTP/1.0 200 OK\n", 16);
                        ACE::write_n(ACE_STDOUT,"HTTP/1.0 200 OK\n", 16);
                        const char* m_mimeType = getMimeType(filename);
                        peer.send_n("Content-type: ", 14);
                        peer.send_n(m_mimeType, strlen(m_mimeType));
                        peer.send_n("\n", 1);
                        
                        ACE::write_n(ACE_STDOUT, "Content-type: ", 14);
                        ACE::write_n(ACE_STDOUT, m_mimeType, strlen(m_mimeType));
                        ACE::write_n(ACE_STDOUT, "\n", 1);
                        char* content_len = new char[16];
                        std::unique_ptr<char> auto_content_len (content_len);
                        ACE_OS::itoa (size, content_len, 10);
                        peer.send_n("Content-length: ", 16);
                        peer.send_n(content_len, strlen(content_len));
                        peer.send_n("\n\n", 2);
                        peer.send_n(mm_file, size);
                        ACE::write_n(ACE_STDOUT, "Content-length: ", 16);
                        ACE::write_n(ACE_STDOUT, content_len, strlen(content_len));
                        ACE::write_n(ACE_STDOUT, "\n\n", 2);
                        // ACE::write_n(ACE_STDOUT, mm_file, size);
                        ret = munmap(mm_file, size);
                        goto peer_error;
                    }
                } //end 
            } //end if recv result > 0
            else
            {
                goto peer_error;
            }
        } //end for read data
    peer_error:
        peer.close();
    }//end for listen
    mtrace();
acceptor_error:
    return acceptor.close()==-1?1:0;
}
#endif // BOOST_AUTO_TEST_MAIN
