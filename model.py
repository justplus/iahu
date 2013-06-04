#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import date,time,timedelta,datetime
import xml.etree.ElementTree as ET
import urllib2
import json
import web
import re
import common

def _create_db():
    # 本地环境
    host = 'localhost'
    db = 'atahu'
    port = 3306
    user = 'root'
    pw = '1111'
    try:
        import sae.const
        db = sae.const.MYSQL_DB
        user = sae.const.MYSQL_USER
        pw = sae.const.MYSQL_PASS
        host = sae.const.MYSQL_HOST
        port = int(sae.const.MYSQL_PORT)
    except ImportError:
        pass
    return web.database(dbn='mysql', host=host, port=port, db=db, user=user, pw=pw)

#获取数据库操作对象    
db = _create_db()

#******解析XML数据-->对象
def parse_msg(rawmsgstr):
    root = ET.fromstring(rawmsgstr)
    msg = {}
    for child in root:
        msg[child.tag] = child.text
    return msg

#获取天气
def get_weather(wtype):
    if wtype == 0:
        url = "http://www.weather.com.cn/data/cityinfo/101220101.html"
    elif wtype == 1:
        url = "http://m.weather.com.cn/data/101220101.html"
    try:
        resp = urllib2.urlopen(url)
        weather = json.load(resp)
    except:
        weather=None
    return weather

#获取校车时刻
def get_schoolbus(schoolname):
    cday = date.isoweekday(date.today())
    if cday == 6:
        if schoolname == u"老校区":
            return u"今日老校区发车时间为： 7:50  8:30  9:40  13:20"
        else:
            return u"今日新校区发车时间为： 10:10  11:10  12:00  16:30  17:20"
    elif cday == 7:
        if schoolname == u"老校区":
            return u"今日老校区发车时间为： 8:30"
        else:
            return u"今日新校区发车时间为： 17:20"
    else:
        if schoolname == u"老校区":
            return u"今日老校区发车时间为： 7:50  8:30  9:40  11:00  13:20  15:00  16:00  18:10"
        else:
            return u"今日新校区发车时间为： 7:15  8:10  9:00  10:10  11:10  12:00  14:20  15:40  16:30  17:20  18:30  21:30"

#获取部门电话
def get_phone(deptname):
    sqlstr = "select * from phoneDB where dept like '%" + deptname + "%'"
    results = db.query(sqlstr)
    retstr = ""
    for result in results:
        retstr = "%s%s:%s "%(retstr,result.dept,result.phone)
    return retstr

#获取教务处新闻
def get_jwcnews():
    sqlstr = "select * from jwcnewsDB limit 0,10"
    results = db.query(sqlstr)
    retstr = ""
    for result in results:
        retstr = """%s<item>
                <Title><![CDATA[%s ---%s]]></Title>
                <PicUrl><![CDATA[]]></PicUrl>
                <Url><![CDATA[%s]]></Url>
                </item>"""%(retstr,result.newsTitle,result.newsPubDate,result.newsLink)
    return "<ArticleCount>10</ArticleCount><Articles>%s</Articles>"%(retstr)

#获取宣讲会信息
def get_jobnews():
    sqlstr = "select count(*) as rc from jobnewsDB order by jobDate limit 0,10"
    countresult = db.query(sqlstr)
    rcount = countresult[0].rc
    sqlstr = "select * from jobnewsDB order by jobDate limit 0,10"
    results = db.query(sqlstr)
    retstr = ""
    for result in results:
        tmpstr = u"公司：%s宣讲会日期：%s/%s 宣讲会地点：%s-%s"%(result.jobCompany,result.jobDate,result.jobTime,result.jobFrom,result.jobPlace)
        retstr = """%s<item>
                <Title><![CDATA[%s]]></Title>
                <Description><![CDATA[]]></Description>
                <PicUrl><![CDATA[]]></PicUrl>
                <Url><![CDATA[%s]]></Url>
                </item>"""%(retstr,tmpstr,result.jobLink)
    return "<ArticleCount>%s</ArticleCount><Articles>%s</Articles>"%(rcount,retstr)

