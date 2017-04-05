if [ $# -lt 2 ]; then
	echo "Usage: sh $0 input(urllist) output(result)"
	exit -1
fi

urllist=$1;  output=$2;


# 这种方式得到的xpage是zip格式 可以通过 get_html_from_db.py 解析
cat $urllist | awk -F'\t' '{print $1}' | ./bin/dbnetget -i url -o dd -d csum -df st -l conf/offsum576 -pf $output

# 这种格式得到的xpage 需要anti-spam解析
#cat $urllist | ./bin/dbnetget -df cp -i url -o dd -d csum -l conf/offsum576 -pf $output
