# 将新扫出来的数据拷贝到110机器上，去分发抓取解析页面
function scpShopurlsToAliyun() {
	srcFile=data/crumb/
	host=114.215.101.25
	destPath=/search/money/data/
	PASSWD=Sougou123
	#scp data/crumb/dianping.url.types 10.134.96.110:/search/fangzi/ServiceApp/Dianping/Scan/data/shop_urls.types
      ./bin/expect/scp_dir.exp "$srcFile" "$host:$destPath" $PASSWD
}
scpShopurlsToAliyun
