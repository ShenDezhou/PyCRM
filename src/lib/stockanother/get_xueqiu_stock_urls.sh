

# ɨ���ȡ����shop urls
cd /search/money/
	
	sh -x bin/get_pattern_url.sh conf/pattern_xueqiu_conf 1>log/xueqiu.stock.std 2>log/xueqiu.stock.err

cd -


# ɨ���ȡ�������̵�crumb
sh -x bin/get_dianping_shop_crumb.sh 1>log/xueqiu.crumb.std 2>log/xueqiu.crumb.err


