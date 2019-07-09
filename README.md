# BLCS
该代码为了自动下载36漫画网中“百炼成神”的图片
https://www.36mh.com/manhua/bailianchengshen/

主要使用的python第三方库：
  1、request
  2、selenium
  3、bs4

request：
  可以通过get、post的方式请求链接，获取网页源码信息
  
selenium
  如果网站中需要进行一些JS操作，request已经不满足操作需要了。
  selenium将会打开电脑上的游览器，然后进行请求页面，执行JS等操作。
  https://selenium-python.readthedocs.io/
