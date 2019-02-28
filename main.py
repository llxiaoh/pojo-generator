# -*- coding:utf-8 -*-
import codecs
import os
import pymysql
import traceback


class DATA_BASE_CONFIG:
    HOST = ""
    DB = ""
    USERNAME = ""
    PASSWORD = ""
    # 是否开启驼峰写法
    CAMEL_STYLE=True
    TARGET_TABLE_NAME = ""
    GET_TABLE_FIELDS_SQL = "show full fields from %s";

class Field:
    column_name = None;
    def __init__(self,column_name):
        self.column_name = column_name
    def get_column_name(self):
        return self.column_name
    def get_property_name(self):
        if self.column_name is None:
            raise Exception("字段未赋值")
        if DATA_BASE_CONFIG.CAMEL_STYLE:
            return self.column_name.replace("_","").title()
        return self.column_name

class TableData:
    table_name = None
    field_list = None
    package_name = None
    def __init__(self,table_name):
        self.table_name = table_name
    def add_column(self,field):
        if self.field_list is None:
            self.field_list = []
        self.field_list.append(field)

def getConnection():
    return pymysql.connect(host=DATA_BASE_CONFIG.HOST,
                           db=DATA_BASE_CONFIG.DB,
                           user=DATA_BASE_CONFIG.USERNAME,
                           passwd=DATA_BASE_CONFIG.PASSWORD,
                           charset="utf8",
                           use_unicode=True,)

def fillAllTaleData(tablenameList,tableData):
    try:
        connection = getConnection()
        cursor = connection.cursor()
        cursor.execute(DATA_BASE_CONFIG.GET_TABLE_FIELDS_SQL)
        result = cursor.fetchall()
        if result is None:
            raise Exception("获取表字段异常")
        for field_row in result:
            print(field_row[0])
    except:
        traceback.print_exc()
    pass

def generateTableData():
    pass

def generate_java_pojo():
    pass

def generate_mybatis_sql():
    pass

if __name__ == "__main__":
    print("START GENERATOR ...")
    pass
    print("MISSION COMPLETE")