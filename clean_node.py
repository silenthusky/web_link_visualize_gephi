# encoding: utf-8

#Author Ambulong zeng.ambulong@gmail.com

import json, hashlib, sys

reload(sys)
sys.setdefaultencoding('utf8')

domain = "jandan.net" #目标站点域名

class cleaner(object):
	def __init__(self, dom):
		self.domain = dom
		self.nodes = []
	
	def save2file(self, fname, text):
		file_object = open(fname, 'w')
		file_object.write(text)
		file_object.close()
	
	def saveNodeTable(self):
		filename = self.domain+".clean.nodetable.csv"
		text = "id\tlabel\tweight\n"
		for node in self.nodes:
			text = text+node+"\n"
		self.save2file(filename, text)
	
	#执行入口     
	def run(self):
		filename = self.domain+'.nodetable.csv'
		try:
			f = open(filename)
		except:
			print 'Open file error!'
			return False
		
		line = f.readline()
		
		while line:
		    uhash,url,weight = line.split("\t")
		    if url == '_jandan.net' or url == '_jandan.net_':
		    	weight = 100
		    if url.find('_jandan.net_author') == 0:
		    	weight = 10+len(url.split('_'))-3
		    elif url.find('_jandan.net_tag') == 0:
		    	weight = 20+len(url.split('_'))-3
		    else:
		    	weight = 0
		    
		    item = uhash+"\t"+url+"\t"+str(weight)
		    self.nodes.append(item)
		    print item
		    
		    line = f.readline()

		f.close()
		
		self.saveNodeTable()

		

if __name__ == '__main__':
	cleaner(domain).run()
