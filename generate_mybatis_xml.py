#encoding:utf-8
'''
    生成mybatis xml
'''
import codecs
import os
import pymysql
import traceback
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

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

def generate_mybatis_select_list(method_id,result_type,fields,table_name):
    template = '''\t<select id="%sList" resultType="%s">
    \t\tSELECT %s \t\t\tFROM `%s`;
\t</select>
'''%(method_id,result_type,fields,table_name)
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

def generate_mybatis_delete(method_id,table_name,pri_key):
    template = '''\t<delete id="%s">
    \t\tDELETE * FROM `%s` WHERE `%s`=#{0};
\t</delete>
'''%(method_id,table_name,pri_key)
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

def generate_mybatis_xml(table_data,config_dir):
    if table_data is None:
        raise Exception("数据为空")
    file_name = config_dir+table_data.get_table_name()+".xml"
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
    content += generate_mybatis_delete(table_data.get_delete_method_id(),table_name,pri_key)
    content += generate_mybatis_update(table_data.get_update_method_id(),result_type,table_name,update_fields,pri_key,pri_property)
    # content += generate_mybatis_select(table_data.get_select_method_id(),result_type,as_fields,table_name,pri_key,pri_property)
    content += generate_mybatis_select_pri(table_data.get_select_method_id(),result_type,as_fields,table_name,pri_key)
    content += generate_mybatis_select_list(table_data.get_select_method_id(),result_type,as_fields,table_name)

    with codecs.open(file_name,"w","utf-8") as f:
        f.write(generate_mybatis_sql(namespace,content))