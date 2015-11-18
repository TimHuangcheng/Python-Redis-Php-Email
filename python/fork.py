#!/usr/bin/env python
#coding: utf-8

#python模拟linux的守护进程

import sys, os, time, atexit, string
import redis 
import tsendemail 
import CRedis
import pickle as p 
import phpseriralize as php_P
import ConfigParser
from signal import SIGTERM

class Daemon:
  def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/tem/py'):
      #需要获取调试信息，改为stdin='/dev/stdin', stdout='/dev/stdout', stderr='/dev/stderr'，以root身份运行。
    self.stdin = stdin
    self.stdout = stdout
    self.stderr = stderr
    self.pidfile = pidfile
  
  def _daemonize(self):
    try:
      pid = os.fork()    #第一次fork，生成子进程，脱离父进程
      if pid > 0:
        sys.exit(0)      #退出主进程
    except OSError, e:
      sys.stderr.write('fork #1 failed: %d (%s)\n' % (e.errno, e.strerror))
      sys.exit(1)
  
    os.chdir("/home/python")      #修改工作目录
    os.setsid()        #设置新的会话连接
    os.umask(0)        #重新设置文件创建权限
  
    try:
      pid = os.fork() #第二次fork，禁止进程打开终端
      if pid > 0:
        sys.exit(0)
    except OSError, e:
      sys.stderr.write('fork #2 failed: %d (%s)\n' % (e.errno, e.strerror))
      sys.exit(1)
  
     #重定向文件描述符
    sys.stdout.flush()
    sys.stderr.flush()
    si = file(self.stdin, 'r')
    so = file(self.stdout, 'a+')
    se = file(self.stderr, 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())
  
     #注册退出函数，根据文件pid判断是否存在进程
    atexit.register(self.delpid)
    pid = str(os.getpid())
    file(self.pidfile,'w+').write('%s\n' % pid)
  
  def delpid(self):
    os.remove(self.pidfile)

  def start(self):
     #检查pid文件是否存在以探测是否存在进程
    try:
      pf = file(self.pidfile,'r')
      pid = int(pf.read().strip())
      pf.close()
    except IOError:
      pid = None
  
    if pid:
      message = 'pidfile %s already exist. Daemon already running!\n'
      sys.stderr.write(message % self.pidfile)
      sys.exit(1)
    
    #启动监控
    self._daemonize()
    self._run()

  def stop(self):
    #从pid文件中获取pid
    try:
      pf = file(self.pidfile,'r')
      pid = int(pf.read().strip())
      pf.close()
    except IOError:
      pid = None
  
    if not pid:   #重启不报错
      message = 'pidfile %s does not exist. Daemon not running!\n'
      sys.stderr.write(message % self.pidfile)
      return

     #杀进程
    try:
      while 1:
        os.kill(pid, SIGTERM)
        time.sleep(0.1)
        #os.system('hadoop-daemon.sh stop datanode')
        #os.system('hadoop-daemon.sh stop tasktracker')
        #os.remove(self.pidfile)
    except OSError, err:
      err = str(err)
      if err.find('No such process') > 0:
        if os.path.exists(self.pidfile):
          os.remove(self.pidfile)
      else:
        print str(err)
        sys.exit(1)

  def restart(self):
    self.stop()
    self.start()

  def _run(self):
    """ run your fun"""
    #while True:
      #fp=open('/tmp/result','a+')
      #fp.write('Hello World\n')
      #sys.stdout.write('%s:hello world\n' % (time.ctime(),))
      #sys.stdout.flush() 
      #time.sleep(2)
    config = ConfigParser.ConfigParser()
    #rc = redis.Redis(host='localhost',port=6379,db=0) 
    #读取配置
    config.read("Config.ini")
    redisAuthInfo = {}
    redisAuthInfo['host'] = config.get('Redis','host')
    redisAuthInfo['port'] = config.get('Redis','port')
    redisAuthInfo['db'] = config.get('Redis','db')
    rc = CRedis.CRedis(redisAuthInfo)
    ps = rc.pubsub() 
    ps.subscribe(['email'])  #订阅两个频道，分别是count_alarm ip_alarm 
    #print '//////////////////////////////////////'
    #print '@author    Tim'
    #print '@since     Version 1.0.0'
    #print 'Redis Python Email program start'
    #print ' - Subscribe \'email\' success '
    #print time.strftime('%Y-%m-%d %H:%M:%S')
    i = 0
    for item in ps.listen(): 
        i=i+1
        print time.strftime('%Y-%m-%d %H:%M:%S') + 'Listen' + str(i)
        #print 'Waiting new message'
        if item['type'] == 'message': 
            #print item['channel'] , item['data']
            shoplist = rc.get(item['data'])
            #if shoplist is None :
            #    continue
            un = php_P.PHPUnserialize()
            da = un.unserialize(shoplist)
            authInfo = {}
            authInfo['server'] = config.get('Email','server')
            authInfo['user'] = config.get('Email','user')
            authInfo['password'] = config.get('Email','password')
            fromAdd = config.get('Email','fromAdd')
            toAdd = da['to']
            subject = da['subject']
            plainText = '这里是普通文本'
            htmlText = da['template']
            sendbool = tsendemail.sendEmail(authInfo, fromAdd, toAdd, subject, plainText, htmlText)
            if sendbool :
                #print da['to'] , da['subject'] , 'Send Yes' , i
                rc.remove(item['data'])
                print time.strftime('%Y-%m-%d %H:%M:%S') + '  Success  '+'    '+da['to'] +'    '+da['subject']
                #file = open('redis_python_email.txt','a')
                #file.write(time.strftime('%Y-%m-%d %H:%M:%S') + '  Success  '+'    '+da['to'] +'    '+da['subject'])
                #file.write('\n-------------\n')
                #file.close()
            else :
                #print da['to'] , da['subject'] , 'Send Fail' , i
                print time.strftime('%Y-%m-%d %H:%M:%S') + '  Fail  '+'    '+da['to'] +'    '+da['subject']
                #file = open('redis_python_email.txt','a')
                #file.write(time.strftime('%Y-%m-%d %H:%M:%S') + '  Fail  '+'    '+da['to'] +'    '+da['subject'])
                #file.write('\n-------------\n')
                #file.close()
            del da # remove the shoplist  
            del shoplist # remove the shoplist  
            del authInfo # remove the shoplist  
            del htmlText # remove the shoplist  

if __name__ == '__main__':
    daemon = Daemon('/tmp/watch_process.pid', stdout = '/tmp/watch_stdout.log', stderr = '/home/python/error.log')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            filelog = open('access-py.log','a')
            filelog.write(time.strftime('%Y-%m-%d %H:%M:%S') + '  start  ')
            filelog.write('\n-------------\n')
            filelog.close()
            print '////////////////////////////////////////'
            print '//  @author    Tim'
            print '//  @since     Version 1.0.0'
            print '//  Redis Python Email program start'
            print '//   - Subscribe Channel \'email\' success'
            print '////////////////////////////////////////'
            daemon.start()
        elif 'stop' == sys.argv[1]:
            filelog = open('access-py.log','a')
            filelog.write(time.strftime('%Y-%m-%d %H:%M:%S') + '  stop  ')
            filelog.write('\n-------------\n')
            filelog.close()
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print 'unknown command'
            sys.exit(2)
        sys.exit(0)
    else:
        print 'usage: %s start|stop|restart' % sys.argv[0]
        sys.exit(2)