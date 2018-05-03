#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import smtplib  
from email.mime.text import MIMEText
import jinja2 # pip install Jinja2

FROM = ' Weekly Report'
TMPL=u'''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html lang="ch">
<head>
    <title>Jenkins Weekly Report Email</title>
</head>
<body>
    <h1>服务更新状态</h1>
    <table border="1">
        <tr>
            <th>服务名成</th>
            <th>失败次数</th>
            <th>作者</th>
            <th>部门</th>
        </tr>
    {% for service in services %}
        <tr>
            <td>{{service.NAME}}</td>
            <td>{{service.FAILNUM}}</td>
            <td>{{service.AUTH}}</td>
            <td>{{service.DEPARTMENT}}</td>
        </tr>
    {% endfor %}
    </table>
</body>
</html>
'''
class customSmtp(object):
    def __init__(self, smtpHostName, user, passwd):
        self.smtp = smtplib.SMTP()
        self.smtp.connect(smtpHostName)
        self.smtp.login(user, passwd)
        self.user = user
    def commit(self, subject, content,toAuthor):
        tmpl = jinja2.Template(TMPL)
        cont = tmpl.render(services=content)
        msg = MIMEText(cont, _subtype='html',_charset='utf8')
        msg['Subject'] = subject
        msg['From'] = FROM
        msg['To'] = ';'.join(toAuthor[1:])
        msg['CC'] = toAuthor[0]
        self.smtp.sendmail(self.user, toAuthor, msg.as_string())

if __name__ == '__main__':
    pass


