# -*- coding:utf-8 -*-
import codecs
import os
import pymysql


class DATA_BASE_CONFIG:
    URL=""
    USERNAME = ""
    PASSWORD = ""
    # 是否开启驼峰写法
    CAMEL_STYLE=True
    TARGET_TABLE_NAME = ""

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
    # 表名
    table_name = None
    # 字段列表
    field_list = None
    # 包名
    package_name = None

    def __init__(self,table_name):
        self.table_name = table_name

    def add_column(self,field):
        if self.field_list is None:
            self.field_list = []
        self.field_list.append(field)


def getConnection():
    pass

def fillAllTaleData(tablenameList,tableData):
    pass

def generateTableData():
    pass


if __name__ == "__main__":
    print("START GENERATOR ...")
    pass
    print("MISSION COMPLETE")