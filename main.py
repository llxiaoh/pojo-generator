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
reload(sys)
sys.setdefaultencoding("utf-8")

class DATA_BASE_CONFIG:
    HOST = "127.0.0.1"
    DB = "test"
    USERNAME = ""
    PASSWORD = ""
    CAMEL_STYLE=True
    TARGET_TABLE_NAME = "test"
    GET_TABLE_FIELDS_SQL = "show full fields from %s";
    PACKAGE_NAME = "com.demo"

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


def generate_java_type(obj):
    if obj.find("tinyint") > -1:
        return "byte"
    if obj.find("bigint") > -1 or obj.find("datetime") > -1 or obj.find("timestamp") > -1:
        return "long"
    if obj.find("int") > -1:
        return "int"
    if obj.find("varchar") > -1:
        return "String"
    raise Exception("未转换类型:%s"%obj)


def generate_java_pojo_template(java_name,package_name,content,get_set_content):
    template = '''package %s.bean.po

public class %s{
%s

%s
}
'''%(package_name,java_name,content,get_set_content)
    return template

def generate_java_pojo_content_template(java_type,name,explain):
    template = '''
    /** %s */
    private %s %s;
'''%(explain,java_type,name)
    return template

def generate_java_pojo_getset_content_template(java_type,name,explain):
    template = '''
    /** 获取%s */
    public %s get%s(){
        return this.%s;
    }
    /** 设值%s */
    public void set%s(%s %s){
        this.%s = %s;
    }
'''%(explain,java_type,name.title(),name,explain,name.title(),java_type,name,name,name)
    return template

def generate_java_pojo(table_data):
    if table_data is None:
        raise Exception("表数据获取异常")
    class_name = table_data.get_class_name()
    package_name = DATA_BASE_CONFIG.PACKAGE_NAME
    field_list = table_data.get_field_list()
    if field_list is None:
        raise Exception("[%s]表没有字段 "%table_data.get_table_name)
    content = ""
    setget_content = ""
    for field in field_list:
        java_type = field.get_column_java_property()
        name = field.get_property_name()
        comment = field.get_comment()
        content += generate_java_pojo_content_template(java_type,name,comment)
        setget_content += generate_java_pojo_getset_content_template(java_type,name,comment)
    with codecs.open("./%s.java"%class_name,"w+","utf-8") as f:
        f.write(generate_java_pojo_template(class_name,package_name,content,setget_content))


def generate_mybatis_select(method_id,result_type,fields,table_name,pri_key,pri_property):
    template = '''\t<select id="%s" resultType="%s" parameterType="%s">
    \t\tSELECT %s \t\t\tFROM `%s` WHERE `%s`=#{%s};
\t</select>
'''%(method_id,result_type,result_type,fields,table_name,pri_key,pri_property)
    return template

def generate_mybatis_select_pri(method_id,result_type,fields,table_name,pri_key):
    template = '''\t<select id="%sPri" resultType="%s">
    \t\tSELECT %s \t\t\tFROM `%s` WHERE `%s`=#{0};
\t</select>
'''%(method_id,result_type,fields,table_name,pri_key)
    return template

def generate_mybatis_insert(method_id,table_name,fields,values,parameter_type):
    template = '''\t<insert id="%s" parameterType="%s">
    \t\tINSERT INTO `%s`(%s\t\t\t) VALUES(%s\t\t\t);
\t</insert>
'''%(method_id,parameter_type,table_name,fields,values)
    return template

def generate_mybatis_update(method_id,parameter_type,table_name,fields,pri_key,pri_property):
    template = '''\t<update id="%s" parameterType="%s">
    \t\tUPDATE `%s` SET %s \t\t\tWHERE `%s`=#{%s};
\t</update>
'''%(method_id,parameter_type,table_name,fields,pri_key,pri_property)
    return template

def generate_mybatis_delete(method_id,table_name,pri_key,pri_property):
    template = '''\t<delete id="%s">
    \t\tDELETE * FROM `%s` WHERE `%s`=#{%s};
\t</delete>
'''%(method_id,table_name,pri_key,pri_property)
    return template


def generate_mybatis_sql(namespace,content):
    template = '''<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
"http://mybatis.org/dtd/mybatis-3-mapper.dtd">

<mapper namespace="%s">
%s
</mapper>
'''%(namespace,content)
    return template

def generate_mybatis_xml(table_data):
    if table_data is None:
        raise Exception("数据为空")
    file_name = table_data.get_table_name()+".xml"
    field_list = table_data.get_field_list()
    if field_list is None:
        raise Exception("字段为空")
    column_fields = ""    
    property_fields = ""
    as_fields = ""
    update_fields = ""
    pri_key = None
    pri_property = None
    for field in field_list:
        column_fields += "\t\t\t\t,`%s` \r\n"%field.get_column_name()
        property_fields += "\t\t\t\t,#{%s} \r\n"%field.get_property_name()
        as_fields += "\t\t\t\t,`%s` as %s \r\n"%(field.get_column_name(),field.get_property_name())
        if field.get_pri_key():
            pri_key = field.get_column_name()
            pri_property = field.get_property_name()
        else:
            update_fields += "\t\t\t\t,`%s`=#{%s}\r\n"%(field.get_column_name(),field.get_property_name())
    if pri_key is None:
        raise Exception("未创建主键")
    column_fields = column_fields[5:]
    property_fields = property_fields[5:]
    as_fields = as_fields[5:]
    update_fields = update_fields[5:]
    namespace = table_data.get_namespace()
    result_type = table_data.get_result_type()
    table_name = table_data.get_table_name()

    content = ""
    content += generate_mybatis_insert(table_data.get_insert_method_id(),table_name,column_fields,property_fields,result_type)
    content += generate_mybatis_delete(table_data.get_delete_method_id(),table_name,pri_key,pri_property)
    content += generate_mybatis_update(table_data.get_update_method_id(),result_type,table_name,update_fields,pri_key,pri_property)
    content += generate_mybatis_select(table_data.get_select_method_id(),result_type,as_fields,table_name,pri_key,pri_property)
    content += generate_mybatis_select_pri(table_data.get_select_method_id(),result_type,as_fields,table_name,pri_key)

    with codecs.open(file_name,"w","utf-8") as f:
        f.write(generate_mybatis_sql(namespace,content))

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
        generate_java_pojo(data)
        generate_mybatis_xml(data)
    print("MISSION COMPLETE")
