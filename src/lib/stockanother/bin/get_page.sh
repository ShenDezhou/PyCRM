if [ $# -lt 2 ]; then
	echo "Usage: sh $0 input(urllist) output(result)"
	exit -1
fi

urllist=$1;  output=$2;


# ���ַ�ʽ�õ���xpage��zip��ʽ ����ͨ�� get_html_from_db.py ����
cat $urllist | awk -F'\t' '{print $1}' | ./bin/dbnetget -i url -o dd -d csum -df st -l conf/offsum576 -pf $output

# ���ָ�ʽ�õ���xpage ��Ҫanti-spam����
#cat $urllist | ./bin/dbnetget -df cp -i url -o dd -d csum -l conf/offsum576 -pf $output
