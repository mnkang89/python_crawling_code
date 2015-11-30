#-*- coding: utf-8 -*-

import argparse
import requests
import datetime
from bs4 import BeautifulSoup as bs
from urllib.parse import urlencode
import csv

class MLB(object):
    def __init__(self,query):
        self.query=query
        self.user_agent={'User-agent': 'Mozilla/5.0'}

    def url_scraper(self):
        url_list=list()
        user_agent = {'User-agent': 'Mozilla/5.0'}
        query=str(self.query)
        query=urlencode({'keyword':query},encoding='euc-kr')

        url="http://mlbpark.donga.com/mbs/articleL.php?mbsC=bullpen2&mbsW=search&select=stt&opt=1&"+query
        base_url="http://mlbpark.donga.com"
        
        page=1
        while True:
            page_url=url+"&cpage="+str(page)
            print(page_url)
            page_source=requests.get(page_url,headers=user_agent).text
            #print(page_source)
            tmp=bs(page_source)
            
            tmp_text_number=tmp.select('td[class="A11gray"]')
            tmp_list=tmp.select('a[href^="/mbs/articleVC.php?mbsC=bullpen2"]')
            tmp_writer=tmp.select('a[href^="javascript:userInfo"]')
            tmp_date=tmp.select('font[color="717171"]')

            if not tmp_list:
                break
            for i in range(25):
                try:
                    text_number=tmp_text_number[i].text
                    text_subject=tmp_list[i].text
                    text_writer=tmp_writer[i].text
                    text_time=tmp_date[i].text

                    a=str(tmp_list[i]).split("amp;")
                    factors=a[1]+a[2]+a[3]+a[4]+a[5]+query
                    fragment=a[0].split('"')[1]+factors

                    urls=base_url+fragment
                    #print(text_number,text_subject,text_writer,text_time)
                    lst=urls,text_number,text_subject,text_writer,text_time
                    url_list.append(lst)
                except:
                    pass
            page=page+1
            
        return(url_list)

    def content_scraper(self,urls):
        jobs=len(urls)
        query=self.query        

        user_agent={'User-agent': 'Mozilla/5.0'}
        csv_content_file = open(str("/home/mnkang89/jobdong/python_data/crawl_data/MLB/")+"MLB_cont_"+str(self.query)+str('.csv'), "w")
        csv_repl_file = open(str("/home/mnkang89/jobdong/python_data/crawl_data/MLB/")+"MLB_repl_"+str(self.query)+str('.csv'), "w")

        cw_content = csv.writer(csv_content_file , delimiter='\t')
        cw_repl = csv.writer(csv_repl_file,delimiter='\t')
        
        job=1
        failed=0
        for i in range(jobs):
            percent=round((job/jobs)*100,2)
            print("[job: ",job,"] [fail: ",failed,"]","[percent: ",percent,"]")
            number=urls[i][1]
            subject=urls[i][2]
            writer=urls[i][3]
            time=urls[i][4]

            page_url=urls[i][0]
            r=requests.get(page_url,headers=user_agent)
            r.encoding='euc-kr'
            tmp=bs(r.text)

            try:
                content=tmp.select('div[id="container"]')[0].select('td[class="G13"]')[0].text.strip()
                content=replace_all(content)
                cont_row=(number,subject,writer,time,content,query)
                cw_content.writerow(cont_row)

                repl_len=len(tmp.select('div[id="container"]')[0].select('td[class="G12"]'))

                for i in range(repl_len):
                    tmp_repl=tmp.select('div[id="container"]')[0].select('td[class="G12"]')[i].text.strip()
                    tmp_repl=replace_all(tmp_repl)
                    repl_row=(number,time,tmp_repl,query)
                    cw_repl.writerow(repl_row)                    
            except:
                failed+=1
                pass
            
            job+=1
            
        csv_content_file.close()
        csv_repl_file.close()

        
def replace_all(content):
    replace_dic=['\n','\r','\t']
    for i in replace_dic:
        content=content.replace(i,'')
    return content

   

if __name__=="__main__":
    parser=argparse.ArgumentParser(description="controller")
    parser.add_argument("--query",action="store",dest="query",required=True)
    given_args=parser.parse_args()
    query=str(given_args.query)
    a=MLB(query)
    urls=a.url_scraper()
    a.content_scraper(urls)




