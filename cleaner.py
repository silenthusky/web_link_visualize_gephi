# encoding: utf-8

#Author Ambulong zeng.ambulong@gmail.com

import json, hashlib, sys

reload(sys)
sys.setdefaultencoding('utf8')

domain = "jandan.net" #目标站点域名

#set maximum recursion depth
sys.setrecursionlimit(1000000)

class cleaner(object):
	def __init__(self, dom):
		self.domain = dom
		self.sides = []
		self.nodes = []
		self.nlog = [] #记录节点
		self.slog = [] #记录边
		self.target = "http://"+domain+"/"
		super(cleaner, self).__init__()
	
	#读取文件内容
	def readfile(self, filename):
		file_object = open(filename)
		text = ''
		try:
			text = file_object.read()
		except:
			text = ''
		finally:
			file_object.close()
		return text
	
	#获取字符串MD5
	def md5(self, string):
		string = str(string).decode('utf-8')
		md5 = hashlib.md5(string.encode('utf-8')).hexdigest()
		return md5
	
	#获取节点
	def getNodes(self, url):
		nodes = []
		if not url:
			return nodes
		
		url = url[7:].replace('?','/').replace('&','/') #去除开头的http://，并替换?与&
		slash_arr = url.split('/')
		
		prei = ''
		for i in range(len(slash_arr)):
			slash_arr[i] = prei+'_'+slash_arr[i]
			prei = slash_arr[i]
		return slash_arr
		
	#生成节点表格
	def genNodeTable(self, data, url):
		uhash = self.md5(url)
		
		if uhash in self.nlog:
			return
		self.nlog.append(uhash)
		
		
		nodes = self.getNodes(url) #获取节点
		for node in nodes:
			item = self.md5(node)+"\t"+node
			self.nodes.append(item)
			print item
		
		if data.has_key(uhash):
			if len(data[uhash]) <= 0:
				return
			for u in data[uhash]:
				self.genNodeTable(data, u)
	
	#生成边表格
	def genSideTable(self, data, url, parent_url=''):
		uhash = self.md5(url)
		puhash = self.md5(parent_url)
		
		if uhash in self.slog:
			return
		self.slog.append(uhash)
		
		unodes = self.getNodes(url)
		punodes = self.getNodes(parent_url)
		
		
		if len(punodes) > 0:
			#将前URL的最后一个节点作为当前第一个节点
			unodes.insert(0, punodes.pop()) 
		
		for i in range(len(unodes)):
			if i >= len(unodes)-1:
				break
			side = self.md5(unodes[i])+"\t"+self.md5(unodes[i+1])
			self.sides.append(side)
			print side
		
		if data.has_key(uhash):
			if len(data[uhash]) <= 0:
				return
			for u in data[uhash]:
				self.genSideTable(data, u, url)
	
	def save2file(self, fname, text):
		file_object = open(fname, 'w')
		file_object.write(text)
		file_object.close()
	
	def saveNodeTable(self):
		filename = self.domain+".nodetable.csv"
		text = "id\tlabel\tweight\n"
		for node in self.nodes:
			text = text+node+"\t"+"1"+"\n"
		self.save2file(filename, text)
	
	def saveSideTable(self):
		filename = self.domain+".sidetable.csv"
		text = "source\ttarget\tweight\n"
		for side in self.sides:
			text = text+side+"\t"+"1"+"\n"
		self.save2file(filename, text)
	
	#执行入口     
	def run(self):
		filename = self.domain+'.json'
		text = self.readfile(filename)
		if not text:
			print 'Readfile error!'
			return False
		try:
			json_arr = json.loads(text)
		except:
			print 'Json decode error!'
			return False
		
		#print text
		index = self.md5(self.target)
		if not json_arr.has_key(index):
			print 'Index is gone'
			return False
		
		self.genNodeTable(json_arr, self.target)
		self.genSideTable(json_arr, self.target)
		
		self.saveNodeTable()
		self.saveSideTable()
		

if __name__ == '__main__':
	cleaner(domain).run()
