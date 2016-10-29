# -*- coding: utf-8 -*-
__author__ = 'pleasurelong@foxmail.com'
import tornado.gen

class DataTable():

    def __init__(self, columns=[], table='', indexcolumn='', sortcol='', req=None, where='', 
                rowcount='', searchcolumns='', isexport=False, isprint=False):
        self.resultData = None
        self.cadinalityFiltered = 0
        self.cardinality = 0

        # Array of database columns which should be read and sent back to DataTables
        self._columns = columns
        # Indexed column (used for fast and accurate table cardinality)
        self._indexColumn = indexcolumn
        # DB table to use
        self._sTable = table
        self._sortCol = sortcol
        self._requests = req
        self._MAXLENGTH = 20
        self._MAXDOWNLOAD_LENGTH = 30000
        self._bDownload = isexport or isprint

        self._where = where

        self._rowcount = rowcount

        self._searchColumns = searchcolumns.split(',') if searchcolumns else []

    def __output_dic__(self, res):

        output = {}
        output["draw"] = int(self._requests.get_argument('draw', 0))
        output["recordsTotal"] = self.cardinality
        output["recordsFiltered"] = self.cadinalityFiltered
        data = []
        output["data"] = data
        res['output'] = output
        if not self.resultData or len(self.resultData) <= 0:
            return output
        else:
            for row in self.resultData:
                rowdic = {}
                for i in range(len(self._columns)):
                    #处理as
                    tmpcomns = self._columns[i].split(' ')[-1].split('.')[-1]
                    # pos = tmpcomns.rfind('AS ')
                    # if pos != -1:
                    #     self._columns[i] = tmpcomns[pos+3:]
                    rowdic[tmpcomns] = str(row[tmpcomns]).replace('"', '\\"')
                data.append(rowdic)

    def __output_str__(self, res):
        output = '{'
        output += '"draw": '+str(int(self._requests.get_argument('sEcho', 0)))+', '
        output += '"recordsTotal": '+str(self.cardinality)+', '
        output += '"recordsFiltered": '+str(self.cadinalityFiltered)+', '
        output += '"data": [ '
        if not self.resultData or len(self.resultData) <= 0:
            output += ']}'
        else:
            for row in self.resultData:
                output += '{'
                for i in range(len(self._columns)):

                    #处理as
                    tmpcomns = self._columns[i].split(' ')[-1].split('.')[-1]
                    # pos = tmpcomns.rfind('AS ')
                    # if pos != -1:
                    #     self._columns[i] = tmpcomns[pos+3:]


                    if self._columns[i] == "version":
                # 'version' specific formatting
                        if row[self._columns[i]] == "0":
                            output += '"-",'
                        else:
                            output += '"'+str(self._columns[i])+'":'
                            output += '"'+str(row[self._columns[i]])+'",'
                    else:
                # general formatting
                        output += '"'+str(self._columns[i])+'":'
                        output += '"'+str(row[self._columns[i]]).replace('"', '\\"')+'",'

                # Optional Configuration:
                # If you need to add any extra columns (add/edit/delete etc) to the table, that aren't in the
                # database - you can do it here
                output = output[:-1]
                output += '},'
            output = output[:-1]
            output += '] }'
        res['output'] = output

    @tornado.gen.coroutine
    def query(self, res):

        # Get the data
        #conn = self._requests.get_db_conn()
        #yield conn.connect()
        sql = """
            SELECT SQL_CALC_FOUND_ROWS %(columns)s
            FROM   %(table)s %(where)s %(order)s %(limit)s""" % dict(
                columns=', '.join(self._columns), table=self._sTable,
                where=self.filtering(),
                order = self.ordering(),
                limit=self.paging()
            )
        sql = ''.join(sql.split('\n'))
        sql = sql.replace('%', '%%')
        dataCursor = yield self._requests.query_db(sql)
        self.resultData = dataCursor
        results = yield self._requests.query_db("""SELECT FOUND_ROWS()""")
        self.cadinalityFiltered = results[0]['FOUND_ROWS()']
        
        # sql = "SELECT COUNT(%s) FROM %s"% (self._indexColumn, self._sTable)
        # sql = sql.replace('%', '%%')
        # results = yield self._requests.query_db(sql)
        # self.cardinality = results[0]['COUNT(%s)'% self._indexColumn]
        self.cardinality = self.cadinalityFiltered
        self.__output_dic__(res)

    def filtering(self):
        filter = ""
        if self._requests.get_argument('search[value]', '') and self._searchColumns:
            filter = "WHERE "
            for s in self._searchColumns:
                #处理as
                # tmpcomns = self._columns[i].split(' ')[-1].split('.')[-1]
                # pos = tmpcomns.rfind('AS ')
                # if pos != -1:
                #     self._columns[i] = tmpcomns[pos+3:]
                filter += "%s LIKE '%%%s%%' OR " % (s, self._requests.escape_string(self._requests.get_argument('search[value]', '')))
            filter = filter[:-3]

        if not self._where:
            return filter
        if not filter and self._where:
            filter = "WHERE %s" % (self._where)
            return filter
        if filter and self._where:
            filter = filter[:5] + ' ( ' + filter[5:] + " ) AND %s" % (self._where)
            return filter

    def ordering(self):
        order = ""
        if self._requests.get_argument('order[0][column]', '') != "":
            order = "ORDER BY  "
            #处理as
            i = int(self._requests.get_argument('order[0][column]'))
            tmpcomns = self._columns[i].split(' ')[-1].split('.')[-1]
            # pos = tmpcomns.rfind('AS ')
            # if pos != -1:
            #     self._columns[i] = tmpcomns[pos+3:]
            order += "%s %s, " % (tmpcomns, self._requests.get_argument('order[0][dir]', ''))
        elif self._sortCol:
            order = "ORDER BY  " + self._sortCol + " , "
        return order[:-2]

    #
    # paging
    # Create the 'LIMIT' part of the SQL string
    #
    def paging(self):
        if self._bDownload:
            return 'LIMIT 0, ' + str(self._MAXDOWNLOAD_LENGTH)
        limit = ""
        if (self._requests.get_argument('start', "") != "") and (self._requests.get_argument('length', -1) != -1) and self._requests.get_argument('length', 51) > self._MAXLENGTH:
            limit = "LIMIT %s, %s" % (self._requests.get_argument('start', 0), self._requests.get_argument('length', 0))
            return limit
        if (self._requests.get_argument('draw', "") != ""):
            limit = "LIMIT %s, %s" % (int(self._requests.get_argument('draw', 0)) * self._MAXLENGTH, self._MAXLENGTH)
            return limit
        return "LIMIT 0, 20"


