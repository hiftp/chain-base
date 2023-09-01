# -*- coding: utf-8 -*-
import json
import logging, requests
from odoo import api, http, SUPERUSER_ID, _
from odoo.addons.web.controllers.main import Home
from odoo.http import request
from ._utils import _params, _odoo_param,_unit_params
import re
import base64

_logger = logging.getLogger(__name__)

class Home(Home):
   
    @http.route('/iap/message_send', type='json', auth='none', csrf=False)
    def sms_zhutong_message_send(self, numbers, message):
        for number in numbers:
            self._sms_zhutong_unit_message_send(number, message)

    @http.route('/iap/sms/2/send', type='json', auth='none', csrf=False)
    def sms_zhutong_message_batch_send(self, messages, account_token):
        results = []
        for message in messages: 
            _logger.info("正则表达式测试开始")
            _logger.info("获取电话号码%s",str(message.get('number')))
            reg_result = self._sms_zhuong_phone_regex(str(message.get('number'))) 
            _logger.info("获取reg_result结果%s",str(message.get('number')))
            if reg_result:
                result = self._sms_zhutong_unit_message_send([message['number']], message['content'])
                result['res_id'] = message['res_id']
                results.append(result)
        return results
        
    def _sms_zhutong_unit_message_send(self, numbers, message):
        _logger.info("国际短信验证")       
        url = 'https://api-gateway.zthysms.com/ims/v1/send'
        user_info_str = _odoo_param('sms_zhutong.username') + ":" + _odoo_param('sms_zhutong.password')
        user_info = base64.b64encode(user_info_str.encode())
        
        headers = {
            'Content-Type': 'application/json',
            "Authorization":"Basic" + user_info.decode()
        }
        params = _unit_params(','.join([str(number) for number in numbers]), message,'YX')

        response = requests.post(url=url, data=json.dumps(params), headers=headers)
        result = json.loads(response.text)
        return {
            'state': result.get('code') == 200 and 'success' or 'fail',
            'credit': 0.0,
            'return_code': result
        }

    def _sms_zhuong_phone_regex(self,number):        
        ar_DZ= re.compile(r"(^(\+?213|0)(5|6|7)\d{8}$)")
        ar_SY= re.compile(r"(^(!?(\+?963)|0)?9\d{8}$)")
        ar_SA= re.compile(r"(^(!?(\+?966)|0)?5\d{8}$)")
        en_US= re.compile(r"(^(\+?1)?[2-9]\d{2}[2-9](?!11)\d{6}$)")
        cs_CZ= re.compile(r"(^(\+?420)?[1-9][0-9]{2}?[0-9]{3}?[0-9]{3}$)")
        de_DE= re.compile(r"(^(\+?49[ \.\-])?([\(]{1}[0-9]{1,6}[\)])?([0-9 \.\-\/]{3,20})((x|ext|extension)[ ]?[0-9]{1,4})?$)")
        da_DK= re.compile(r"(^(\+?45)?(\d{8})$)")
        el_GR= re.compile(r"(^(\+?30)?(69\d{8})$)")
        en_AU= re.compile(r"(^(\+?61|0)4\d{8}$)")
        en_GB= re.compile(r"(^(\+?44|0)7\d{9}$)")
        en_HK= re.compile(r"(^(\+?852\-?)?[569]\d{3}\-?\d{4}$)")
        en_IN= re.compile(r"(^(\+?91|0)?[789]\d{9}$)")
        en_NZ= re.compile(r"(^(\+?64|0)2\d{7,9}$)")
        en_ZA= re.compile(r"(^(\+?27|0)\d{9}$)")
        en_ZM= re.compile(r"(^(\+?26)?09[567]\d{7}$)")
        es_ES= re.compile(r"(^(\+?34)?(6\d{1}|7[1234])\d{7}$)")
        fi_FI= re.compile(r"(^(\+?358|0)\s?(4(0|1|2|4|5)?|50)\s?(\d\s?){4,8}\d$)")
        fr_FR= re.compile(r"(^(\+?33|0)[67]\d{8}$)")
        he_IL= re.compile(r"(^(\+972|0)([23489]|5[0248]|77)[1-9]\d{6})")
        hu_HU= re.compile(r"(^(\+?36)(20|30|70)\d{7}$)")
        it_IT= re.compile(r"(^(\+?39)?\s?3\d{2} ?\d{6,7}$)")
        ja_JP= re.compile(r"(^(\+?81|0)\d{1,4}[ \-]?\d{1,4}[ \-]?\d{4}$)")
        ms_MY= re.compile(r"(^(\+?6?01){1}(([145]{1}(\-|\s)?\d{7,8})|([236789]{1}(\s|\-)?\d{7}))$)")
        nb_NO= re.compile(r"(^(\+?47)?[49]\d{7}$)")
        nl_BE= re.compile(r"(^(\+?32|0)4?\d{8}$)")
        nn_NO= re.compile(r"(^(\+?47)?[49]\d{7}$)")
        pl_PL= re.compile(r"(^(\+?48)? ?[5-8]\d ?\d{3} ?\d{2} ?\d{2}$)")
        pt_BR= re.compile(r"(^(\+?55|0)\-?[1-9]{2}\-?[2-9]{1}\d{3,4}\-?\d{4}$)")
        pt_PT= re.compile(r"(^(\+?351)?9[1236]\d{7}$)")
        ru_RU= re.compile(r"(^(\+?7|8)?9\d{9}$)")
        sr_RS= re.compile(r"(^(\+3816|06)[- \d]{5,9}$)")
        tr_TR= re.compile(r"(^(\+?90|0)?5\d{9}$)")
        vi_VN= re.compile(r"(^(\+?84|0)?((1(2([0-9])|6([2-9])|88|99))|(9((?!5)[0-9])))([0-9]{7})$)")
        zh_TW= re.compile(r"(^(\+?886\-?|0)?9\d{8}$)")
        
        if re.fullmatch(ar_DZ, number):
            return True
        if re.fullmatch(ar_SY, number):
             return True
        if re.fullmatch(ar_SA, number):
            return True
        if re.fullmatch(cs_CZ, number):
            return True
        if re.fullmatch(de_DE, number):
             return True
        if re.fullmatch(da_DK, number):
            return True
        if re.fullmatch(el_GR, number):
             return True
        if re.fullmatch(en_US, number):
            return True
        if re.fullmatch(en_AU, number):
            return True
        if re.fullmatch(en_GB, number):
             return True
        if re.fullmatch(en_HK, number):
            return True
        if re.fullmatch(en_IN, number):
             return True
        if re.fullmatch(en_NZ, number):
            return True
        if re.fullmatch(en_ZA, number):
             return True
        if re.fullmatch(en_ZM, number):
            return True
        if re.fullmatch(es_ES, number):
             return True
        if re.fullmatch(fi_FI, number):
            return True
        if re.fullmatch(fr_FR, number):
             return True
        if re.fullmatch(he_IL, number):
            return True
        if re.fullmatch(hu_HU, number):
             return True
        if re.fullmatch(it_IT, number):
            return True
        if re.fullmatch(ja_JP, number):
             return True
        if re.fullmatch(ms_MY, number):
            return True
        if re.fullmatch(nb_NO, number):
             return True
        if re.fullmatch(nl_BE, number):
            return True
        if re.fullmatch(nn_NO, number):
             return True
        if re.fullmatch(pl_PL, number):
            return True
        if re.fullmatch(pt_BR, number):
             return True
        if re.fullmatch(pt_PT, number):
            return True
        if re.fullmatch(ru_RU, number):
             return True
        if re.fullmatch(sr_RS, number):
            return True
        if re.fullmatch(tr_TR, number):
             return True
        if re.fullmatch(vi_VN, number):
             return True
        if re.fullmatch(zh_TW, number):
             return True
                 

  


