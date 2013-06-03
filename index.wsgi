#*************************************************************************
#	-*- coding:utf-8 -*-
#	> File Name: code.py
#	> Author: justplus
#	> Mail: justplus@ahu.edu.cn 
#	> Created Time: 2013年05月22日 星期三 13时37分
#   >校园助手---微信平台
# ************************************************************************
import os
import web
import hashlib
import time
import model

#地址映射
urls = (
'/', 'Index'
)

#推送文本消息格式
textTpl = """<xml>
        <ToUserName><![CDATA[%s]]></ToUserName>
        <FromUserName><![CDATA[%s]]></FromUserName>
        <CreateTime>%s</CreateTime>
        <MsgType><![CDATA[%s]]></MsgType>
        <Content><![CDATA[%s]]></Content>
        <FuncFlag>0</FuncFlag>
        </xml>"""
        
pictextTpl = """<xml>
             <ToUserName><![CDATA[%s]]></ToUserName>
             <FromUserName><![CDATA[%s]]></FromUserName>
             <CreateTime>%s</CreateTime>
             <MsgType><![CDATA[%s]]></MsgType>
             %s
             <FuncFlag>0</FuncFlag>
             </xml>"""

musicTpl = """<xml>
            <ToUserName><![CDATA[%s]]></ToUserName>
            <FromUserName><![CDATA[%s]]></FromUserName>
            <CreateTime>%s</CreateTime>
            <MsgType><![CDATA[%s]]></MsgType>
            %s
            <FuncFlag>0</FuncFlag>
            </xml>"""
             
