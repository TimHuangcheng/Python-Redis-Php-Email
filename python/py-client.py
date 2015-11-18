#!/usr/bin/env python 
#coding=utf-8 
import redis 

if __name__ == "__main__": 

    rc = redis.Redis(host='localhost',port=6379,db=0) 
    ip_addr = "192.168.1.100" 
    #for i in xrange(500): 
        #count = rc.lpush("ip:192.168.1.100",i) 
        #if count > 1000: 
            rc.publish("count_alarm", 12) 
            rc.publish('ip_alarm', ip_addr) 