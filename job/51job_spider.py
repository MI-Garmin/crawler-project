import ssl
import urllib
from bs4 import BeautifulSoup as BS
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
import requests
from urllib import parse  # decode
import re
import json
import pprint
import xlwt
import sqlite3 as sql

# 分析网页信息，结构，考虑怎么进行构建爬虫程序

# 案例为查找深圳的具体岗位信息
# 输入职位关键词，获取详情url
keyword = input('输入搜索职位关键字：')
keyword_decode = parse.quote(parse.quote(keyword))

# web link
base_url = "https://search.51job.com/list/040000,000000,0000,00,9,99," + keyword_decode + ",2,1.html?lang=c&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&ord_field=0&dibiaoid=0&line=&welfare="
savepath = "jobdata.xls"


# main function
def main():
    job_list = []
    # 遍历网页（页数）
    for i in range(1, 3):
        baseurl = "https://search.51job.com/list/040000,000000,0000,00,9,99," + keyword_decode + ",2," + str(i) + ".html?lang=c&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&ord_field=0&dibiaoid=0&line=&welfare="
        print(baseurl)
        job_data = get_job_data(baseurl)
        job_list.append(job_data)
    # print(job_list[0][1])

    # saving the data with .xls file or using database
    # 1. .xls file
    save_data(job_list, savepath)


# demand for the web page, return html text
def ask_url(url):
    ssl._create_default_https_content = ssl._create_unverified_context
    html = ""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
    }
    # request = Request(url, headers=head)
    try:
        # response = urlopen(request)
        # html = response.read().decode('gbk','ignore')
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding
        html = response.text
    except URLError as e:
        if hasattr(e, 'code'):
            print(e.code)
        if hasattr(e, 'reason'):
            print(e.reason)
    return html


# 解析网页，获取工作岗位详细信息页的链接
def get_job_data(url):
    # a list to save each info of job
    job_data = []
    html = ask_url(url)
    soup = BS(html, 'html.parser')

    # create regex rule
    regex = re.compile('window.__SEARCH_RESULT__ =(.*?)</script>')
    items = str(soup)

    items = re.findall(regex, items)[0]
    html_data = str(items)

    # save job_data
    json_data = json.loads(html_data)
    for i in range(len(json_data['engine_jds'])):
        # a list to save each job infomation
        data = [json_data['engine_jds'][i]['job_href'], json_data['engine_jds'][i]['company_name'],
                json_data['engine_jds'][i]['job_name'], json_data['engine_jds'][i]['providesalary_text'],
                json_data['engine_jds'][i]['workarea_text'], "%s %s" % (json_data['engine_jds'][i]['workyear'], "years experience"),
                json_data['engine_jds'][i]['issuedate']]
        job_data.append(data)
    return job_data


# create table
def init_db(dbpath):
    query = '''
        CREATE TABLE jobinfo
        (
        id integer primary key autoincrement,
        job_link text,
        job_title varchar,
        job_location varchar,
        salary numeric,
        requirement text
        )
    '''
    conn = sql.connect(dbpath)
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    conn.close()


# save the data
def save_data(datalist, savepath):
    print("start to save")
    book = xlwt.Workbook(encoding='gbk', style_compression=0)
    # sheet = book.add_sheet("51job info", cell_overwrite_ok=True)
    col = ("job link", "company name", "job tittle", "salary", "work area", "experience", "issuedate")
    # for i in range(0, 7):
    #     sheet.write(0, i, col[i])
    # 遍历页数
    for i in range(0, len(datalist)):
        sheet = book.add_sheet("page" + str(i+1), cell_overwrite_ok=True)
        for p in range(0, 7):
            sheet.write(0, p, col[p])
        page = datalist[i]
        # print(page)
        for x in range(1, len(page)):
            data = page[x]
            for y in range(0, 7):
                sheet.write(x, y, data[y])
    book.save(savepath)
    print('success!')


# execute main() function
if __name__ == '__main__':
    main()
