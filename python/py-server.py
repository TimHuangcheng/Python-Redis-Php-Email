#!/usr/bin/env python 
#coding=utf-8 
import redis 
import tsendemail 
import CRedis
import pickle as p 
import phpseriralize as php_P
import ConfigParser
import time
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
ps.subscribe(['email'])  #订阅频道
print '//////////////////////////////////////'
print '@author    Tim'
print '@since     Version 1.0.0'
print 'Redis Python Email program start'
print ' - Subscribe \'email\' success '
i=0
for item in ps.listen(): 
        i=i+1
        print 'Listen' + str(i)
        #print 'Waiting new message'
        if item['type'] == 'message': 
            #print item['channel'] , item['data']
            shoplist = rc.get(item['data'])
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
                print da['to'] , da['subject'] , 'Send Yes' , i
                rc.remove(item['data'])
                print time.strftime('%Y-%m-%d %H:%M:%S') + '  Success  '+'    '+da['to'] +'    '+da['subject']
                #file = open('redis_python_email.txt','a')
                #file.write(time.strftime('%Y-%m-%d %H:%M:%S') + '  Success  '+'    '+da['to'] +'    '+da['subject'])
                #file.write('\n-------------\n')
                #file.close()
            else :
                print da['to'] , da['subject'] , 'Send Fail' , i
                print time.strftime('%Y-%m-%d %H:%M:%S') + '  Fail  '+'    '+da['to'] +'    '+da['subject']
                #file = open('redis_python_email.txt','a')
                #file.write(time.strftime('%Y-%m-%d %H:%M:%S') + '  Fail  '+'    '+da['to'] +'    '+da['subject'])
                #file.write('\n-------------\n')
                #file.close()
            del da # remove the shoplist  
            del shoplist # remove the shoplist  
            del authInfo # remove the shoplist  
            del htmlText # remove the shoplist  