#获取课程信息
def get_course(courseName):
    sqlstr = "select count(*) as rc from courseDB where courseName like '%" + courseName + "%'"
    countresult = db.query(sqlstr)
    rcount = countresult[0].rc
    if rcount == 0:
        return None
    sqlstr = sqlstr.replace("count(*) as rc","*")
    results = db.query(sqlstr)
    retstr = ""
    for result in results:
        tmpstr = u"%s %s %s学分 %s\n"%(result.courseName,result.courseType,result.courseCredit,result.courseSchool)
        retstr = "%s%s"%(retstr,tmpstr)
    return retstr[0:-2]

#获取教师信息
def get_teacher(teacherName):
    sqlstr = "select count(*) as rc FROM scheduleDB inner join teacherDB inner join courseDB on teacherDB.teacherName = '%s' and scheduleDB.courseID = courseDB.courseID and scheduleDB.teacherID = teacherDB.teacherID group by courseName"%teacherName
    countresult = db.query(sqlstr)
    rcount = countresult[0].rc
    if rcount == 0:
        return None
    sqlstr = sqlstr.replace("count(*) as rc","courseDB.courseName,courseDB.courseSchool,teacherDB.teacherID,teacherDB.teacherName,teacherDB.teacherTitle,teacherDB.teacherDept")
    results = db.query(sqlstr)
    retstr = ""
    for result in results:
        tmpstr = u"教职工号：%s  姓名：%s  职称：%s   院系：%s   授课：%s(%s)\n"%(result.teacherID,result.teacherName,result.teacherTitle,result.teacherDept,result.courseName,result.courseSchool)
        retstr = "%s%s"%(retstr,tmpstr)
    return retstr[0:-2]

#获取课程表信息
def get_coursetable(roomName):
    try:
        qweek = common.get_week_today()
        sqlstr = "select scheduleDB.courseTime,scheduleDB.courseID,courseDB.courseName,scheduleDB.teacherID,teacherDB.teacherName,scheduleDB.courseDept,scheduleDB.fromWeek,scheduleDB.endWeek from scheduleDB inner join courseDB inner join teacherDB inner join classroomDB on classroomDB.roomName = '%s' and classroomDB.roomID=scheduleDB.roomID and fromWeek<=%s and endWeek>=%s and courseWeekday='%s' and scheduleDB.courseID=courseDB.courseID and scheduleDB.teacherID=teacherDB.teacherID order by courseTime asc limit 0,11"%(roomName,qweek,qweek,common.get_weekday_today())
        qresults = db.query(sqlstr)
        retstr = ""
        for result in qresults:
            retstr = u"%s第%s节：%s 教师：%s 班级：%s 起讫周：%s-%s\n"%(retstr,result.courseTime,result.courseName,result.teacherName,result.courseDept if result.courseDept else "--",result.fromWeek,result.endWeek)
    except:
        return None
    else:
        return retstr[0:-2]

#获取教室信息
def get_classroom(condition):
    try:
        if condition == u"博南" or condition == u"博学南楼":
            bds = [u'博南A楼',u'博南B楼',u'博南C楼']
            bncond = "buildingName in ('"+"','".join(bds)+"')"
        elif condition == u"博北" or condition == u"博学北楼":
            bds = [u'博北A楼',u'博北B楼',u'博北C楼',u'博北D楼']
            bncond = "buildingName in ('"+"','".join(bds)+"')"
        elif condition == u"":
            bncond = "0 = 0"
        else:
             bncond = "buildingName = '" + condition + "'"
        qweek = common.get_week_today()
        tmplist=common.get_classindex(common.get_now_time(),common.get_next_time())
        if tmplist:
            jccondition="courseTime in("+",".join(str(x) for x in tmplist)+")"
        else:
            jccondition="1=0"
        sqlstr="select * from classroomDB where %s and roomID not in(select roomID from scheduleDB where courseWeekday='%s' and fromWeek <= %s and endWeek >= %s and %s) limit 0,30"%(bncond,common.get_weekday_today(),qweek,qweek,jccondition)
        qresults = db.query(sqlstr)
        retstr = ""
        for result in qresults:
            retstr = u"%s教室：%s 座位数：%s 类型：%s\n"%(retstr,result.roomName,result.seatCount,result.roomType)
    except:
        return None
    else:
        return retstr

