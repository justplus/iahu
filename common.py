#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import date,time,timedelta,datetime
#学期第一周的日期
firstweek=date(2013,2,27)

#上课时间
classtime=[time(8,30),time(9,20),time(10,20),time(11,10),time(14,00),time(14,50),time(15,40),time(16,30),time(19,00),time(19,50),time(20,40)]

#一节课持续时间
classdurition=40

#下课时间
def get_classover(classstart):
    overhour=classstart.hour
    overminute=classstart.minute;
    if classstart.minute+classdurition>=60:
        overhour=overhour+1
        overminute=overminute+classdurition-60
    else:
        overminute=overminute+classdurition
    return time(overhour,overminute)
    

#输入日期是学期的第几周date.today()
def get_week(input_date):
    s=input_date.split("-");
    year=int(s[0])
    month=int(s[1])
    day=int(s[2])
    return ((date(year,month,day)-firstweek).days-1)/7+1

#输入日期是周几
def get_weekday(input_date):
    s=input_date.split("-");
    year=int(s[0])
    month=int(s[1])
    day=int(s[2])
    weekdays=[u"周一",u"周二",u"周三",u"周四",u"周五",u"周六",u"周日"]
    return weekdays[date.isoweekday(date(year,month,day))-1]

#今天是学期的第几周
def get_week_today():
    return ((date.today()-firstweek).days-1)/7+1

#今天的日期
def get_date_today():
	td=date.today()
	if td.month<10:
		month_str="0"+str(td.month)
	else:
		month_str=str(td.month)
	if td.day<10:
		day_str="0"+str(td.day)
	else:
		day_str=str(td.day)
	return str(td.year)+"-"+month_str+"-"+day_str
	
#当前时刻
def get_now_time():
	nowtime=datetime.now()
	h=nowtime.hour
	m=nowtime.minute
	return "%s:%s"%(h,m)
	
#下一时刻（40min后）
def get_next_time():
	nowtime=datetime.now()
	h=nowtime.hour
	m=nowtime.minute
	if m+40>=60:
		h=h+1
		m=m+40-60
	else:
		m=m+40
	return "%s:%s"%(h,m)
	
#今天是周几
def get_weekday_today():
	weekdays=[u"周一",u"周二",u"周三",u"周四",u"周五",u"周六",u"周日"]
    	return weekdays[date.isoweekday(date.today())-1]
    	
#输入开始时间和结束时间，看跨过了哪节课
def get_classindex(start_time,end_time):
    s=start_time.split(":")
    stime=time(int(s[0]),int(s[1]))
    s=end_time.split(":")
    etime=time(int(s[0]),int(s[1]))
    start=1
    kindex=0
    if classtime[0]>stime:
        start=0
    elif get_classover(classtime[10])<=stime:
        start=12
    else:
        while kindex<11:
            if classtime[kindex]<=stime and stime<get_classover(classtime[kindex]):
                start=kindex+1
                break
            elif classtime[kindex+1]>stime and stime>=get_classover(classtime[kindex]):
                start=kindex+2
                break
            kindex=kindex+1
    end=1
    kindex=0
    if classtime[0]>etime:
        end=0
    elif classtime[10]<etime:
        end=12
    else:
        while kindex<11:
            if classtime[kindex]<=etime and stime<get_classover(classtime[kindex]):
                end=kindex+1
                break
            elif classtime[kindex+1]>etime and etime>=get_classover(classtime[kindex]):
                end=kindex+1
                break
            kindex=kindex+1
    tmplist = range(15)[start:end+1]
    """if start==0 and end!=0:
        tmplist.remove(0)"""
    return tmplist
