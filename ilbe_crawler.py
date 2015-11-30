#-*- coding: utf-8 -*-
'''
---일베 게시판 사용설명서---

<사용법>
a=ilbe("힙합")
urls=a.url_scraper()
results=a.content_scraper(urls)
'''
import csv
import requests
import datetime
from bs4 import BeautifulSoup as bs
from time import sleep
import argparse


class ilbe(object):
    def __init__(self,query,menu="celeb"):
        self.user_agent={'User-agent': 'Mozilla/5.0'}
        self.query=query
        self.menu=menu

    def url_scraper(self):
        url_list=list()
        user_agent =self.user_agent
        query=str(self.query)
        menu=str(self.menu)
        url="http://www.ilbe.com/?_filter=search&mid="+menu+"&category=&search_target=title&search_keyword="+query
        #table=music부분이 변하는부분
        
        page=1
        while True:
            page_url=url+"&page="+str(page)
            print(page_url)
            page_source=requests.get(page_url,headers=user_agent).text
            tmp=bs(page_source)
            tmp_list=tmp.select('tr[class^=bg]')

            if '비정상적인 검색입니다.' in str(tmp):
                continue

            if not tmp_list:
                break
                
            for i in range(22):
                try:
                    content_url=str(tmp.select('tr[class^=bg]')[i].select('a')[0])
                    content_url=content_url.split('"')[1].replace('amp;','')
                    text_number=content_url.split('=')[-1]
                    text_subject=tmp.select('tr[class^=bg]')[i].select('td[class=title]')[0].text.strip()
                    text_subject=replace_all(text_subject)

                    text_writer=tmp.select('tr[class^=bg]')[i].select('td[class=author]')[0].text.strip()
                    text_time=tmp.select('tr[class^=bg]')[i].select('td[class=date]')[0].text.strip()
                    text_time=replace_all(text_time)

                    lst=content_url,text_number,text_subject,text_writer,text_time
                    url_list.append(lst)
                except:
                    pass
    
            page=page+3
        
        return(url_list)

    def content_scraper(self,urls):
        csv_content_file = open(str("/home/ubuntu/kms/crawling/data/ilbe/")+"ilbe_cont_"+str(self.query)+str('.csv'), "w")
        csv_repl_file = open(str("/home/ubuntu/kms/crawling/data/ilbe/")+"ilbe_repl_"+str(self.query)+str('.csv'), "w")

        cw_content = csv.writer(csv_content_file , delimiter='\t')
        cw_repl = csv.writer(csv_repl_file,delimiter='\t')

        query=self.query
        jobs=len(urls)
        user_agent={'User-agent': 'Mozilla/5.0'}
        proxies1 = {"http": "http://210.101.131.231:8080"}
        proxies2 = {"http": "http://210.101.131.232:8080"}
        contents_list=list()
        repl_list=list()
        
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

            while True:
                try:
                    #sleep(1.5)
                    page_source=requests.get(page_url+"&m=1",headers=user_agent).text
                    tmp=bs(page_source)
                    content=tmp.select('div[class^="document"]')[0].text
                    print("성공!")
                    break
                except IndexError:
                    try:
                        page_source=requests.get(page_url+"&m=1",headers=user_agent,proxies=proxies1).text
                        tmp=bs(page_source)
                        content=tmp.select('div[class^="document"]')[0].text
                        print("프록시1 성공!")
                        break
                    except IndexError:
                        try:
                            page_source=requests.get(page_url+"&m=1",headers=user_agent,proxies=proxies2).text
                            tmp=bs(page_source)
                            content=tmp.select('div[class^="document"]')[0].text
                            print("프록시2 성공!")
                            break
                        except:
                            pass
                except KeyboardInterrupt:
                    print('keyboard')
                    return
                except Exception as error:
                    print(error)

            try:
                content=tmp.select('div[class^="document"]')[0].text
                content=replace_all(content)
                cont_row=(number,subject,writer,time,content,query)
                
                cw_content.writerow(cont_row)
                #여기까지했음
                repl_len=len(tmp.select('li[id^="comment_"]'))
                for i in range(repl_len):
                    tmp_repl=tmp.select('li[id^="comment_"]')[i].text.strip()
                    if not tmp_repl:
                        tmp_repl="NONE"

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
    a=ilbe(query)
    urls=a.url_scraper()
    a.content_scraper(urls)

