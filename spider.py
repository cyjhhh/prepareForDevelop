import urllib.request, urllib.error
import re
from bs4 import BeautifulSoup
import logging
import pymysql


logging.basicConfig(filename = "/root/myProject/project.log",level = logging.INFO, filemode = 'a', format = '%(asctime)s - %(levelname)s: %(message)s')


findlink = re.compile(r'<a href="(.*?)">')  # 电影链接
findimg = re.compile(r'<img.*src="(.*?)".*/>', re.S)  # 电影图片链接
findtitle = re.compile(r'<span class="title">(.*)</span>')  # 电影名
findrank = re.compile(r'<em class="">(\d*)</em>')  # 电影排名
findscore = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')  # 电影评分
findnumber = re.compile(r'<span>(\d*)人评价</span>')  # 评价人数
findinfo = re.compile(r'<span class="inq">(.*)</span>')  # 详情


def getData(baseurl):
    dataList = []
    for i in range(10):
        url = baseurl + str(i*25)
        html = askURL(url)  # html此时是获取到的网页源码
        # 解析数据
        soup = BeautifulSoup(html, "html.parser")
        a = soup.find_all('div', class_='item')
        for item in a:
            item = str(item)
            data = []

            link = re.findall(findlink, item)
            data.append(link[0])

            img = re.findall(findimg, item)
            data.append(img[0])

            title = re.findall(findtitle, item)
            if len(title) == 2:
                title[1] = re.sub('\xa0', '', title[1])
                title[1] = title[1].replace('/', '')
            else:
                title.append(' ')  # 有些只有一个中文名
            data.append(title[0])
            data.append(title[1])

            rank = re.findall(findrank, item)
            data.append(rank[0])

            score = re.findall(findscore, item)
            data.append(score[0])

            number = re.findall(findnumber, item)
            data.append(number[0])

            info = re.findall(findinfo, item)
            if len(info) != 0:
                data.append(info[0])
            else:
                data.append(' ')  # 有些没有优选评价

            dataList.append(data)
    return dataList


def askURL(url):
    # 设置UA
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
    }
    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response =urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
    except Exception as e:
        print(e)
    return html


def initTable():
    con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='test')
    cur = con.cursor()
    sql = '''
        create table movieTop250(
            Rank int primary key,
            CTitle varchar(100) not null,
            OTitle varchar(100),
            Img varchar(100),
            Link varchar(100),
            Score varchar(20),
            Number varchar(50),
            Info varchar(200)
        )
    '''
    try:
        cur.execute(sql)
        print('创建成功')
    except Exception as e:
        print(e)
        print('创建失败')
        logging.error(str(e))
    finally:
        con.close()


def saveData(dataList):
    print('insert start')
    con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='test')
    cur = con.cursor()
    sql = '''
        insert into movieTop250(Rank, CTitle, OTitle, Img, Link, Score, Number, Info) values (%s, %s, %s, %s, %s, %s, %s, %s)
    '''
    for data in dataList:
        print(data)
        try:
            cur.execute(sql, (data[4], data[2], data[3], data[1], data[0], data[5], data[6], data[7]))
            con.commit()
            print('insert ok!')
        except Exception as e:
            print(e)
            logging.error(str(e))
    con.close()


if __name__ == '__main__':
    url = "https://movie.douban.com/top250?start="
    res = getData(url)
    initTable()
    saveData(res)