#主体类
class Index:
    def GET(self):
        getdata = web.input()
        token = "iahu"
        tmpList = [token, getdata.timestamp, getdata.nonce]
        tmpList.sort()
        tmpstr = ''.join(tmpList)
        hashstr = hashlib.sha1(tmpstr).hexdigest()
        if hashstr == getdata.signature:
            return getdata.echostr
        else:
            return None
    def POST(self):
        obj = model.parse_msg(web.data())
        if obj["Content"] == "Hello2BizUser":
            return textTpl%(obj["FromUserName"],obj["ToUserName"],str(int(time.time())),"text",u"欢迎关注安大校园助手，您可以输入以下【格式】指令来进行查询:\n天气/今日天气/明日天气\n校车/新校区校车/老校区校车\n电话/教务处电话\n教务处新闻\n宣讲会\nC语言课程\n张三老师\n博学北楼A101课表\n自习室/自习室博南/自习室博学南楼\njava图书\n电影三个合伙人\n歌曲爱你一万年\n豆瓣电台华语\n")
        else:
            userContent = obj["Content"]
            if userContent.find(u"天气") >= 0:
                if userContent == u"明日天气":
                    tweather = model.get_weather(1)
                    if not tweather:
                        retstr = u"连接服务器出错，稍后重试！"
                    else:
                        retstr = u"明日天气：%s   温度：%s   %s (来源：中国天气网)"%(tweather["weatherinfo"]["weather2"],tweather["weatherinfo"]["temp2"],tweather["weatherinfo"]["wind2"])
                else:
                    tweather = model.get_weather(0)
                    if not tweather:
                        retstr = u"连接服务器出错，稍后重试！"
                    else:
                        retstr = u"今日天气：%s   最高温度：%s   最低温度：%s   发布时间：%s (来源：中国天气网)"%(tweather["weatherinfo"]["weather"],tweather["weatherinfo"]["temp1"],tweather["weatherinfo"]["temp2"],tweather["weatherinfo"]["ptime"])
                return textTpl%(obj["FromUserName"],obj["ToUserName"],str(int(time.time())),"text",retstr)
            elif userContent.find(u"校车") >= 0:
                if userContent == u"老校区校车" or userContent == u"校车老校区":
                    retstr = model.get_schoolbus(u"老校区")
                else:
                    retstr = model.get_schoolbus(u"新校区")
                return textTpl%(obj["FromUserName"],obj["ToUserName"],str(int(time.time())),"text",retstr)
            elif userContent.find(u"电话") >= 0:
                phoneinfo = model.get_phone(userContent[0:-2] if userContent.find(u"电话") > 0 else userContent[2:])
                if phoneinfo == "":
                    retstr = u"抱歉，没有找到您要找的电话！"
                else:
                    retstr = phoneinfo
                return textTpl%(obj["FromUserName"],obj["ToUserName"],str(int(time.time())),"text",retstr)
            elif userContent == u"教务处新闻":
                retstr = model.get_jwcnews()
                return pictextTpl%(obj["FromUserName"],obj["ToUserName"],str(int(time.time())),"news",retstr)
            elif userContent.find(u"宣讲会") >= 0:
                retstr = model.get_jobnews()
                return pictextTpl%(obj["FromUserName"],obj["ToUserName"],str(int(time.time())),"news",retstr)
            elif userContent.find(u"课程") >= 0:
                courseinfo = model.get_course(userContent[0:-2] if userContent.find(u"课程") > 0 else userContent[2:])
                if courseinfo == None:
                    retstr = u"抱歉，没有找到您查询的课程！"
                    return textTpl%(obj["FromUserName"],obj["ToUserName"],str(int(time.time())),"text",retstr)
                else:
                    retstr = courseinfo
                    return textTpl%(obj["FromUserName"],obj["ToUserName"],str(int(time.time())),"text",retstr)
            elif userContent.find(u"老师") >= 0:
                teacherinfo = model.get_teacher(userContent[0:-2] if userContent.find(u"老师") > 0 else userContent[2:])
                if teacherinfo == None:
                    retstr = u"抱歉，没有找到您查询的教师信息！"
                    return textTpl%(obj["FromUserName"],obj["ToUserName"],str(int(time.time())),"text",retstr)
                else:
                    retstr = teacherinfo
                    return textTpl%(obj["FromUserName"],obj["ToUserName"],str(int(time.time())),"text",retstr)
            elif userContent.find(u"课表") >= 0:
                coursetableinfo = model.get_coursetable(userContent[0:-2] if userContent.find(u"课表") > 0 else userContent[2:])
                if coursetableinfo == None:
                    retstr = u"抱歉，没有找到您查询的教室课表信息！"
                    return textTpl%(obj["FromUserName"],obj["ToUserName"],str(int(time.time())),"text",retstr)
                else:
                    retstr = coursetableinfo
                    return textTpl%(obj["FromUserName"],obj["ToUserName"],str(int(time.time())),"text",retstr)
            elif userContent.find(u"自习室") >= 0:
                roominfo = model.get_classroom(userContent[3:] if userContent.find(u"自习室") == 0 else userContent[0:-3])
                if roominfo == None:
                    retstr = u"抱歉，没有找到满足您条件的自习室信息！"
                    return textTpl%(obj["FromUserName"],obj["ToUserName"],str(int(time.time())),"text",retstr)
                else:
                    retstr = roominfo
                    return textTpl%(obj["FromUserName"],obj["ToUserName"],str(int(time.time())),"text",retstr + u"(列出前30条,请增加搜索条件过滤)")
            elif userContent.find(u"图书") >= 0:
                bookinfo = model.get_book(userContent[2:] if userContent.find(u"图书") == 0 else userContent[0:-2])
                if bookinfo == None:
                    retstr = u"抱歉，没有找到您查询的图书！"
                    return textTpl%(obj["FromUserName"],obj["ToUserName"],str(int(time.time())),"text",retstr)
                else:
                    retstr = bookinfo
                    return pictextTpl%(obj["FromUserName"],obj["ToUserName"],str(int(time.time())),"news",retstr)
            elif userContent.find(u"电影") >= 0:
                movieinfo = model.get_movie(userContent[2:] if userContent.find(u"电影") == 0 else userContent[0:-2])
                if movieinfo == None:
                    retstr = "抱歉，没有找到您查询的电影！"
                    return textTpl%(obj["FromUserName"],obj["ToUserName"],str(int(time.time())),"text",retstr)
                else:
                    retstr = movieinfo
                    return pictextTpl%(obj["FromUserName"],obj["ToUserName"],str(int(time.time())),"news",retstr)
            elif userContent.find(u"歌曲") >= 0:
                musicinfo = model.get_music(userContent[2:] if userContent.find(u"歌曲") == 0 else userContent[0:-2])
                if musicinfo == None:
                    retstr = "抱歉，没有找到您查询的歌曲！"
                    return textTpl%(obj["FromUserName"],obj["ToUserName"],str(int(time.time())),"text",retstr)
                else:
                    retstr = musicinfo
                    return pictextTpl%(obj["FromUserName"],obj["ToUserName"],str(int(time.time())),"news",retstr)
            elif userContent.find(u"豆瓣电台") >= 0:       
                musicurlinfo = model.get_musicurl(userContent[4:] if userContent.find(u"豆瓣电台") == 0 else userContent[0:-4])
                if musicurlinfo == None:
                    retstr = "抱歉，没有找到您查询的歌曲！"
                    return textTpl%(obj["FromUserName"],obj["ToUserName"],str(int(time.time())),"text",retstr)
                else:
                    retstr =  musicurlinfo
                    return musicTpl%(obj["FromUserName"],obj["ToUserName"],str(int(time.time())),"music",retstr)
            elif userContent.find(u"建议") >= 0:
                return textTpl%(obj["FromUserName"],obj["ToUserName"],str(int(time.time())),"text",u"感谢您的建议或意见，查看后给您回复！")
            else:
                return textTpl%(obj["FromUserName"],obj["ToUserName"],str(int(time.time())),"text",u"非法指令，您可以输入以下【格式】指令来进行查询:\n天气/今日天气/明日天气\n校车/新校区校车/老校区校车\n电话/教务处电话\n教务处新闻\n宣讲会\nC语言课程\n张三老师\n博学北楼A101课表\n自习室/自习室博南/自习室博学南楼\njava图书\n电影三个合伙人\n歌曲爱你一万年\n豆瓣电台华语\n")

app = web.application(urls, globals())
if __name__ == "__main__":
    app.run()
else:
    import sae
    application = sae.create_wsgi_app(app.wsgifunc())   