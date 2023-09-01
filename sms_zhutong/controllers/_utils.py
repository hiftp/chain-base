import hashlib
from datetime import datetime, timedelta
from odoo.http import request

def _md5(key):
    result = hashlib.md5(key.encode('utf8')).hexdigest().lower()
    return result

def _odoo_param(key):
    return request.env['ir.config_parameter'].sudo().get_param(key)

def _params(mobile, content):
    tkey = str(int(datetime.now().timestamp()))
    params = {
        'username': _odoo_param('sms_zhutong.username'),
        'tKey': tkey,
        'password': _md5(_md5(_odoo_param('sms_zhutong.password'))+tkey),
        'mobile': mobile,
        'content': content,
    }
    return params
    
def _unit_params(phone, content,type):
    unit_params = { 
        'sendTime': "",       
        'content': content,        
        'phone':phone,
        'type':type
    }
    return unit_params


# username    用户名（必填）
# tkey    当前时间（必填,24小时制），格式：yyyyMMddHHmmss，例如：20160315130530。
# 客户时间早于或晚于网关时间超过30分钟，则网关拒绝提交。
# password    密码（必填）:md5( md5(password)  +  tkey) ) 
# 其中“+”表示字符串连接。即：先对密码进行md5加密，将结果与tkey值合并，再进行一次md5加密。
# 两次md5加密后字符串都需转为小写。
# 例如：若当前时间为2016-03-15 12:05:30，密码为123456，
# 则：password =md5(md5(“123456”) + “20160315120530” )
# 则：password =md5(e10adc3949ba59abbe56e057f20f883e20160315120530)
# 则：password = ea8b8077f748b2357ce635b9f49b7abe
# mobile  手机号 (必填，最多支持2000个号码)
# content 发送内容（必填,最好不要包含空格和回车，最多支持500个字，一个内容里面只能包含一个签名，如：内容【签名】）
# productid   产品id(必填，不同的产品用于发不同类型的信息)
# xh  扩展的小号,必须为数字，没有请留空。
# 注意：若为多签名用户，又无法确保所提交签名与扩展号一一对应,参数xh=0。所发送签名和扩展号需要提前报备，SMS短信平台系统会根据签名自动加上扩展号。

