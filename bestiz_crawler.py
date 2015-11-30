
# -*- coding: utf-8 -*-


'''
1.셀레늄으로 세션개방(하고자하는 게시판)


->목록페이지 url 임시저장(게시글 갯수 또한 저장)
->fopen을 이용해서 게시판파일 생성 and 오픈

[1차 for문]
2.셀레늄으로 게시글 하나하나 클릭(for문으로 돌아가고 게시글 갯수이용해서 리밋지정)
3.게시글내부에서 페이지소스 까보기(셀레늄->.text로)

4.셀렉터: [키워드, 제목, 게시글, 작성자]
7.fwrite을 이용해서 파일에 csv로 입력
->print문을 이용해서 게시시간 확인

[1차 for문 종속]
9.목록페이지로 돌아가기(with selenium back function)

[1차 for문 아웃]
10.다음페이지 클릭(셀레늄.click()이용)
11.if second <a>tag is 'prev' than click keep searching
'''

from bs4 import BeautifulSoup as bs
from selenium import webdriver
import requests
import csv

#file open
csv_file = open(str("/home/mnkang89/kms/")+"guestheaven"+str('.csv'), "w")
cw = csv.writer(csv_file , delimiter=',')

#session start
driver=webdriver.Firefox()
url=str("http://hgc.bestiz.net/zboard/zboard.php?&id=ghm2")
driver.get(url)
driver.find_element_by_css_selector('input[name="keyword"]').send_keys("소녀시대")

#snsd search
driver.find_element_by_css_selector('input[src="skin/gcmbl/search_right.gif"]').click()

while True:
    #페이지 로드 웨이팅
    driver.implicitly_wait(2) 
    soup=bs(driver.page_source)
    cont_num=len(soup.select('table')[3].select('td[align=left]'))

    #날짜구하기 ㅠㅠ
    a=len(soup.select('table')[3].select('span'))
    date=list()

    for i in range(1,a,2):
        b=soup.select('table')[3].select('span')[i]
        b=str(b).split(">")[1].split('<')[0]
        date.append(b)

    print(date)
    
    if(cont_num!=0):
        for i in range(1,cont_num+1):
            driver.find_element_by_css_selector(str("body > div > table:nth-child(5) > tbody > tr > td:nth-child(2)\
            > table:nth-child(1) > tbody > tr:nth-child("+str(2*i)+") > td:nth-child(2) > a")).click()

            writer=driver.find_element_by_css_selector("body > div > table:nth-child(5) > tbody > tr > td:nth-child(2) > table:nth-child(2) > tbody > tr:nth-child(4) > td:nth-child(2) > table > tbody > tr > td:nth-child(1) > span").text

            title=driver.find_element_by_css_selector("body > div > table:nth-child(5) > tbody > tr > td:nth-child(2) > table:nth-child(2) > tbody > tr:nth-child(6) > td:nth-child(2) > b").text

            try:
                content=driver.find_element_by_css_selector("body > div > table:nth-child(5) > tbody > tr > td:nth-child(2) > table:nth-child(3) > tbody").text
            except:
                content="NONE"

            try:
                reply=driver.find_element_by_css_selector("body > div > table:nth-child(5) > tbody > tr > td:nth-child(2) > table:nth-child(15) > tbody").text
            except:
                reply="NONE"

            row=[date[i-1],writer,title,content,reply]

            #writing in csv file
            cw.writerow(row)

            print(row)
            driver.back()

    try:
        driver.find_element_by_css_selector('body > div > table:nth-child(5) > tbody > tr > td:nth-child(2) > table:nth-child(2) > tbody > tr > td:nth-child(1) > zeroboard > a').click()
    except:
        try:
            driver.find_element_by_css_selector('body > div > table:nth-child(5) > tbody > tr > td:nth-child(2) > table:nth-child(2) > tbody > tr > td.listnum > zeroboard > font > a').click()
        except:
            try:
                driver.find_element_by_css_selector('body > div > table:nth-child(5) > tbody > tr > td:nth-child(2) > table:nth-child(2) > tbody > tr > td.listnum > zeroboard > font > font > a').click()
            except:
                pass
                break

