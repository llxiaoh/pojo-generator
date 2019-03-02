#encoding:utf-8
'''
    生成dao
'''
import codecs
import os
import pymysql
import traceback
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def generate_java_dao_template(import_package,imports,explain,class_name,content):
	template = '''package %s;
import java.util.List;
import org.apache.ibatis.session.SqlSession;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
%s

/**
 * %s
 * @author auto_generate
 *
 */
public final class %s {
    public static final %s INSTANCE = new %s();
    private %s() {}
    
    private Logger log = LoggerFactory.getLogger("ACTION");
    
%s
}
'''%(import_package,imports,explain,class_name,class_name,class_name,class_name,content)
	return template

def generate_java_dao(table_data,package,sql_get,config_dir,other_import):

	table_class_name = table_data.get_class_name()
	dao_class_name = table_class_name[:-2] + "DAO"
	result_class_name = table_class_name[:-2] + "PO"

	file_name = config_dir+dao_class_name+".java"
    
	name_space = table_data.get_namespace()

	select_one_id = "select"+result_class_name
	select_one_pri_id = "select"+result_class_name+"Pri"
	select_list_id = "select"+result_class_name+"List"
	insert_id = "insert"+result_class_name
	delete_id = "delete"+result_class_name
	update_id = "update"+result_class_name

	class_explain = "DAO操作"

	import_content = generate_dao_import(package+".po."+result_class_name)+other_import

	import_package = package+".dao"

	result_type_as_param = result_class_name[0].lower()+result_class_name[1:]

	pri_type = table_data.get_pri_type()
	pri_name = table_data.get_pri_name()


	content = ""
	content += generate_dao_get_list_method_template("查询%s列表"%result_class_name,result_class_name,select_list_id,sql_get,select_list_id,dao_class_name,name_space)
	# content += generate_dao_get_one_method_template("查询单条%s"%result_class_name,result_class_name,select_one_id,result_class_name,result_type_as_param,sql_get,select_one_id,dao_class_name,name_space)
	content += generate_dao_get_one_method_pri_template("查询单条%s"%result_class_name,result_class_name,select_one_pri_id,pri_type,pri_name,sql_get,select_one_pri_id,dao_class_name,name_space)
	content += generate_dao_insert_template("新增%s"%result_class_name,insert_id,result_class_name,result_type_as_param,sql_get,insert_id,dao_class_name,name_space)
	content += generate_dao_update_template("修改%s"%result_class_name,update_id,result_class_name,result_type_as_param,sql_get,update_id,dao_class_name,name_space)
	content += generate_dao_delete_template("删除%s"%result_class_name,delete_id,pri_type,pri_name,sql_get,delete_id,dao_class_name,name_space)

	with codecs.open(file_name,"w+","utf-8") as f:
		f.write(generate_java_dao_template(import_package,import_content,class_explain,dao_class_name,content))


def generate_dao_import(import_java):
	template = '''import %s;\r\n'''%import_java
	return template

def generate_dao_get_list_method_template(explain,result_type,method_name,sql_get,select_id,class_name,namespace):
	template = '''	/**
	 * %s
	 * @return
	 */
	public List<%s> get%s() {
		SqlSession session = null;
		try {
			session = %s;
			return session.selectList("%s.%s");
		}catch(Exception e) {
			log.error("%s#%s error",e);
		}finally {
			if(session != null) {
				session.close();
			}
		}
		return null;
	}
'''%(explain,result_type,method_name,sql_get,namespace,select_id,class_name,method_name)
	return template

def generate_dao_get_one_method_template(explain,result_type,method_name,param_type,param_name,sql_get,select_id,class_name,namespace):
	template = '''	/**
	 * %s
	 * @return
	 */
	public %s %s(%s %s) {
		SqlSession session = null;
		try {
			session = %s;
			return session.selectOne("%s.%s",%s);
		}catch(Exception e) {
			log.error("%s#%s error",e);
		}finally {
			if(session != null) {
				session.close();
			}
		}
		return null;
	}
'''%(explain,result_type,method_name,param_type,param_name,sql_get,namespace,select_id,param_name,class_name,method_name)
	return template	

def generate_dao_get_one_method_pri_template(explain,result_type,method_name,param_type,param_name,sql_get,select_id,class_name,namespace):
	template = '''	/**
	 * %s
	 * @return
	 */
	public %s %s(%s %s) {
		SqlSession session = null;
		try {
			session = %s;
			return session.selectOne("%s.%s",%s);
		}catch(Exception e) {
			log.error("%s#%s error",e);
		}finally {
			if(session != null) {
				session.close();
			}
		}
		return null;
	}
'''%(explain,result_type,method_name,param_type,param_name,sql_get,namespace,select_id,param_name,class_name,method_name)
	return template		

def generate_dao_insert_template(explain,method_name,param_type,param_name,sql_get,select_id,class_name,namespace):
	template = '''	/**
	 * %s
	 * @return
	 */
	public int %s(%s %s) {
		SqlSession session = null;
		try {
			session = %s;
			return session.insert("%s.%s",%s);
		}catch(Exception e) {
			log.error("%s#%s error",e);
		}finally {
			if(session != null) {
				session.close();
			}
		}
		return 0;
	}
'''%(explain,method_name,param_type,param_name,sql_get,namespace,select_id,param_name,class_name,method_name)
	return template

def generate_dao_update_template(explain,method_name,param_type,param_name,sql_get,select_id,class_name,namespace):
	template = '''	/**
	 * %s
	 * @return
	 */
	public int %s(%s %s) {
		SqlSession session = null;
		try {
			session = %s;
			return session.update("%s.%s",%s);
		}catch(Exception e) {
			log.error("%s#%s error",e);
		}finally {
			if(session != null) {
				session.close();
			}
		}
		return 0;
	}
'''%(explain,method_name,param_type,param_name,sql_get,namespace,select_id,param_name,class_name,method_name)
	return template

def generate_dao_delete_template(explain,method_name,param_type,param_name,sql_get,select_id,class_name,namespace):
	template = '''	/**
	 * %s
	 * @return
	 */
	public int %s(%s %s) {
		SqlSession session = null;
		try {
			session = %s;
			return session.delete("%s.%s",%s);
		}catch(Exception e) {
			log.error("%s#%s error",e);
		}finally {
			if(session != null) {
				session.close();
			}
		}
		return 0;
	}
'''%(explain,method_name,param_type,param_name,sql_get,namespace,select_id,param_name,class_name,method_name)
	return template