#去除空格
def stripblank(s):
    return unicode(s.strip().lstrip("\r\n        ").rstrip("\r\n        "), "utf-8")

#获取图书馆书籍信息
def get_book(bookName):
    keyword = urllib2.quote(bookName.encode("utf-8"))
    getstring = "http://lib.ahu.cn/b_s.php?k=" + keyword + "&s_t=title&page=1&source=0&model=1&sort_t=CATA_DATE&sort_v=2&aaa=%E6%A3%80%E7%B4%A2"
    req = urllib2.Request(getstring)
    fd = urllib2.urlopen(req)
    resp = fd.read()
    p = re.compile(r"<div>[0-9]{1,2}.<a href='(\S+)'[\S\s]?target='_blank'>([\s\S]*?)</a></div><div>作者:([\s\S]*?)&nbsp;<br>索取号:([\s\S]*?)&nbsp;<br>出版社:([\s\S]*?)&nbsp;<br>出版日期:([\s\S]*?)&nbsp;")
    results = p.findall(resp)
    if len(results) == 0:
        return None
    retstr = ""
    for result in results:
        tmpstr = u"书名：%s\n作者：%s\n索取号：%s\n出版社：%s\n出版日期：%s"%(stripblank(result[1]),stripblank(result[2]),stripblank(result[3]),stripblank(result[4]),stripblank(result[5]))
        retstr = """%s<item>
                <Title><![CDATA[%s]]></Title>
                <Description><![CDATA[]]></Description>
                <PicUrl><![CDATA[]]></PicUrl>
                <Url><![CDATA[http://lib.ahu.cn/%s]]></Url>
                </item>"""%(retstr,tmpstr,result[0])
    return "<ArticleCount>%s</ArticleCount><Articles>%s</Articles>"%(len(results),retstr)

#获取豆瓣电影信息
def get_movie(moviename):
    movieurlbase = "http://api.douban.com/v2/movie/search"
    DOUBAN_APIKEY = "082d3d40a387e2571887b7c1ea97a705"
    searchkeys = urllib2.quote(moviename.encode("utf-8"))
    url = '%s?q=%s&apikey=%s' % (movieurlbase, searchkeys, DOUBAN_APIKEY)
    resp = urllib2.urlopen(url)
    movie = json.loads(resp.read())
    if movie == None or movie["subjects"] == None or len(movie["subjects"]) == 0:
        return None
    detailurl = 'http://api.douban.com/v2/movie/subject/%s?apikey=%s' % (movie["subjects"][0]["id"], DOUBAN_APIKEY)
    resp = urllib2.urlopen(detailurl)
    description = json.load(resp)
    description = ''.join(description['summary'])
    retstr = """<item>
             <Title><![CDATA[%s]]></Title>
             <Description><![CDATA[%s]]></Description>
             <PicUrl><![CDATA[%s]]></PicUrl>
             <Url><![CDATA[http://lib.ahu.cn/%s]]></Url>
             </item>"""%(movie["subjects"][0]["title"],description,movie["subjects"][0]["images"]["large"],movie["subjects"][0]["alt"])
    return "<ArticleCount>1</ArticleCount><Articles>%s</Articles>"%(retstr)

