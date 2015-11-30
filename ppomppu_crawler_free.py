#-*- coding: utf-8 -*-
'''
---ppomppu 게시판 사용설명서---

<사용법>
a=ppomppu("힙합")
url_Q=a.url_scraper()
results=a.multi_scraper(url_Q,num)
'''
import argparse
import requests
import datetime
from multiprocessing import Process, Queue
from bs4 import BeautifulSoup as bs
from time import sleep
from urllib.parse import urlencode
import csv
import os

class ppomppu(object):
    def __init__(self,query):
        self.query=query
        self.user_agent={'User-agent': 'Mozilla/5.0'}
        self.failed=0
        self.path="/home/mnkang89/jobdong/python_data/crawl_data/ppomppu/"
        #self.path="/home/ubuntu/kms/data/"

    def url_scraper(self):
        url_Q=Queue()
        user_agent = {'User-agent': 'Mozilla/5.0'}
        url_query=urlencode({'keyword':self.query},encoding='euc-kr')
        #base_url='http://m.ppomppu.co.kr/new/search_result.php?category=0&search_type=sub_memo&'+url_query
        base_url='http://m.ppomppu.co.kr/new/bbs_list.php?id=freeboard&category=&search_type=sub_memo&'+url_query

        page=1
        count=1
        while page<50:
            print(page)
            url=base_url+'&page='+str(page)
            print(url)
            
            page_source=requests.get(url,headers=user_agent).text
            tmp=bs(page_source)

            content_len=len(tmp.select('a[class="noeffect"]'))
            content_list=tmp.select('a[class="noeffect"]')
                
            if content_len==0:
                print('finish!')
                break
            
            for i in range(content_len):
                urls=str(tmp.select('a[class="noeffect"]')[i]).split('"')[3].replace('amp;','')
                #text_subject=tmp.select('a[class="noeffect"]')[i].text.strip().split('\n')[0]
                text_number=urls.split('?')[1].split('&')[1].split('=')[1]
                #text_writer=tmp.select('a[class="noeffect"]')[i].text.strip().split('\n')[2]
                #text_time=tmp.select('a[class="noeffect"]')[i].text.strip().split('\n')[3].split('|')[1].strip()
                #repl_len=tmp.select('a[class="noeffect"]')[i].text.strip().split('\n')[1].split('[')[1].split(']')[0]
                
                lst=(count,urls,text_number)
                url_Q.put(lst)
                count+=1
    
            page=page+1
        
        return url_Q

    def worker(self,url_Q,cont_Q,repl_Q,jobs):
        path='/home/mnkang89/jobdong/python_data/crawl_data/'
        csv_content=open(path+"pp_cont_"+self.query+"_2015.csv","w")
        csv_repl=open(path+"pp_repl_"+self.query+"_past.csv","w")
        cw_content=csv.writer(csv_content,delimiter="\t")
        cw_repl=csv.writer(csv_repl,delimiter="\t")

        while True:
            if url_Q.empty():
                print('empty')
                break
            else:
                urls=url_Q.get()

            print(urls)

            query=self.query
            count=urls[0]
            #subject=urls[2]
            number=urls[2]
            #writer=urls[4]
            #time=urls[5]
            #year=time[0:2]

            #repl_len=int(urls[6])
            page_url='http://m.ppomppu.co.kr/new/'+urls[1]
            page_source=requests.get(page_url,headers=self.user_agent).text
            tmp=bs(page_source)

            try:                
                subject=tmp.select('h4')[0].text.split('\n')[1].strip()
                writer=tmp.select('h4')[0].select('div[class=info]')[0].select('span[class=ct]')[0].text
                time=tmp.select('h4')[0].select('div[class=info]')[0].select('span[class=hi]')[0].text.split('|')[1].strip()
                repl_len=len(tmp.select('textarea'))

                content=tmp.select('div[id="KH_Content"]')[0].text
                content=replace_all(content)
                cont_row=(number,subject,writer,time,content,query)
                cw_content.writerow(cont_row)
                cont_Q.put(cont_row)

                for i in range(repl_len):
                    tmp_repl=tmp.select('textarea')[i].text.strip()
                    tmp_repl=replace_all(tmp_repl)
                    repl_row=(number,time,tmp_repl,query)
                    cw_repl.writerow(repl_row)
                    repl_Q.put(repl_row)

            except Exception as error:
                print(error)
                self.failed+=1
                pass

            failed=self.failed
            percent=round((count/jobs)*100,2)
            print("[job: ",count,"] [fail: ",failed,"]","[percent: ",percent,"]")

        return


    def multi_scraper(self,url_Q,pro_num):
        #file open
        cont_Q=Queue()
        repl_Q=Queue()
        #self.writing_f()
        jobs=url_Q.qsize()
        process_list=list()

        for pro in range(1,pro_num+1):
            i=Process(target=self.worker, args=(url_Q,cont_Q,repl_Q,jobs,))
            process_list.append(i)
            i.start()

        for i in range(pro_num):
            process_list[i].join()

        print('end~!')

        path=self.path
        dirs=['past','2012','2013','2014','2015']
        for i in range(len(dirs)):
            directory=self.path+dirs[i]
            if not os.path.exists(directory):
                os.mkdir(directory)

        csv_content_past=open(path+"past/pp_cont_"+self.query+"_past.csv","w")
        csv_content_2012=open(path+"2012/pp_cont_"+self.query+"_2012.csv","w")
        csv_content_2013=open(path+"2013/pp_cont_"+self.query+"_2013.csv","w")
        csv_content_2014=open(path+"2014/pp_cont_"+self.query+"_2014.csv","w")
        csv_content_2015=open(path+"2015/pp_cont_"+self.query+"_2015.csv","w")
        csv_repl_past=open(path+"past/pp_repl_"+self.query+"_past.csv","w")
        csv_repl_2012=open(path+"2012/pp_repl_"+self.query+"_2012.csv","w")
        csv_repl_2013=open(path+"2013/pp_repl_"+self.query+"_2013.csv","w")
        csv_repl_2014=open(path+"2014/pp_repl_"+self.query+"_2014.csv","w")
        csv_repl_2015=open(path+"2015/pp_repl_"+self.query+"_2015.csv","w")

        cw_content_past=csv.writer(csv_content_past,delimiter="\t")
        cw_content_2012=csv.writer(csv_content_2012,delimiter="\t")
        cw_content_2013=csv.writer(csv_content_2013,delimiter="\t")
        cw_content_2014=csv.writer(csv_content_2014,delimiter="\t")
        cw_content_2015=csv.writer(csv_content_2015,delimiter="\t")
        cw_repl_past=csv.writer(csv_repl_past,delimiter="\t")
        cw_repl_2012=csv.writer(csv_repl_2012,delimiter="\t")
        cw_repl_2013=csv.writer(csv_repl_2013,delimiter="\t")
        cw_repl_2014=csv.writer(csv_repl_2014,delimiter="\t")
        cw_repl_2015=csv.writer(csv_repl_2015,delimiter="\t")

        while not cont_Q.empty():
            cont_row=cont_Q.get()
            print(cont_row)
            year=cont_row[3][2:4]
            if year=='15':
                cw_content_2015.writerow(cont_row)
            elif year=='14':
                cw_content_2014.writerow(cont_row)
            elif year=='13':
                cw_content_2013.writerow(cont_row)
            elif year=='12':
                cw_content_2012.writerow(cont_row)
            else:
                cw_content_past.writerow(cont_row)

        csv_content_past.close()
        csv_content_2012.close()
        csv_content_2013.close()
        csv_content_2014.close()
        csv_content_2015.close()

        while not repl_Q.empty():
            repl_row=repl_Q.get()
            print(repl_row)
            year=repl_row[1][2:4]
            if year=='15':
                cw_repl_2015.writerow(repl_row)
            elif year=='14':
                cw_repl_2014.writerow(repl_row)
            elif year=='13':
                cw_repl_2013.writerow(repl_row)
            elif year=='12':
                cw_repl_2012.writerow(repl_row)
            else:
                cw_repl_past.writerow(repl_row)

        csv_repl_past.close()
        csv_repl_2012.close()
        csv_repl_2013.close()
        csv_repl_2014.close()
        csv_repl_2015.close()

        return



def replace_all(content):
    replace_dic=['\n','\r','\t']
    for i in replace_dic:
        content=content.replace(i,'')
    return content


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--query",action="store",dest="query",required=True)
    parser.add_argument("--pronum",action="store",dest="pronum",type=int,required=True)

    given_args=parser.parse_args()
    query=str(given_args.query)
    pronum=given_args.pronum

    a=ppomppu(query)
    url_Q=a.url_scraper()
    a.multi_scraper(url_Q,pronum)














