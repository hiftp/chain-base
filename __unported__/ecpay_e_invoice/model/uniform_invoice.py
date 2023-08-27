#-*- coding:utf-8 -*-
from odoo import _, models, fields, api
from odoo.exceptions import UserError
import random
import decimal
import datetime
from ..sdk.ecpay_main import *
from werkzeug import urls


class UniformInvoice(models.Model):
    _name = 'uniform.invoice'

    name = fields.Char(string='統一發票號碼')
    state = fields.Selection(
        string='狀態', default='wait',
        selection=[('wait', '等待上傳'), ('upload_success', '開立成功'), ('upload_failure', '開立失敗'), ('invalid', '作廢')]
    )
    related_number = fields.Char(
        default=lambda self: 'ECPAY' + time.strftime("%Y%m%d%H%M%S", time.localtime()) +
                                                      str(random.randint(1000000000, 2147483647)),
        readonly=True
    )
    IIS_Award_Flag = fields.Selection(
        string='中獎旗標',
        selection=[('0', '未中獎'), ('1', '已中獎'), ('X', '有統編之發票')]
    )
    IIS_Award_Type = fields.Selection(
        string='中獎種類',
        selection=[
            ('0', '未中獎'), ('6', '六獎 二百元'), ('5', '五獎 一千元'), ('4', '四獎 四千元'), ('3', '三獎 一萬元'),
            ('2', '二獎 四萬元'), ('1', '頭獎 二十萬元'), ('7', '特獎 二百萬元'), ('8', '特別獎 一千萬'),
            ('9', '無實體2000元獎'), ('10', '無實體百萬元獎')]
    )

    IIS_Carrier_Num = fields.Char(string='載具編號')
    IIS_Carrier_Type = fields.Selection(
        string='載具類別',
        selection=[('1', '綠界科技電子發票載具'), ('2', '消費者自然人憑證'), ('3', '消費者手機條碼')]
    )
    IIS_Category = fields.Selection(
        string='發票類別',
        selection=[('B2B', '有統編'), ('B2C', '無統編')]
    )
    IIS_Check_Number = fields.Char(string='發票檢查碼')
    IIS_Clearance_Mark = fields.Selection(
        string='通關方式',
        selection=[('1', '經海關出口'), ('2', '非經海關出口')]
    )
    IIS_Create_Date = fields.Datetime(string='發票開立時間')
    IIS_Customer_Addr = fields.Char(string='客戶地址')
    IIS_Customer_Email = fields.Char(string='客戶電子信箱')
    IIS_Customer_ID = fields.Char(string='客戶編號')
    IIS_Customer_Name = fields.Char(string='客戶名稱')
    IIS_Customer_Phone = fields.Char(string='客戶電話')
    IIS_Identifier = fields.Char(string='買方統編')
    IIS_Invalid_Status = fields.Selection(
        string='發票作廢狀態',
        selection=[('1', '已作廢'), ('0', '未作廢')]
    )
    IIS_IP = fields.Char(string='發票開立IP')
    IIS_Issue_Status = fields.Selection(
        string='發票開立狀態',
        selection=[('1', '發票開立'), ('0', '發票註銷')]
    )
    IIS_Love_Code = fields.Char(string='捐款單位捐贈碼')
    IIS_Mer_ID = fields.Char(string='合作特店編號')
    IIS_Number = fields.Char(string='發票號碼')
    IIS_Print_Flag = fields.Selection(
        string='列印旗標',
        selection=[('1', '列印'), ('0', '不列印')]
    )
    IIS_Random_Number = fields.Char(string='隨機碼')
    IIS_Relate_Number = fields.Char(string='合作特店自訂編號')
    IIS_Remain_Allowance_Amt = fields.Char(string='剩餘可折讓金額')
    IIS_Sales_Amount = fields.Char(string='發票金額')
    IIS_Tax_Amount = fields.Char(string='稅金')
    IIS_Tax_Rate = fields.Char(string='稅率')
    IIS_Tax_Type = fields.Selection(
        string='課稅別',
        selection=[('1', '應稅'), ('2', '零稅率'), ('3', '免稅'), ('9', '混合應稅與免稅')]
    )
    IIS_Turnkey_Status = fields.Selection(
        string='發票上傳後接收狀態',
        selection=[('C', '成功'), ('E', '失敗'), ('G', '處理中')]
    )
    IIS_Type = fields.Selection(
        string='發票種類',
        selection=[('07', '一般稅額計算'), ('08', '特種稅額計算')]
    )
    IIS_Upload_Date = fields.Datetime(string='發票上傳時間')
    IIS_Upload_Status = fields.Selection(
        string='發票上傳狀態',
        selection=[('1', '已上傳'), ('0', '未上傳')]
    )
    InvoiceRemark = fields.Char(string='發票備註')
    ItemAmount = fields.Char(string='商品合計')
    ItemCount = fields.Char(string='商品數量')
    ItemName = fields.Char(string='商品名稱')
    ItemPrice = fields.Char(string='商品價格')
    ItemRemark = fields.Char(string='商品備註說明')
    ItemTaxType = fields.Char(string='商品課稅別')
    ItemWord = fields.Char(string='商品單位')
    PosBarCode = fields.Char(string='顯示電子發票BARCODE用')
    QRCode_Left = fields.Char(string='顯示電子發票QRCODE左邊用')
    QRCode_Right = fields.Char(string='顯示電子發票QRCODE右邊用')
    RtnCode = fields.Char(string='回應代碼')
    RtnMsg = fields.Char(string='回應訊息')
    CheckMacValue = fields.Char(string='檢查碼')

    invoice_month = fields.Char(string='發票月份')

    def get_ecpay_invoice_info(self):
        """向綠界後台取得電子發票的詳細資訊"""
        invoice = EcpayInvoice()

        self.demo_invoice_init(invoice, 'Query/Issue', 'INVOICE_SEARCH')

        invoice.Send['RelateNumber'] = self.related_number
        aReturn_Info = invoice.Check_Out()

        if aReturn_Info['RtnCode'] != '1':
            raise UserError('查詢發票失敗!!' + aReturn_Info['RtnMsg'])

        # 設定發票的日期
        invoice_create = datetime.datetime.strptime(aReturn_Info['IIS_Create_Date'], '%Y-%m-%d %H:%M:%S')
        year_tw = invoice_create.year - 1911
        month = invoice_create.month

        if month % 2:
            self.invoice_month = f'{year_tw}年{month:02d}-{month+1:02d}月'
        else:
            self.invoice_month = f'{year_tw}年{month-1:02d}-{month:02d}月'

        # 修正Odoo儲存時間的時差
        if aReturn_Info['IIS_Upload_Date'] == '':
            aReturn_Info.pop('IIS_Upload_Date')

        if aReturn_Info['IIS_Create_Date'] == '':
            aReturn_Info.pop('IIS_Create_Date')

        self.write(aReturn_Info)

    """
    從 account move 搬過來的
    """
    uniform_state = fields.Selection(
        string='電子發票狀態', default='to invoice',
        selection=[('to invoice', '未開電子發票'), ('invoiced', '已開電子發票'), ('invalid', '已作廢')]
    )
    ecpay_tax_type = fields.Selection(
        string='商品單價是否含稅', default='1', readonly=True,
        # states={'draft': [('readonly', False)]},
        selection=[('1', '含稅'), ('0', '未稅')])
    # show_create_invoice = fields.Boolean(string='控制是否顯示串接電子發票', compute='get_access_invoice_mode')
    # show_hand_in_field = fields.Boolean(string='控制是否顯示手動填入的選項', compute='get_access_invoice_mode')
    is_donation = fields.Boolean(string='是否捐贈發票')
    love_code = fields.Char(string='捐贈碼')
    is_print = fields.Boolean(string='是否索取紙本發票')
    carrier_type = fields.Selection(
        string='載具類別',
        selection=[('1', '綠界科技電子發票載具'), ('2', '自然人憑證'), ('3', '手機條碼')]
    )
    carrier_num = fields.Char(string='載具號碼')
    ecpay_customerIdentifier = fields.Char(string='統一編號')
    ec_print_address = fields.Char(string='發票寄送地址')
    ec_ident_name = fields.Char(string='發票抬頭')

    is_refund = fields.Boolean(string='是否為折讓')
    refund_finish = fields.Boolean(string='折讓完成')
    refund_state = fields.Selection(
        string='折讓通知狀態', default='draft',
        selection=[('draft', '草稿'), ('to be agreed', '待同意'), ('agreed', '開立成功'), ('disagree', '開立失敗')]
    )
    refund_ecpay_kind = fields.Selection(
        string='同意類型', default='offline', required=True, help='折讓電子發票同意類型',
        selection=[('offline', '紙本同意'), ('online', '線上同意')],
    )

    IA_Allow_No = fields.Char(string='折讓單號')
    ecpay_invoice_code = fields.Char(string='綠界電子發票自訂編號 ')
    partner_id = fields.Many2one('res.partner', string='客戶', required=True)

    @api.onchange('is_print', 'carrier_type', 'carrier_num')
    def set_carrier_type_false(self):
        if self.is_print is True:
            self.is_donation = False
            self.carrier_type = False
            self.carrier_num = False

    @api.onchange('is_donation')
    def set_is_print_false(self):
        if self.is_donation is True:
            self.is_print = False

    # 控制是否顯示手動開立的按鈕
    # 注意depends的self有時會有多筆，需要以for loop來執行。
    # @api.depends('ecpay_invoice_id')
    # def get_access_invoice_mode(self):
    #     auto_invoice_mode = self.env['ir.config_parameter'].sudo().get_param('ecpay_invoice_tw.auto_invoice')
    #     for row in self:
    #         if auto_invoice_mode == 'automatic':
    #             row.show_create_invoice = False
    #             row.show_hand_in_field = False
    #         elif auto_invoice_mode == 'hand in':
    #             row.show_create_invoice = False
    #             row.show_hand_in_field = True
    #         else:
    #             row.show_create_invoice = True
    #             row.show_hand_in_field = False

    # 當開立模式是自動開立時，在發票進行驗證(打開)時，同時進行開立發票的動作。
    # def action_invoice_open(self):
    def action_post(self):
        auto_invoice = self.env['ir.config_parameter'].sudo().get_param('ecpay_invoice_tw.auto_invoice')

        if auto_invoice == 'automatic':
            if self.state in ['wait', 'upload_failure']:
                self.create_ecpay_invoice()
            elif self.is_refund is True:
                # 如果發票為折讓，則不自動產生電子發票
                self.run_refund()
        return True

    """
    準備基本電子發票商家參數
    """

    def demo_invoice_init(self, ecpay_invoice, _type, method):
        """
        判斷設定是否為測試電子發票模式
        """
        config = self.env['ir.config_parameter'].sudo()
        url = 'https://einvoice.ecpay.com.tw/' + _type
        ecpay_demo_mode = config.get_param('ecpay_invoice_tw.ecpay_demo_mode')
        if ecpay_demo_mode:
            url = 'https://einvoice-stage.ecpay.com.tw/' + _type

        ecpay_invoice.Invoice_Method = method
        ecpay_invoice.Invoice_Url = url
        ecpay_invoice.MerchantID = config.get_param('ecpay_invoice_tw.ecpay_MerchantID')
        ecpay_invoice.HashKey = config.get_param('ecpay_invoice_tw.ecpay_HashKey')
        ecpay_invoice.HashIV = config.get_param('ecpay_invoice_tw.ecpay_HashIV')

    # 匯入Odoo發票明細到電子發票中
    def prepare_item_list(self):
        res = []
        amount_total = 0.0
        for line in self.line_ids:
            # 若Vat = 0(免稅)，商品金額需為免稅金額若Vat = 1(含稅)，商品金額需為含稅金額
            # if self.ecpay_tax_type == '0':
            #     ItemPrice = line.price_subtotal / int(line.quantity)
            #     ItemAmount = line.price_subtotal
            # else:
            #     ItemPrice = line.price_total / int(line.quantity)
            #     ItemAmount = line.price_total

            res.append({
                'ItemName': line.name[:30],
                'ItemCount': line.quantity,
                'ItemWord': line.product_id.uom_id.name[:6],
                'ItemPrice': line.price,
                'ItemTaxType': '',
                'ItemAmount': line.total,
                'ItemRemark': line.name[:40]
            })
            amount_total += line.total
        return res, amount_total

    # 準備客戶基本資料
    def prepare_customer_info(self, ecpay_invoice):
        ecpay_invoice.Send.update({
            'CustomerID': '',

            # 新版統編寫法，取得電商前端統編
            'CustomerIdentifier': self.ecpay_customerIdentifier if self.ecpay_customerIdentifier else '',

            # 新版抬頭寫法，取得電商抬頭，如果沒有預設取得partner 名稱
            'CustomerName': self.ec_ident_name if self.ec_ident_name else self.partner_id.name,

            # 新版寄送地址寫法，取得電商發票寄送地址，如果沒有預設取得partner 地址
            'CustomerAddr': self.ec_print_address if self.ec_print_address else self.partner_id.street,
            'CustomerPhone': self.partner_id.mobile if self.partner_id.mobile else '',
            'CustomerEmail': self.partner_id.email if self.partner_id.email else '',
            'ClearanceMark': '',
        })

    # 檢查發票邏輯
    def validate_ecpay_invoice(self):

        if self.is_print is True and self.is_donation is True:
            raise UserError('列印發票與捐贈發票不能同時勾選！！')
        elif self.is_print is True and self.carrier_type is not False:
            raise UserError('列印發票時，不能夠選擇發票載具！！')
        elif self.is_print is False and self.carrier_type in ['2', '3'] and self.is_donation is False:
            if self.carrier_num is False:
                raise UserError('請輸入發票載具號碼！！')
            elif self.carrier_type == '3':
                if not self.check_carruernum(self.carrier_num):
                    raise UserError('手機載具不存在！！')

        if self.is_donation is True and self.love_code is not False:
            if not self.check_lovecode(self.love_code):
                raise UserError('愛心碼不存在！！')

         # 檢查客戶地址
        if self.ec_print_address is False and self.partner_id.street is False:
            raise UserError('請到客戶資料中輸入客戶地址或在當前頁面輸入發票寄送地址！')

    @api.onchange('partner_id')
    def _autocomplete_partner_information(self):
        partner = self.partner_id
        if partner:
            self.ec_ident_name = partner.name
            self.ec_print_address = partner.street

    # 產生電子發票
    def create_ecpay_invoice(self):

        # 檢查基本開票邏輯
        self.validate_ecpay_invoice()

        # 建立電子發票物件
        invoice = EcpayInvoice()

        # 設定基本電子發票商家參數
        self.demo_invoice_init(invoice, 'Invoice/Issue', 'INVOICE')

        # 匯入發票種的發票明細到電子發票物件
        invoice.Send['Items'], amount_total = self.prepare_item_list()

        decimal.getcontext().rounding = decimal.ROUND_05UP
        print(round(decimal.Decimal(amount_total)))

        # 匯入客戶基本資訊
        self.prepare_customer_info(invoice)

        # 建立Odoo中，新的uniform.invoice的紀錄
        # record = self.env['uniform.invoice'].create({})

        invoice.Send.update({
            'RelateNumber': self.related_number,
            'Print': '0',
            'Donation': '0',
            'LoveCode': '',
            'CarruerType': '',
            'CarruerNum': '',
            'TaxType': '1',
            'SalesAmount': round(decimal.Decimal(amount_total)),
            'InvoiceRemark': 'Odoo',
            'InvType': '07',
            'vat': self.ecpay_tax_type,
        })

        # 加入是否捐贈，是否列印，與發票載具的設定
        if self.is_print is True or self.ecpay_customerIdentifier:
            invoice.Send['Print'] = '1'
        if self.is_donation is True:
            invoice.Send['Donation'] = '1'
            invoice.Send['LoveCode'] = self.love_code
        if self.carrier_type is not False:
            invoice.Send['CarruerType'] = self.carrier_type
            if self.carrier_num is not False and invoice.Send['CarruerType'] in ['2', '3']:
                invoice.Send['CarruerNum'] = self.carrier_num

        # 送出資訊
        aReturn_Info = invoice.Check_Out()

        # 檢查是否開立成功
        if aReturn_Info['RtnCode'] != '1':
            raise UserError('串接電子發票失敗!!錯誤訊息：' + aReturn_Info['RtnMsg'])

        # 設定發票號碼
        self.name = aReturn_Info['InvoiceNumber']

        # 成功開立發票後，將電子發票與Odoo發票關聯
        # self.ecpay_invoice_id = record

        # 利用RelateNumber到綠界後台取得電子發票的詳細資訊並儲存到Odoo電子發票模組
        self.get_ecpay_invoice_info()

        # 設定Odoo發票為已開電子發票
        self.uniform_state = 'invoiced'
        self.state = 'upload_success'

    def run_invoice_invalid(self):
        """
        執行電子發票作廢
        """

        # 建立物件
        invoice = EcpayInvoice()

        # 初始化物件
        self.demo_invoice_init(invoice, 'Invoice/IssueInvalid', 'INVOICE_VOID')

        invalid_invoice = list(filter(lambda x: x.IIS_Invalid_Status == '1', self))
        if invalid_invoice:
            raise UserError(_('電子發票：%s 已作廢!!' % ','.join([i.name for i in invalid_invoice])))

        for line in self:

            invoice.Send['InvoiceNumber'] = line.name
            invoice.Send['Reason'] = line.name
            return_info = invoice.Check_Out()

            # 判定是否成功作廢
            if return_info['RtnCode'] != '1':
                raise UserError('作廢電子發票失敗!!錯誤訊息：' + return_info['RtnMsg'])

            line.get_ecpay_invoice_info()


        # 檢查是否有開立電子發票
        # if self.ecpay_invoice_id:
        #     if self.ecpay_invoice_id.IIS_Invalid_Status == '1':
        #         raise UserError('該電子發票：%s 已作廢!!' % self.ecpay_invoice_id.name)
        # else:
        #     raise UserError('找不到電子發票!!')

        # 設定電子發票作廢需要參數
        # invoice.Send['InvoiceNumber'] = self.ecpay_invoice_id.name
        # invoice.Send['Reason'] = self.name

        # 送出資訊
        # aReturn_Info = invoice.Check_Out()

        # 判定是否成功作廢
        # if aReturn_Info['RtnCode'] != '1':
        #     raise UserError('作廢電子發票失敗!!錯誤訊息：' + aReturn_Info['RtnMsg'])

        # 更新儲存在Odoo中的電子發票資訊
        # self.ecpay_invoice_id.get_ecpay_invoice_info()

    # 執行電子發票折讓
    def run_refund(self):
        # 檢查欲折讓的發票是否有被設定
        # if self.ecpay_invoice_id.id is False:
        #     raise UserError('找不到欲折讓的發票！')
        # 取得折讓方式(紙本開立或線上開立)
        # refund_mode = self.env['ir.config_parameter'].sudo().get_param('ecpay_invoice_tw.ecpay_AllowanceByCollegiate')
        if self.refund_ecpay_kind == "offline":
            refund_mode = False
        else:
            refund_mode = True

        # 建立物件
        invoice = EcpayInvoice()
        # 初始化物件,依折讓方式(紙本開立或線上開立)
        if refund_mode:
            if not self.partner_id.email: raise UserError('必需要有客戶e-mail才能通知！')
            self.demo_invoice_init(invoice, 'Invoice/AllowanceByCollegiate', 'AllowanceByCollegiate')
            # 取得 domain
            base_url = self.env['ir.config_parameter'].sudo().get_param('ecpay_invoice_tw.ecpay_allowance_domain')
            if not base_url:
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            invoice.Send['ReturnURL'] = urls.url_join(base_url, '/invoice/ecpay/agreed_invoice_allowance')
        else:
            self.demo_invoice_init(invoice, 'Invoice/Allowance', 'ALLOWANCE')

        # invoice.Send['InvoiceNo'] = self.ecpay_invoice_id.name
        invoice.Send['AllowanceNotify'] = 'E'
        invoice.Send['NotifyMail'] = self.partner_id.email if self.partner_id.email else ''

        # 匯入發票種的發票明細到電子發票物件
        invoice.Send['Items'], amount_total = self.prepare_item_list()
        invoice.Send['AllowanceAmount'] = int(self.amount_total)

        # 送出資訊
        aReturn_Info = invoice.Check_Out()

        # 檢查是否開立成功
        if aReturn_Info['RtnCode'] != '1':
            raise UserError('折讓開立失敗!!錯誤訊息：' + aReturn_Info['RtnMsg'])
        # 寫入折讓號碼
        self.IA_Allow_No = aReturn_Info['IA_Allow_No']
        # 更新發票的剩餘折讓金額
        # self.ecpay_invoice_id.IA_Remain_Allowance_Amt = aReturn_Info['IA_Remain_Allowance_Amt']
        self.refund_finish = True
        # 若為線上開立，還需處理後續狀態
        if refund_mode:
            self.refund_state = 'to be agreed'
        else:
            self.refund_state = 'agreed'

    @api.model
    def check_carruernum(self, text):
        """
        電子發票前端驗證手機條碼ＡＰＩ
        """

        # 建立電子發票物件
        invoice = EcpayInvoice()
        # 初始化物件
        self.demo_invoice_init(invoice, 'Query/CheckMobileBarCode', 'CHECK_MOBILE_BARCODE')

        # 準備傳送參數
        invoice.Send['BarCode'] = text

        # 送出資訊
        aReturn_Info = invoice.Check_Out()

        # 檢查是否成功
        return aReturn_Info['RtnCode'] == '1' and aReturn_Info['IsExist'] == 'Y'

    # 電子發票前端驗證愛心碼ＡＰＩ
    @api.model
    def check_lovecode(self, text):
        # 建立電子發票物件
        invoice = EcpayInvoice()
        # 初始化物件
        self.demo_invoice_init(invoice, 'Query/CheckLoveCode', 'CHECK_LOVE_CODE')

        # 準備傳送參數
        invoice.Send['LoveCode'] = text

        # 送出資訊
        aReturn_Info = invoice.Check_Out()

        # 檢查是否成功
        return aReturn_Info['RtnCode'] == '1' and aReturn_Info['IsExist'] == 'Y'

    def get_ecpay_invoice(self):
        """
        人工填入電子發票
        """
        if self.ecpay_invoice_code is False:
            raise UserError('請填入綠界電子發票自訂編號 ！！')

        # 建立Odoo中，新的uniform.invoice的紀錄
        record = self.env['uniform.invoice'].create({})

        # invoice.Send['RelateNumber'] = record.related_number
        record.related_number = self.ecpay_invoice_code

        # 設定發票號碼
        # record.name = aReturn_Info['InvoiceNumber']

        # 成功開立發票後，將電子發票與Odoo發票關聯
        # self.ecpay_invoice_id = record

        # 利用RelateNumber到綠界後台取得電子發票的詳細資訊並儲存到Odoo電子發票模組
        record.get_ecpay_invoice_info()
        record.name = record.IIS_Number

        # 設定Odoo發票為已開電子發票
        self.uniform_state = 'invoiced'
        return True

    line_ids = fields.One2many('uniform.invoice.line', 'invoice_id', string='明細')
    active = fields.Boolean(string='啟用', default=True)

    @api.model
    def create(self, vals_list):
        if not vals_list.get('line_ids'):
            raise UserError(_('此發票無明細'))

        return super(UniformInvoice, self).create(vals_list)

    # @api.multi
    # def unlink(self):
        # if not all(i.state in ['wait', 'upload_failure'] for i in self):
            # raise UserError(_('選擇的發票裡有上傳成功'))

        # return super(UniformInvoice, self).unlink()
