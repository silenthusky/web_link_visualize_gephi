# CMS(内容管理系统)数据可视化分析

* 通过URL来分类CMS，网站是否有多套不同系统
* 通过代码中的require/include来分类CMS，CMS结构

* 测试 Wordpress
* 测试 Discuz

## 介绍

CMS(Content Management System, 中文：内容管理系统)是指在一个合作模式下，用于管理工作流程的一套制度。该系统可应用于手工操作中，也可以应用到电脑或网络里。作为一种中央储存器（central repository），内容管理系统可将相关内容集中储存并具有群组管理、版本控制等功能。版本控制是内容管理系统的一个主要优势。[1](https://zh.wikipedia.org/wiki/内容管理系统) 通俗理解就是可用来管理文章、图片、文献等内容的系统，常见的CMS类型有门户或商业网站的发布和管理系统、个人网站系统、Wiki等。本文将以常见的两套CMS系统，Wordpress和Discuz为例进行分析。

* 通过URL来分类CMS/网站是否有多套不同系统

  我们都知道常见的WEB页面是由HTML标签组成的，一个正常的WEB页面内通常会有外部载入资源（CSS文件、JS文件、图片等）和超链接，而且不同CMS都会有独一无二的资源调用和页面链接（正常情况下），因此我们可以将这些作为CMS系统的指纹信息对系统进行分类和识别。同时我们也可以通过生成的关系图来判断网站是否使用了多套不同的系统。

## 思路

### 爬虫

我们先自己写个简单的网页爬虫，可以从网站的首页开始抓取页面源代码，同时可以设置抓取的页面深度(页面深度：如首页是第一级，首页指向的内部链接为第二级，第二级指向的链接为第三级，以此类推)。
要抓取的内容包括CSS和JS文件，因为该两类文件内可能继续调用外部资源。

该爬虫需要以下功能：

1. 抓取页面，可设置抓取超时时间。
2. 提取页面标签内的`src`, `url`, `href`属性，并对属性进行标注分类（如：JS文件、CSS文件、超链接），同时过滤掉外部链接，无关链接。
3. 将抓取的页面保存。

### 分析

我们默认将首页作为第一个节点，链接内的相对路径作为第二个节点，若链接中存在参数，则将参数作为第三个节点。

如存在如下页面：

```
<!--URL: /index.php-->
<html>
<body>
<a href="./index.php?mod=login">Login</a>
<a href="./index.php?mod=threads&page=1">Page 1</a>
<a href="./index.php?page=2&mod=threads">Page 2</a>
<a href="./threads/page/3">Page 3</a>
<a href="./threads/29834">Thread title</a>
<body>
</html>
```

则存在如下关系：

index.php--mod=login
index.php--mod=threads&page=1
index.php--page=2&mod=threads
index.php--threads/page/3
index.php--threads/29834

