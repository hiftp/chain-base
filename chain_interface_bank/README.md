#### 所有功能列表请参照对应的开发文档
#### doc目录下
<h3>2019-02-18调整了对外接口</h3>
- 将原接口的数据传递xml方式改为了json方式

<h3>json数据格式</h3>
> 传递付款单
<pre><code>
json_data = {
    "system_name": "接入系统名称",
    "system_code": "接入系统代码",
    "create_date": "上传日期yyyy-MM-dd<",
    "create_time": "上传时间HH:mm:ss",
    "payments": [
        {
            "source_number":"付款单据编号",
            "source_model":"单据模型",
            "company_code":"公司编码",
            "public_signs":"公私标识",
            "payment_model":"付款模式",
            "cross_row_identi":"跨行标识",
            "off_site_identi":"异地标识",
            "payee_identi":"收款方标识",
            "debit_identi":"借贷标识",
            "payee_bank":"收款方归属银行名称",
            "payee_bank_code":"收款方归属银行代码",
            "payee_opening_bank":"收款方开户行名称",
            "payee_opening_bank_code":"收款方开户行代码",
            "payee_opening_province":"收款方省份名称",
            "payee_opening_province_code":"收款方省份代码",
            "payee_opening_city":"收款方城市名称",
            "payee_opening_city_code":"收款方城市代码",
            "currency_type":"币种",
            "partner_id":"收款户名",
            "partner_bank_number":"收款账号",
            "partner_number":"客户编号",
            "partner_contact":"收款联系人",
            "partner_contact_phone":"联系人电话",
            "partner_contact_add":"联系人地址",
            "pay_money":"付款金额",
            "pay_summary":"摘要",
            "pay_use":"付款用途",
        }
    ]
}
</code></pre>

> 传递付款单响应结果 
<pre><code>
result_data = {
    "source_number": "付款单据编号",
    "source_model": "单据模型",
    "company_code": "公司编码",
    "state": "状态码",
    "message": "消息",
}
</code></pre>


> 查询付款状态
<pre><code>
json_data = {
    "system_name": "接入系统名称",
    "system_code": "接入系统代码",
    "create_date": "上传日期yyyy-MM-dd<",
    "create_time": "上传时间HH:mm:ss",
    "payment": [
        {
            "form_number": "单据编号",
            "form_model": "单据模型",
        },
        {
            "form_number": "单据编号",
            "form_model": "单据模型",
        }
    ]
}
</code></pre>

> 查询付款状态响应结果

<pre><code>
result_data = {
    "state": "状态码",
    "message": "消息",
    "results": [
        {
            "form_number": "单据编号",
            "form_model": "单据模型"
            "company_code": "公司代码"
            "payment_state": "付款状态"
        },
        {
            "form_number": "单据编号",
            "form_model": "单据模型"
            "company_code": "公司代码"
            "payment_state": "付款状态"
        }
    ]
}
</code></pre>




