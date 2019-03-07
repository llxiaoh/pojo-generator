#encoding:utf-8
'''
    生成po
'''
import codecs
import os
import pymysql
import traceback
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


def generate_java_pojo_template(java_name,package_name,content,get_set_content):
    template = '''package %s.bean.po;

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
    sname = name[0].title()+name[1:]
    template = '''
    /** 获取%s */
    public %s get%s(){
        return this.%s;
    }
    /** 设值%s */
    public void set%s(%s %s){
        this.%s = %s;
    }
'''%(explain,java_type,sname,name,explain,sname,java_type,name,name,name)
    return template

def generate_java_pojo(table_data,package_name,config_dir):
    if table_data is None:
        raise Exception("表数据获取异常")
    class_name = table_data.get_class_name()
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
    with codecs.open("%s.java"%(config_dir+class_name),"w+","utf-8") as f:
        f.write(generate_java_pojo_template(class_name,package_name,content,setget_content))
