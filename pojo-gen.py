#encoding:utf-8
'''
    V 1.0 自动生成java类以及相应的增删改查工具
    在DATA_BASE_CONFIG 下配置数据库信息，以及制定的表即可
'''
import codecs
import os
import pymysql
import traceback
import sys
from generate_po import generate_java_pojo
from generate_mybatis_xml import generate_mybatis_xml
from generate_dao import generate_java_dao
reload(sys)
sys.setdefaultencoding("utf-8")

class DATA_BASE_CONFIG:
    HOST = "127.0.0.1"
    DB = "test"
    USERNAME = ""
    PASSWORD = ""
    CAMEL_STYLE=True
    TARGET_TABLE_NAME = ""
    GET_TABLE_FIELDS_SQL = "show full fields from %s";
    PACKAGE_NAME = ""
    DIR = "./gen/"
    GET_SQL_SEESION_CODE = ""
    DAO_IMPORTS = '''\r\n
'''


class Field:
    column_name = None
    column_type = None
    column_desc = None
    pri = False
    def __init__(self,column_name,column_type,column_desc,column_pri):
        self.column_name = column_name
        self.column_type = column_type
        self.column_desc = column_desc
        if column_pri.find("PRI") > -1:
            self.pri = True
    def get_column_name(self):
        return self.column_name
    def get_column_type(self):
        return self.column_type
    def get_column_java_property(self):
        return generate_java_type(self.column_type)
    def get_property_name(self):
        if self.column_name is None:
            raise Exception("字段未赋值")
        if DATA_BASE_CONFIG.CAMEL_STYLE:
            return getCamelName(self.column_name)
        return self.column_name
    def get_comment(self):
        if self.column_desc is None:
            return ""
        return self.column_desc
    def get_pri_key(self):
        return self.pri

class TableData:
    table_name = None
    field_list = None
    package_name = None
    def __init__(self,table_name,package_name):
        self.table_name = table_name
        self.package_name = package_name
    def add_column(self,field):
        if self.field_list is None:
            self.field_list = []
        self.field_list.append(field)
    def get_table_name(self):
        return self.table_name
    def get_class_name(self):
        if DATA_BASE_CONFIG.CAMEL_STYLE:
            content = ""
            for i in self.table_name.split("_"):
                content += i.title()
            return content+"PO"
        return self.table_name
    def get_field_list(self):
        return self.field_list
    def get_namespace(self):
        return self.package_name+self.get_class_name()
    def get_select_method_id(self):
        return "select"+self.get_class_name()
    def get_result_type(self):
        return self.package_name+"."+self.get_class_name()
    def get_delete_method_id(self):
        return "delete"+self.get_class_name()
    def get_update_method_id(self):
        return "update"+self.get_class_name()
    def get_insert_method_id(self):
        return "insert"+self.get_class_name()
    def get_pri_type(self):
        if self.field_list is None:
            raise Exception("没有主键")
        for field in self.field_list:
            if field.get_pri_key():
                return field.get_column_java_property()
    def get_pri_name(self):
        if self.field_list is None:
            raise Exception("没有主键")
        for field in self.field_list:
            if field.get_pri_key():
                return field.get_property_name()

def generate_java_type(obj):
    if obj.find("tinyint") > -1:
        return "byte"
    if obj.find("bigint") > -1 or obj.find("datetime") > -1 or obj.find("timestamp") > -1:
        return "long"
    if obj.find("int") > -1:
        return "int"
    if obj.find("varchar") > -1:
        return "String"
    if obj.find("float") > -1:
        return "float"
    if obj.find("varbinary") > -1:
        return "byte[]"
    raise Exception("未转换类型:%s"%obj)

def getConnection():
    return pymysql.connect(host=DATA_BASE_CONFIG.HOST,
                           db=DATA_BASE_CONFIG.DB,
                           user=DATA_BASE_CONFIG.USERNAME,
                           passwd=DATA_BASE_CONFIG.PASSWORD,
                           charset="utf8",
                           use_unicode=True,)

def generateTableData(table_name):
    try:
        data = TableData(table_name,DATA_BASE_CONFIG.PACKAGE_NAME)
        connection = getConnection()
        cursor = connection.cursor()
        cursor.execute(DATA_BASE_CONFIG.GET_TABLE_FIELDS_SQL%table_name)
        result = cursor.fetchall()
        if result is None:
            raise Exception("获取表字段异常")
        for field_row in result:
            data.add_column(Field(field_row[0],field_row[1],field_row[8],field_row[4]))
        return data
    except:
        traceback.print_exc()

def getCamelName(name):
    r = ""
    for i in name.split("_"):
        r += i.title()
    return r[0].lower()+r[1:]


def get_tables(table_name):
    tables = []
    connection = getConnection()
    if connection is None:
        raise Exception("数据库连接失败")
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES LIKE '%s'"%('%'+table_name+'%'))
        result = cursor.fetchall()
        if result is None:
            raise Exception("未查询到含有[%s]的表"%table_name)
        for row in result:
            tables.append(row[0])
        return tables
    except:
        traceback.print_exc()


if __name__ == "__main__":
    print("START GENERATOR ...")
    tables = get_tables(DATA_BASE_CONFIG.TARGET_TABLE_NAME)
    if tables is None or len(tables) == 0:
        raise Exception("未找到[%s]相关表"%DATA_BASE_CONFIG.TARGET_TABLE_NAME)
    for table in tables:
        data = generateTableData(table)
        generate_java_pojo(data,DATA_BASE_CONFIG.PACKAGE_NAME,DATA_BASE_CONFIG.DIR)
        generate_mybatis_xml(data,DATA_BASE_CONFIG.DIR)
        generate_java_dao(data,DATA_BASE_CONFIG.PACKAGE_NAME,DATA_BASE_CONFIG.GET_SQL_SEESION_CODE,DATA_BASE_CONFIG.DIR,DATA_BASE_CONFIG.DAO_IMPORTS)
    print("MISSION COMPLETE")
