#encoding:utf-8
import requests
import chardet
import urllib
import os
import threading
from multiprocessing import Queue
from bs4 import BeautifulSoup
import pandas as pd
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

order=''  #需要下载的章节序号
local=''  #图片的存储路径

#下载图片
def download(urls):
	global local
	i=1
	for url in urls:
		r = requests.get(url)
		with open(local+str(i)+'.jpg','wb') as pic:
			pic.write(r.content)
		i+= 1
	print("图片下载完成")

#创建目录
def mk_dir(title):
	global local
	local=os.getcwd()
	try:
		os.mkdir(local+'\\'+'blcs')
		print("blcs目录创建完成！")   
	except:
		print("blcs目录已经存在！")

	local=local+'\\'+'123'+'\\'

	try:
		os.mkdir(local+title)  #图片的绝对存储地址
		print("%s目录创建完成!"%title)
	except:
		print("%s目录已经存在"%title)
	finally:
		local+=title+'\\'

#使用request获取首页
def get_soup(href):
	user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
	headers = {'User-Agent':user_agent}
	r=requests.get(href,headers=headers)
	r.encoding=chardet.detect(r.content)['encoding']
	soup=BeautifulSoup(r.text,'html.parser')
	return(soup)

#获取章节目录
def get_order(soup):
	order=pd.DataFrame(columns=["title_w","src_w"])
	for w998 in soup.find_all(class_="w998 bc cf"):
		for w728 in w998.find_all(class_="fl w728"):
			for chapters in w728.find_all(id="chapters"):
				for comic_chapters in chapters.find_all(class_="comic-chapters"):
					for clearfix in comic_chapters.find_all(class_="chapter-body clearfix"):
						for a in clearfix.ul.find_all('a'):
							order_ww=a.find('span').get_text()
							src_ww=r'https://www.36mh.com/'+a.get('href')
							count = {"title_w":order_ww,"src_w":src_ww}
							order = order.append(count,ignore_index=True)
	return(order)

#获取图片链接
def get_src(url_order):
	browser = webdriver.Chrome()
	wait = WebDriverWait(browser,10)
	browser.get(url_order)
	submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#chapter-scroll')))
	submit.click()
	time.sleep(5)
	browser.execute_script('window.scrollTo(0,document.body.scrollHeight)')
	time.sleep(5)
	browser.execute_script('window.scrollTo(0,document.body.scrollHeight)')
	urls = re.findall('<im.*?src="(.*?)".*?style="">',browser.page_source)
	browser.close()
	return urls

#返回图片链接表
def get_order_list(order):
	order_to_json=order.to_json(orient='index')
	order_json=json.loads(order_to_json)
	num_download=input("请输入要下载的序号：")
	src=order_json[num_download]['src_w']
	title=order_json[num_download]['title_w']
	lists=get_src(src)
	return title,lists

#主函数方法
def main():
	global num_download
	global title
	url=r'https://www.36mh.com/manhua/bailianchengshen/'
	soup=get_soup(url)
	order=get_order(soup)
	print(order)
	#选择查看隐藏的目录还是直接选择某个目录下载
	num_1=input("选择查看隐藏目录请按1，直接下载请按2！")
	if num_1=='1':
		start=input("输入起始目录号：")
		end=input("输入结束目录号：")
		print(order['order_w'][int(start):int(end)+1])
		title,lists=get_order_list(order)
	else:
		title,lists=get_order_list(order)
	mk_dir(title)
	download(lists)

#代码执行体
if __name__ == '__main__':
	main()