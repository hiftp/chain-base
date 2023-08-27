#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import urllib
import hashlib
import requests


class EcpayInvoiceMethod:
    """執行發票作業項目。"""

    # 一般開立發票。
    INVOICE = 'INVOICE'

    # 延遲或觸發開立發票。
    INVOICE_DELAY = 'INVOICE_DELAY'

    # 開立折讓。
    ALLOWANCE = 'ALLOWANCE'

    # 發票作廢。
    INVOICE_VOID = 'INVOICE_VOID'

    # 折讓作廢。
    ALLOWANCE_VOID = 'ALLOWANCE_VOID'

    # 查詢發票。
    INVOICE_SEARCH = 'INVOICE_SEARCH'

    # 查詢作廢發票。
    INVOICE_VOID_SEARCH = 'INVOICE_VOID_SEARCH'

    # 查詢折讓明細。
    ALLOWANCE_SEARCH = 'ALLOWANCE_SEARCH'

    # 查詢折讓作廢明細。
    ALLOWANCE_VOID_SEARCH = 'ALLOWANCE_VOID_SEARCH'

    # 發送通知。
    INVOICE_NOTIFY = 'INVOICE_NOTIFY'

    # 付款完成觸發或延遲開立發票。
    INVOICE_TRIGGER = 'INVOICE_TRIGGER'

    # 手機條碼驗證。
    CHECK_MOBILE_BARCODE = 'CHECK_MOBILE_BARCODE'

    # 愛心碼驗證。
    CHECK_LOVE_CODE = 'CHECK_LOVE_CODE'


class EcpayCarruerType:
    """電子發票載具類別"""

    # 無載具
    No = ''

    # 會員載具
    Member = '1'

    # 買受人自然人憑證
    Citizen = '2'

    # 買受人手機條碼
    Cellphone = '3'


class EcpayPrintMark:
    """電子發票列印註記"""

    # 不列印
    No = '0'

    # 列印
    Yes = '1'


class EcpayDonation:
    """電子發票捐贈註記"""

    # 捐贈
    Yes = '1'

    # 不捐贈
    No = '0'


class EcpayClearanceMark:
    """通關方式"""

    # 經海關出口
    Yes = '1'

    # 非經海關出口
    No = '2'


class EcpayTaxType:
    """課稅類別"""

    # 應稅
    Dutiable = '1'

    # 零稅率
    Zero = '2'

    # 免稅
    Free = '3'

    # 應稅與免稅混合(限收銀機發票無法分辦時使用，且需通過申請核可)
    Mix = '9'


class EcpayInvType:
    """字軌類別"""

    # 一般稅額
    General = '07'


class EcpayVatType:
    """商品單價是否含稅"""

    # 商品單價含稅價
    Yes = '1'

    # 商品單價未稅價
    No = '0'


class EcpayDelayFlagType:
    """延遲註記"""

    # 延遲註記
    Delay = '1'

    # 觸發註記
    Trigger = '2'


class EcpayPayTypeCategory:
    """交易類別"""

    # ECPAY
    Ecpay = '2'


class EcpayAllowanceNotifyType:
    """通知類別"""

    # 簡訊通知
    Sms = 'S'

    # 電子郵件通知
    Email = 'E'

    # 皆通知
    All = 'A'

    # 皆不通知
    No = 'N'


class EcpayNotifyType:
    """發送方式"""

    # 簡訊通知
    Sms = 'S'

    # 電子郵件通知
    Email = 'E'

    # 皆通知
    All = 'A'


# 發送內容類型
class EcpayInvoiceTagType():
    # 發票開立

    Invoice = 'I'

    # 發票作廢

    Invoice_Void = 'II'

    # 折讓開立

    Allowance = 'A'

    # 折讓作廢

    Allowance_Void = 'AI'

    # 發票中獎

    Invoice_Winning = 'AW'


class EcpayNotifiedType:
    """發送對象"""

    # 通知客戶
    Customer = 'C'

    # 通知廠商
    vendor = 'M'

    # 皆發送
    All = 'A'


class ECPay_EncryptType:
    """加密類型"""

    # MD5(預設)
    ENC_MD5 = 0

    # SHA256
    ENC_SHA256 = 1


class ECPay_IO:

    @staticmethod
    def ServerPost(parameters: dict, service_url: str):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        # 組合字串
        send_data = '&'.join([f'{key}={str(val)}' for key, val in parameters.items()])
        r = requests.post(service_url, data=send_data, headers=headers)
        return r.text


class ECPay_CheckMacValue():
    '''
    *產生檢查碼
    '''

    @staticmethod
    def generate(ar_parameters=None, hash_key='', hash_iv='', enc_type=0):
        if ar_parameters is None:
            ar_parameters = {}

        mac_value = ''
        if ar_parameters:
            if 'CheckMacValue' in ar_parameters:
                del ar_parameters['CheckMacValue']

            sorted_str = 'HashKey=' + hash_key

            for key in sorted(ar_parameters.keys(), key=str.lower):
                sorted_str += '&' + key + '=' + str(ar_parameters[key])

            sorted_str += '&HashIV=' + hash_iv

            mac_value = urllib.parse.quote_plus(sorted_str)

            # 轉成小寫
            mac_value = mac_value.lower()

            # 取代為與 dotNet 相符的字元
            mac_value = ECPay_CheckMacValue.do_str_replace(mac_value)

            # 編碼
            if enc_type == ECPay_EncryptType.ENC_SHA256:
                mac_value = hashlib.sha256(mac_value.encode('utf-8')).hexdigest()  # SHA256 編碼
            else:
                mac_value = hashlib.md5(mac_value.encode('utf-8')).hexdigest()  # MD5 編碼

            # 轉成大寫
            mac_value = mac_value.upper()

        return mac_value

    @staticmethod
    def restore_str_replace(string):
        mapping_dict = {'!': '%21', '*': '%2a', '(': '%28', ')': '%29'}
        for key, val in mapping_dict.items():
            string = string.replace(key, val)

        return string

    @staticmethod
    def do_str_replace(string):
        mapping_dict = {'!': '%21', '*': '%2a', '(': '%28', ')': '%29', '/': '%2F'}
        for key, val in mapping_dict.items():
            string = string.replace(val, key)

        return string
