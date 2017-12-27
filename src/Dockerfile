from bangtech/crm_web:fudan

ADD lib/  /search/lib/
ADD tpl/  /search/tpl/
ADD util/ /search/util/
ADD views/ /search/views/
ADD [^s]* /search/
RUN pip install pywxpay
VOLUME ["/search"]
CMD ["python /search/index.py --port=8890"]
