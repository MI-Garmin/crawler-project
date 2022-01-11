import re
import ssl
from urllib.error import URLError
from urllib.request import Request
from urllib.request import urlopen
import xlwt
import sqlite3
from bs4 import BeautifulSoup as BS

"""
1.获取网页url，获取html信息 --> urllib
2.解析网页，获取具体信息 --> beautifulsoup4
3.保存获取的信息  --> sql | xls
"""

# 创建正则表达式对象，表示规则
findLink = re.compile(r'\<a href="(.*?)">')
# 图片
findImgSrc = re.compile(r'<img .*src="(.*?)"', re.S)  # 让换行符包括在字符中
# 标题
findTitle = re.compile(r'<span class="title">(.*)</span>')
# 评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
# 概括
findInq = re.compile(r'<span class="inq">(.*)</span>')


def main():
    # web link
    baseurl = 'https://movie.douban.com/top250?start='
    # the path of the xls file
    path = 'movie TOP250.xls'
    # database path
    dbpath = 'movie.db'

    # 1.get the information
    datalist = getData(baseurl)
    print(len(datalist))

    # 2.1 save data into the xls file
    save_data(datalist, path)

    # 2.2 save data into Database
    save_data_db(datalist, dbpath)


def getData(baseurl):
    datalist = []
    for i in range(0, 10):
        url = baseurl + str(i * 25)
        html = askURL(url)

        # 逐一获取数据（25页）
        soup = BS(html, 'html.parser')
        for item in soup.find_all('div', {'class': 'item'}):
            data = []
            # 将抓取到的信息转换为string类型，做接下来的分析
            item = str(item)
            # print(item)

            # 查找网页链接
            link = re.findall(findLink, item)[0]
            data.append(link)

            # 获取图片链接
            img = re.findall(findImgSrc, item)[0]
            data.append(img)

            # 查找片名，分析可能会存在2个片名，故用if判断操作
            title = re.findall(findTitle, item)
            if len(title) == 2:
                cn_title = title[0]
                data.append(cn_title)
                en_title = title[1].replace("/", "")
                data.append(en_title)
            else:
                data.append(title[0])
                data.append(" ")

            # 评分
            score = re.findall(findRating, item)[0]
            data.append(score)

            # 概括
            inq = re.findall(findInq, item)
            if len(inq) != 0:
                inq = inq[0].replace("。", "")
                data.append(inq)
            else:
                data.append(" ")

            datalist.append(data)
    return datalist


# method1: save the data into local files(xls etc.)
def save_data(datalist, savepath):
    print('start to save...')
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = book.add_sheet("douban movie TOP250", cell_overwrite_ok=True)
    col = ("link", "img", "title", "for_title", "score", "content")
    for i in range(0, 6):
        sheet.write(0, i, col[i])
    for i in range(1, 250):
        data = datalist[i]
        for j in range(0, 6):
            sheet.write(i, j, data[j])
    book.save(savepath)


# method2: save the data into Database
def save_data_db(datalist, dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()

    for data in datalist:
        for index in range(len(data)):
            # 判断数值型不做操作
            if index == 4:
                continue
            data[index] = '"' + data[index] + '"'
        sql = '''
            insert into movie250 (
            web_link, img_link, cn_title, en_title, rating, introduction)
            values(%s)'''%",".join(data)

        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()


def init_db(dbpath):
    sql = '''
        create table movie250
        (
        id integer primary key autoincrement,
        web_link text,
        img_link text,
        cn_title varchar,
        en_title varchar,
        rating numeric,
        introduction text
        )
    '''
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()


def askURL(url):
    ssl._create_default_https_context = ssl._create_unverified_context
    head = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/96.0.4664.110 Safari/537.36 "
    }
    request = Request(url, headers=head)
    html = ''
    try:
        response = urlopen(request)
        html = response.read().decode('utf-8')
    except URLError as e:
        if hasattr(e, 'code'):
            print(e.code)
        if hasattr(e, 'reason'):
            print(e.reason)

    return html


if __name__ == '__main__':
    main()
    print('Finsh, Please check!')
