import Queue
import argparse
import requests
import datetime
from bs4 import BeautifulSoup as bs

class naver(object):
	def __init__(self,query,start,end,number):
		self.query=str(query)
		self.start=str(start)
		self.end=str(end)
		self.user_agent={'User-agent': 'Mozilla/5.0'}
		self.number=number
		self.jobs_Queue=self.job_maker()
		
	def job_maker(self):
		user_agent = self.user_agent
		query=self.query
		start_date=self.start
		end_date=self.end

		inputs=Queue.Queue()		        
		url="http://cafeblog.search.naver.com/search.naver?where=post&query="+query+"&ie=utf8&st=sim&sm=tab_opt&date_from="+start_date+"&date_to="+end_date+"&date_option=6&srchby=all&dup_remove=1&post_blogurl=&post_blogurl_without=&nso=so%3Ar%2Ca%3Aall%2Cp%3Afrom"+start_date+"to"+end_date+"&mson=0"

		page_source=requests.get(url,headers=user_agent).text

		try:
			total=int(bs(page_source).find('span','title_num').text.split('/')[1].replace(' ','')[:-1].replace(',',''))
		except:
			print("No results....")
			returnx

		print("dddddddddddddddddddddddddddddddddddddddddddddd")
		print(total)
		print("dddddddddddddddddddddddddddddddddddddddddddddd")
		number=self.number
		assigned=total/number

		bin_list=range(0,total,assigned)

		new_list=[]
		for i in bin_list:
			rounded=int(round(i,-1))+1
			new_list.append(rounded)

		if len(new_list)==number+1:
			new_list.pop()

		for i in range(1,number+1):
			if i==number:
				job=range(new_list[i-1],int(round(total,-1)-9),10)
				job.append(int(round(total,-1)-9))

			else:
				job=range(new_list[i-1],new_list[i]-9,10)
			inputs.put(job)
		return inputs

	def scraper(self,worker=1):
		user_agent = self.user_agent
		query=self.query
		start_date=self.start
		end_date=self.end

		try:
			for i in range(worker):
				jobs=self.jobs_Queue.get(True,2)
		except:
			print("Empty Queue....")
			return

		url="http://cafeblog.search.naver.com/search.naver?where=post&query="+query+"&ie=utf8&st=sim&sm=tab_opt&date_from="+start_date+"&date_to="+end_date+"&date_option=6&srchby=all&dup_remove=1&post_blogurl=&post_blogurl_without=&nso=so%3Ar%2Ca%3Aall%2Cp%3Afrom"+start_date+"to"+end_date+"&mson=0"

		count=1
		for i in jobs:
			page_url=url+"&start="+str(i)
			page_source=requests.get(page_url,headers=user_agent).text
			tmp = bs(page_source)

			tmp_list = tmp.find_all('dl')
			for blog_tmp in tmp_list:
				try:
					blog_date = blog_tmp.find('dd','txt_inline').text.split(' ')[0]
				except :
					continue
				blog_url=blog_tmp.find('span','inline').text.split(' ')[1]
				print('[',count,'] ',blog_url)
				count+=1



if __name__=="__main__":
	parser=argparse.ArgumentParser(description="crawler")
	parser.add_argument("--query",action="store",dest="query",required=True)
	parser.add_argument("--start",action="store",dest="start",required=True)
	parser.add_argument("--end",action="store",dest="end",required=True)
	parser.add_argument("--number",action="store",dest="number",type=int,required=True)
	parser.add_argument("--worker",action="store",dest="worker",type=int,required=True)
	given_args=parser.parse_args()
	
	query=str(given_args.query)
	start=str(given_args.start)
	end=str(given_args.end)
	number=given_args.number
	worker=given_args.worker

	crawler=naver(query,start,end,number)
	crawler.scraper(worker)

	





