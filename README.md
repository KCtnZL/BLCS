# BLCS漫画爬取

## 先贴上一张即将爬取的网页重要部分截图
![image](https://github.com/1jone/BLCS/blob/master/images/blcs00.png)

## 本项目主要使用的Python模块
```python
import requests
import os
from bs4 import BeautifulSoup
import pandas as pd
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
```

## 在这里先说下为什么要用到selenium
   * selenium是一个web自动测试工具
   * 使用selenium可以模拟实际中的JS操作
   * 该网站需要使用到js操作，不然没法获取所需图片的链接（下面将会给出）
### 注：使用selenium时切勿忘记安装driver
   * Chrome游览器安装chromedriver
   * Firefox游览器安装geckodriver

## 下面说一说爬取的流程

### 首先要请求并获取到首页的源码内容，之后过滤出每个章节的各项信息

```Python
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
```
上面代码中获取所需信息的方式是使用find（）或者find_all()的方法进行获取，其实还有很多不同的获取方法。比如正则表达式、xpth提取、css提取  
上面代码有个不好的地方时使用了太多for循环嵌套，可能会影响代码执行的效率

### 接下来需要审查每个章节的源码结构，并提取图片链接

在审查页面元素时发现有两个问题：

1、页面有“分页阅读”和“下拉阅读”两种方式：采用不同方式意味着，爬虫要加载的页面数量不同
![image](https://github.com/1jone/BLCS/blob/master/images/blcs06.png)

2、在游览器中使用调试工具查看元素信息时，可以找到图片链接；但是当查看页面的整个响应源码时却没有图片的链接

![image](https://github.com/1jone/BLCS/blob/master/images/blsc01.png)

![image](https://github.com/1jone/BLCS/blob/master/images/blsc02.png)

解决上面的问题需要用到selenium，它可以打开游览器进行请求并模拟点击操作

```python
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
```
执行流程：先获取“下拉阅读”标签位置，之后执行click（），使得所有图片都加载到一个页面中。接下来用 
         `browser.execute_script('window.scrollTo(0,document.body.scrollHeight)')` 来执行进度条拖拽到底部（需要执行两次），这样所有图片链接
         加载完成。最后使用正则来提取图片链接，返回链接表
         
### 接下来就是下载图片了

```python
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
```
使用最简洁的读写文件来下载图片：请求url->将响应内容写入.jpg文件中

### 看下运行的过程以及结果

![image](https://github.com/1jone/BLCS/blob/master/images/blcs03.png)

![image](https://github.com/1jone/BLCS/blob/master/images/blcs04.png)

![image](https://github.com/1jone/BLCS/blob/master/images/blcs05.png)

### 更多的selenium操作请查看手册
https://selenium-python.readthedocs.io/