#获取豆瓣音乐信息
def get_music(musicname):
    musicurlbase = "http://api.douban.com/v2/music/search"
    DOUBAN_APIKEY = "082d3d40a387e2571887b7c1ea97a705"
    searchkeys = urllib2.quote(musicname.encode("utf-8"))
    url = '%s?q=%s&apikey=%s' % (musicurlbase, searchkeys, DOUBAN_APIKEY)
    resp = urllib2.urlopen(url)
    music = json.loads(resp.read())
    if music == None or music["musics"] == None or len(music["musics"]) == 0:
        return None
    description = u"歌手：%s\n专辑名：%s\n专辑评分：%s(%s人评分)\n专辑歌曲：\n%s"%(music["musics"][0]["attrs"]["singer"][0],music["musics"][0]["attrs"]["title"][0],music["musics"][0]["rating"]["average"],music["musics"][0]["rating"]["numRaters"],music["musics"][0]["attrs"]["tracks"][0])
    retstr = """<item>
             <Title><![CDATA[%s]]></Title>
             <Description><![CDATA[%s]]></Description>
             <PicUrl><![CDATA[%s]]></PicUrl>
             <Url><![CDATA[http://lib.ahu.cn/%s]]></Url>
             </item>"""%(music["musics"][0]["title"],description,music["musics"][0]["image"].replace("spic","lpic"),music["musics"][0]["mobile_link"])
    return "<ArticleCount>1</ArticleCount><Articles>%s</Articles>"%(retstr)
    
#获取豆瓣电台信息
def get_musicurl(chname):
    try:
        """query =  urllib2.quote(musicname.encode("utf-8"))
        url = 'http://music.baidu.com/search?key='+query
        response = urllib2.urlopen(url)
        text = response.read()
        reg1 = re.compile(r'<span class="song-title".+?>.+?<a.+?><em><em>(.*?)</em></em></a>',re.S)
        reg2 = re.compile(r'<span class="author_list".+?title="(.*?)">',re.S)
        artist = re.findall(reg2,text)[0]
        musicname = re.findall(reg1,text)[0]
        musicurlbase = "http://box.zhangmen.baidu.com/x?op=12&count=1&title="
        key1 = urllib2.quote(musicname)
        key2 = urllib2.quote(artist)
        url = '%s%s$$%s$$$$' % (musicurlbase, key1,key2)
        resp = urllib2.urlopen(url)
        xml = resp.read()
        description = artist+"-"+musicname
        encode =  re.compile('<encode>.*?CDATA\[(.*?)\]].*?</encode>',re.S).findall(xml)[0] 
        decode =  re.compile('<decode>.*?CDATA\[(.*?)\]].*?</decode>',re.S).findall(xml)[0]  
        musiclink = encode[:encode.rindex('/')+1] + decode"""
        keyword = urllib2.quote(chname.encode("utf-8"))
        url = 'http://douban.fm/j/explore/search?query=%s&start=0&limit=20'%keyword
        resp = urllib2.urlopen(url)
        channels = json.load(resp)
        chNo = channels["data"]["channels"][0]["id"]
        title = u"豆瓣电台" + channels["data"]["channels"][0]["name"] + "MHz"
        qurl = "http://douban.fm/j/mine/playlist?type=n&channel=%s&pb=64"%chNo
        musics = json.load(urllib2.urlopen(qurl))
        musicurl = musics["song"][0]["url"]
        description = u"歌手：%s\n歌曲：%s\n专辑：%s"%(musics["song"][0]["artist"],musics["song"][0]["title"],musics["song"][0]["albumtitle"])
        retstr = """<Music>
                <Title><![CDATA[%s]]></Title>
                <Description><![CDATA[%s]]></Description>
                <MusicUrl><![CDATA[%s]]></MusicUrl>
                <HQMusicUrl><![CDATA[%s]]></HQMusicUrl>
                </Music>"""%(title,description,musicurl,musicurl)
    except:
        return None
    else:
        return retstr
