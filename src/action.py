import time

if __name__ == "__main__": 
    print 'start'
    t = 0
    start = time.time()
    while t<60:
        s = raw_input()
        print "%s:%s" %( s, time.time() - start)
       