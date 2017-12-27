from bangtech/crm_web:fudan

ADD ../src/[^s]* /search/
RUN pip install pywxpay
VOLUME ["/search"]
CMD ["python /search/index.py --port=8890"]
