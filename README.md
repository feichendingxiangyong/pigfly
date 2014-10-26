通过远程vps搭建web服务器代理实现google搜索结果页面重写。直通原网站链接 http://www.xxx.com — Edit

下面开始干活。

解决思路：

	* 搭建远程vps web服务器
	
	* 运行pigfly搜索器
 	
	* 域名gg.yunside.com解释到pigfly服务器
	
	* 搜索关键字
	
	* 返回结果链接
	
	* 享受美好生活！

技术路线：

    * tornado作为web服务器
    
    * nginx作为反向代理

By Shengli Hu 2014-10-24
