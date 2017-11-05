# encoding: utf-8

#Author Ambulong zeng.ambulong@gmail.com

import threading, urllib2, hashlib, re, Queue, os, logging, sys, HTMLParser, json

domain = "jandan.net" #目标站点域名
max_level = 4 #抓取页面深度
timeout = 10 #超时时间（单位s）
threads = 10 #最大线程数
log = {} #记录抓取数据
queues = Queue.Queue() #任务队列
queues_adopted = [] #记录已经抓取过的页面
ignore_ext = ['.png', '.gif', '.doc', '.docx', '.ppt', '.pptx', '.jpge', '.log', '.exe', '.gz', '.txt', '.mp3', '.pdf', '.xls', '.xlsx', '.mp4', '.swf', '.ogg', '.bmp', '.jpg', '.rar', '.zip']

def htmldecode(string):
	h = HTMLParser.HTMLParser()
	return h.unescape(string)

#获取目录
def getabsdir(url):
	if url.rfind('/') >= 0:
		return url[0:url.rfind('/')+1]
	else:
		return url

#处理URL
def fixURL(url, pre_url = ''):
	if not pre_url:
		pre_url = 'http://'+domain+'/'
	url = str(url).strip().strip("'").strip('"')
	if url == '':
		return ''
	if url.find('#') >= 0:
		url = url[0:url.find('#')]
	elif re.compile(r'^\w+://|^//', re.IGNORECASE).match(url):
		if re.compile(r'^http://'+domain, re.IGNORECASE).match(url):
			return url
		elif re.compile(r'^//'+domain, re.IGNORECASE).match(url):
			return "http:"+url
	elif url[0:1] == '/':
		return 'http://'+domain+'/'+url[1:]
	elif url[0:1] == '#' or url[0:5] == 'data:':
		return ''
	elif url[0:2] == './':
		return pre_url+url[2:]
	else:
		return pre_url+url

#禁止自动跳转并获取跳转地址
class NoRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        infourl = urllib2.addinfourl(fp, headers, req.get_full_url())
        infourl.status = code
        infourl.code = code
        if headers['location']:
        	return headers['location']
        else:
        	return infourl
        
    http_error_300 = http_error_302
    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302

opener = urllib2.build_opener(NoRedirectHandler())
urllib2.install_opener(opener)

#记录已经抓取过的网页
def addAdopted(url_hash):
	queues_adopted.append(url_hash)

#判断网页是否已经抓取过
def isAdopted(url_hash):
	if url_hash in queues_adopted:
		return True
	else:
		return False
    
class fetchURL(threading.Thread):
	def __init__(self, url, level):
		threading.Thread.__init__(self)
		addAdopted(self.md5(url))
	    	self.url = htmldecode(url)
	    	self.done = False
	    	self.level = level
	    	
	#获取字符串MD5
	def md5(self, string):
		string = str(string).decode('utf-8')
		md5 = hashlib.md5(string.encode('utf-8')).hexdigest()
		return md5
	
	#判断是否站内链接，并将其处理成完整URL
	def fixURL(self, url, pre_url = ''):
		return fixURL(url, pre_url)
	
	#提取内容内的链接
	def getLinks(self, html):
		links = re.findall(r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')" ,html)
		links = links + re.findall(r"(?<=src=\").+?(?=\")|(?<=src=\').+?(?=\')|(?<=src\s=\s\').+?(?=\')" ,html)
		links = links + re.findall(r"(?<=url=\").+?(?=\")|(?<=url=\').+?(?=\')|(?<=url\s=\s\').+?(?=\')|(?<=url\().+?(?=\))|(?<=url\(\').+?(?=\'\))|(?<=url\(\").+?(?=\"\))" ,html)
		tmp = []
		for link in links:
			link = htmldecode(link)
			flink = self.fixURL(link, getabsdir(self.url))
			if flink:
				tmp.append(flink)
		return tmp
        
	def run(self):
		try:
			name, ext = os.path.splitext(self.url)
			#判断文件后缀
			if ext in ignore_ext:
				links = []
			else:
				request = urllib2.Request(self.url)  
				request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)')  
				response = urllib2.urlopen(request, timeout=timeout)  
				#如果是302跳转，跳转地址当作超链接处理(未处理循环重定向)
				if isinstance(response, basestring):
					links = []
					links.append(self.fixURL(response, getabsdir(self.url)))
				else:
					html = response.read()
					#print html
					links = self.getLinks(html)
		except:
			links = []
		print str(self.level) + "\t" + self.md5(self.url)+"\t"+str(len(links))+"\t"+self.url
		log[self.md5(self.url)] = links
		for link in links:
			link = self.fixURL(link, getabsdir(self.url))
			if link:
				if not isAdopted(self.md5(link)) and not isAdopted(self.md5(link+'/')) and self.level < max_level:
					thread = fetchURL(link, self.level + 1)
					queues.put(thread)
		self.done = True
		

class spider(object):
	def __init__(self, target):
		self.target = target
		super(spider, self).__init__()
	
	def startThread(self):
		#初始化线程池
		pool = []
		for i in range(threads):
			pool.append(None)
		
		#处理线程
		while True:
			try:
				thread_num = threads
				for index in range(len(pool)):
					#暂无线程
					if not pool[index] and not queues.empty():
						pool[index] = queues.get()
					#线程未启动
					if pool[index] and not pool[index].isAlive() and pool[index].done == False:
						pool[index].start()
					#线程已经执行完毕
					if pool[index] and not pool[index].isAlive() and pool[index].done == True:
						pool[index] = None
					#计算当前线程数
					if not pool[index]:
						thread_num = thread_num - 1
				#无线程在执行表示已经执行结束
				if thread_num <= 0:
					#print log
					#将数据以json格式保存
					self.save2file(domain+".json", json.dumps(log))
					break
			
				#print "Current Threads Number: "+str(thread_num)
			except KeyboardInterrupt:
				logging.info("Ctrl C - Stopping Client")
				sys.exit(1)
		print 'Done'
		return
	
	def save2file(self, fname, text):
		file_object = open(fname, 'w')
		file_object.write(text)
		file_object.close()
		
	def run(self):
		print "Spider Comming..."
		print "Target: "+self.target
		index = fetchURL(self.target, 1)
		queues.put(index)
		self.startThread()

if __name__ == '__main__':
	target = "http://"+domain+"/"
	spider(target).run()
