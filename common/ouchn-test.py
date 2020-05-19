# coding=utf-8
import requests


"""用于 简单快速刷新 课程视频观看状态"""

# 从网站登陆，后获取cookie
cookie = ''

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:67.0) Gecko/20100101 Firefox/67.0',
           'X-Requested-With': 'XMLHttpRequest',
           'Cookie': cookie,
           'Content-Type': 'application/x-www-form-urlencoded'}

url = 'http://beijing.ouchn.cn/theme/blueonionre/modulesCompletion.php'


# 近代史课程

courseid = '4216'
# key:sectionid value:cmid
ids = {
        '75298': range(418756, 418765),   # course 3
        '75303': range(418771, 418783),   # course 4
        '75309': range(418787, 418802),   # course 5
        '75315': range(418806, 418817)    # course 6
}

# 特色社会主义课程
courseid2 = '4217'

# key:sectionid value:cmid
ids2 = {
    '75331': range(418835, 418838),  # course 0
    '75336': range(418841, 418851),  # course 1
    '75342': range(418854, 418864),  # course 2
    '75348': range(418867, 418877),  # course 3
    '75354': range(418880, 418909),  # course 4
    '75360': range(418924, 418929),  # course 5
    '75366': range(418932, 418941),  # course 6
    '75372': range(418944, 418947),  # course 7
    '75378': range(418950, 418956),  # course 8
    '75384': range(418959, 418963),  # course 9
    '75390': range(418966, 418976)   # course 10
}


def do_refresh(ids, courseid):
    for sectionid, cmids in ids.iteritems():
        for cmid in cmids:
            params = {'sectionid': sectionid,
                      'id': courseid,
                      'cmid': str(cmid)}

            r = requests.get(url=url, params=params, headers=headers)
            print r.text


if __name__ == '__main__':
    do_refresh(ids2, courseid2)
