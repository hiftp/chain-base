# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from datetime import date
from odoo.exceptions import UserError
from odoo.tools.translate import _


class PaymentVoucher(models.Model):
    _name = 'payment_voucher.ebs'
    _rec_name = 'voucher_no'
    _description = 'payment voucher'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    voucher_type = fields.Many2one(comodel_name="voucher_type.ebs", string='Payment Type')
    address = fields.Text(string="Address", required=False, )
    class_code = fields.Char(string="Classification Code", required=False, )
    voucher_no = fields.Char(string="Voucher Number", default=lambda self: _('New'), requires=False, readonly=True,
                             trace_visibility='onchange', )
    voucher_details_ids = fields.One2many(comodel_name="voucher_details.ebs", inverse_name="voucher_id",
                                          string="Voucher Details", required=False, )
    payable_at = fields.Char(string="Payable At", required=False, )
    originating_memo = fields.Char(string="Originating Memo", required=False, readonly=True)
    state = fields.Selection(string="",
                             selection=[('draft', 'draft'), ('Prepared', 'Prepared'), ('FC Sign Off', 'FC Sign Off'),
                                        ('CFO Approval', 'CFO Approval'),
                                        ('process', 'Processed'),
                                        ('Rejected', 'Rejected'), ], required=False, copy=False, default='draft',
                             readonly=True, tracking=True)
    amount = fields.Float('Amount', )
    account_id = fields.Many2one(string="Debit Account", comodel_name='account.account')
    inv_obj = fields.Many2one('account.move', invisible=1)  # not account invoice
    budget_position_id = fields.Many2one(comodel_name="account.budget.post",
                                         string="Budgetary Position",
                                         required=False,
                                         )  # 预算管理
    # budget_position = fields.Integer(string="Budgetary Position", compute='_total_realised', store=True)
    analytic_id_id = fields.Many2one(comodel_name="account.analytic.account", string="Budget Line", required=False, )
    mode_payment = fields.Many2one(comodel_name='account.journal', string='Payment Account')
    narration = fields.Text(
        string="Narration",
        required=False)
    active = fields.Boolean(
        string='Active', 
        required=False, default=True)
    date = fields.Date(string="Date", required=False, )
    payee_type = fields.Selection(
        string='Payee Type',
        selection=[('vendor', 'Vendor'),
                   ('disco', 'Disco'),
                   ('genco', 'Genco'),
                   ],
        required=False, )
    payee_id = fields.Many2one('res.partner', string='Payee', tracking=True, )
    bill_to_pay = fields.Many2one('account.invoice.report', string='Payment Bill', )
    invoice_amount = fields.Float()
    net_amount = fields.Float()
    compute_tax = fields.Boolean(
        string='Compute tax', 
        required=False)
    # taxes_applied = fields.Many2many(
    #     comodel_name='account.tax',
    #     string='Taxes_applied')
    payment_voucher_id = fields.Char(
        string='Payment_voucher_id', 
        required=False)
    taxes_applied = fields.One2many(
        comodel_name='account.tax',
        compute='_related_taxes',
        string='Taxes_applied',
        required=False)
    payment_id = fields.Many2one(
        comodel_name='account.payment',
        string='Payment_id',
        required=False)
    journal_no = fields.Char(string='Payment Voucher Number', related='payment_id.payment_reference', required=False)
    total_tax = fields.Float(string='total tax')
    tax_computed = fields.Boolean(
        string='Tax_computed',
        required=False)
    payments = fields.One2many(
        comodel_name='account.payment',
        inverse_name='voucher_payment_id',
        string='Payments',
        required=False)


    @api.onchange('payee_type')
    def onchange_payee_type(self):
        for rec in self:
            if rec.payee_type == 'vendor':
                return { 'domain': {'payee_id' : [('supplier', '=', True)]}}
            elif rec.payee_type == 'disco':
                return {'domain': {'payee_id' : [('customer', '=', True)]}}
            elif rec.payee_type == 'genco':
                return { 'domain': {'payee_id' : [('is_genco', '=', True)]}}


    @api.onchange('payee_id')
    def onchange_payee(self):
        for rec in self:
            if rec.payee_id:
                return { 'domain': {'bill_to_pay' : [('partner_id', '=', rec.payee_id.id), ('type', '=', 'in_invoice'), ('state', '!=', 'paid')]}}


    def _related_taxes(self):
        for rec in self:
            related_bill = rec.bill_to_pay
            self.taxes_applied =related_bill.tax_line_ids








    # @api.one
    # @api.depends('analytic_id_id', )
    # def _total_realised(self):
    #
    #     self.total_realised = sum(paid.installment
    #                               for paid in self.schedule_installments_ids.filtered(lambda o: o.state == 'paid'))

    @api.model
    def create(self, vals):
        if vals.get('voucher_no', _('New')) == _('New'):
            vals['voucher_no'] = self.env['ir.sequence'].next_by_code('increment_payment_voucher') or _('New')
        result = super(PaymentVoucher, self).create(vals)
        return result

    @api.one
    @api.depends('voucher_details_ids.rate', )
    def _amount(self):
        self.amount = sum(voucher_details.rate for voucher_details in self.voucher_details_ids)

    # @api.multi
    # def open_vouchers(self):
    #     total_len = self.env['payment_voucher.ebs'].search_count([])
    #     result = total_len
    #     return result
    #



    @api.multi
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'Prepared'),
                   ('Prepared', 'FC Sign Off'),
                   ('FC Sign Off', 'Rejected'),
                   ('FC Sign Off', 'CFO Approval'),
                   ('CFO Approval', 'process'),
                   ('process', 'CFO Approval'),
                   ]
        return (old_state, new_state) in allowed

    @api.multi
    def change_state(self, new_state):
        for voucher in self:
            if voucher.is_allowed_transition(voucher.state, new_state):
                voucher.state = new_state
            else:
                msg = _('Moving from %s to %s is not allowed') % (voucher.state, new_state)
                raise UserError(msg)

    @api.multi
    def payment_voucher_request(self):
        self.change_state('Prepared')

    @api.multi
    def payment_voucher_prepare(self):
        self.change_state('FC Sign Off')

    @api.multi
    def voucher_cfo_approve(self):
        self.change_state('CFO Approval')
    @api.multi
    def taxpayment(self):
        payment_obj = self.env['account.payment'].with_context(active_ids=self.bill_to_pay.ids,
                                                               active_model='account.move',
                                                               active_id=self.bill_to_pay.id)
        taxes = []
        tax_amount_payment = []
        for tax in self.taxes_applied:
            tax_payments = []
            taxrate = tax.tax_id.amount
            taxamount = self.amount * abs(taxrate) / 100
            tax_amounts = []

            tax_pay_vals = {
                'payment_type': 'outbound',
                'partner_type': 'supplier',
                'payment_method_id': 1,
                'amount': taxamount,
                'partner_id': 12,
                'payment_date': self.date,
                'journal_id': self.mode_payment.id,
                'communication': "tax payment",
                'voucher_payment_id': self.id,

            }

            tax_payments.append(tax_pay_vals)
            payment_ta = payment_obj.create(tax_payments)
            payment_ta.post()

            # for total in tax_amounts:
            #     total_tax = sum(total.taxamount)
            #     net_amount = self.amount - total_tax
            #     payment_vals = {
            #         'payment_type': 'outbound',
            #         'partner_type': 'supplier',
            #         'payment_method_id': 1,
            #         'amount': net_amount,
            #         'partner_id': self.payee_id.id,
            #         'payment_date': self.date,
            #         'journal_id': self.mode_payment.id,
            #         'communication': self.bill_to_pay.name,
            #
            #     }
            #     payment = payment_obj.create(payment_vals)
            #
            #     payment.post()


    @api.multi
    def updateamount(self):
        payments = self.env['account.payment'].search([('voucher_payment_id', '=', self.id)])
        taxes = []
        for pay in payments:
            taxes.append(pay.amount)
            total = sum(taxes)
            self.net_amount = self.amount - total

    @api.multi
    def payment_voucher_process(self):
        if not self.compute_tax:
            for payment_val in self:
                payment_obj = self.env['account.payment'].with_context(active_ids=payment_val.bill_to_pay.ids, active_model='account.move',
                                                                       active_id=payment_val.bill_to_pay.id)
                payment_vals = []
                payment_details = {
                    'payment_type': 'outbound',
                    'partner_type': 'supplier',
                    'payment_method_id': 1,
                    'amount': payment_val.amount,
                    'partner_id': payment_val.payee_id.id,
                    'payment_date': payment_val.date,
                    'journal_id': payment_val.mode_payment.id,
                    'communication': payment_val.bill_to_pay.name,
                    'voucher_payment_id': self.id,

                }
                payment_vals.append(payment_details)
                payment = payment_obj.create(payment_vals)
                payment.post()
                self.payment_id = payment.id

        elif self.compute_tax:
            self.taxpayment()
            self.updateamount()
            for payment_val in self:
                payment_obj = self.env['account.payment'].with_context(active_ids=payment_val.bill_to_pay.ids, active_model='account.move',
                                                                       active_id=payment_val.bill_to_pay.id)
                payment_vals = []
                payment_details = {
                    'payment_type': 'outbound',
                    'partner_type': 'supplier',
                    'payment_method_id': 1,
                    'amount': payment_val.net_amount,
                    'partner_id': payment_val.payee_id.id,
                    'payment_date': payment_val.date,
                    'journal_id': payment_val.mode_payment.id,
                    'communication': payment_val.bill_to_pay.name,
                    'voucher_payment_id': self.id,

                }
                payment_vals.append(payment_details)
                payment = payment_obj.create(payment_vals)
                payment.post()
                self.payment_id = payment.id

                # self.payment_id = payment.id


        self.change_state('process')

    # @api.multi
    # def write(self, values):
    #     #return super(PaymentVoucher, self).write(values)
    #     # Add code here
    #     if values.get('state'):
    #         if values.get('state') == 'process':
    #             payval = []
    #             value = values.get('amount')
    #             pays = values.get('payments')
    #             for val in self.payments:
    #                 payment_obj = self.env['account.payment'].with_context(active_ids=self.bill_to_pay.ids,
    #                                                                        active_model='account.move',
    #                                                                        active_id=self.bill_to_pay.id)
    #                 tax_total = sum(val.amount)
    #                 net_amount = value - tax_total
    #                 payment_vals = {
    #                     'payment_type': 'outbound',
    #                     'partner_type': 'supplier',
    #                     'payment_method_id': 1,
    #                     'amount': net_amount,
    #                     'partner_id': self.payee_id.id,
    #                     'payment_date': self.date,
    #                     'journal_id': self.mode_payment.id,
    #                     'communication': self.bill_to_pay.name,
    #
    #                 }
    #                 payval.append(payment_vals)
    #                 payment_less = payment_obj.create(payval)
    #
    #                 payment_less.post()
    #
    #                 self.payment_id = payment_less.id
    #                 return super(PaymentVoucher, self).write(values)
    #         else:
    #             return super(PaymentVoucher, self).write(values)
    #     else:
    #         return super(PaymentVoucher, self).write(values)


class VoucherDetails(models.Model):
    _name = 'voucher_details.ebs'
    _rec_name = 'name'
    _description = 'New Description'

    name = fields.Char()
    voucher_id = fields.Many2one(comodel_name="payment_voucher.ebs", string="", required=False, )
    details = fields.Text(string="Particulars", required=False, )
    payee_id = fields.Many2one('res.partner', string='Payee', tracking=True)
    rate = fields.Float(string="Rate/Amount",  required=False, )
    payee_type = fields.Selection(
        string='Payee Type',
        selection=[('vendor', 'Vendor'),
                   ('disco', 'Disco'),
                   ('genco', 'Genco'),
                   ('employee', 'Employee'), ],
        required=False, )


class PaymentMandate(models.Model):
    _name = 'payment_mandate.ebs'
    _rec_name = 'mandate_no'
    _description = 'Payment Mandate'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    payee_id = fields.Many2one('res.partner', string='Payee', tracking=True, readonly=True,
                               states={'draft': [('readonly', False)], 'CEO Approval': [('readonly', False)]}, )
    description = fields.Text(string="Description", required=False, )
    date = fields.Date(string="Date", required=False, )
    mandate_ref = fields.Char(string="Mandate Reference")
    amount = fields.Float(string="Amount")
    mode = fields.Selection(string="Mode of settlement", selection=[('Remita', 'Remita'), ('GIFMIS', 'GIFMIS'), ],
                            required=False, )
    account_no = fields.Char(string="Account Number")
    bank = fields.Char(string="Bank")
    account_name = fields.Char(string="Account Name")
    state = fields.Selection(string="",
                             selection=[('draft', 'draft'), ('Forward', 'Forward'), ('FC Review', 'FC Review'),
                                        ('CFO Review', 'CFO Review'), ('CEO Approval', 'CEO Approval'),
                                        ('Audit Review', 'Audit Review'), ('CFO forward', 'CFO forward'), ('FC forward', 'FC forward'),
                                        ('Dispatch', 'Dispatch'), ('acknowledge', 'acknowledge'),
                                        ('Rejected', 'Rejected'), ], required=False, copy=False, default='draft',
                             readonly=True, tracking=True)
    mandate_no = fields.Char(string="Mandate Number", default=lambda self: _('New'), requires=False, readonly=True,
                             trace_visibility='onchange', )

    @api.model
    def create(self, vals):
        if vals.get('mandate_no', _('New')) == _('New'):
            vals['mandate_no'] = self.env['ir.sequence'].next_by_code('increment_payment_mandate') or _('New')
        result = super(PaymentMandate, self).create(vals)
        return result



class DiscoInvoicing(models.Model):
    _name = 'disco_invoicing.ebs'
    _description = 'DiscoInvoicing'

    name = fields.Char(string='Billing Circle', compute="billing_circle")
    month = fields.Selection(selection=[('JAN', 'January'), ('FEB', 'February'), ('MAR', 'March'), ('APR', 'April'),
                              ('MAY', 'May'), ('JUN', 'June'), ('JUL', 'July'), ('AUG', 'August'),
                              ('AUG', 'September'), ('OCT', 'October'), ('NOV', 'November'), ('DEC', 'December'), ],
                             string='Billing Month',)
    year = fields.Selection(selection='_get_years', string='Billing Year', store=True)
    disco = fields.Many2one(comodel_name='res.partner', string='Disco', required=False)
    invoice_date = fields.Date(string='Date of Invoicing', required=False)
    submission_date = fields.Date(string='Invoice Submission Date', required=False)
    minimum_remitance = fields.Float(string='Minimum Remittance Amount', )
    invoice_due_date = fields.Date(string='Invoice Due Date')
    invoice_id = fields.Many2one(string='Invoice', comodel_name='account.move', )
    disco_outstanding = fields.Float(string='Total Outstanding')
    outstanding_no_interest = fields.Float(string='Outstanding less interest',)
    interest_period = fields.Float(string='Interest outstanding for the period',)
    cummulative_interest = fields.Float(string='Total Interest')


    @api.multi
    @api.depends('')
    def _get_years(self):
        year_list = []
        for i in range(2010, 2036):
            year_list.append((i, str(i)))
        return year_list


    @api.one
    @api.depends('month', 'year')
    def billing_circle(self):
        for record in self:
            m = record.month
            y = record.year
            record['name'] = ("%s%s" % (m ,y))


class VoucherType(models.Model):
    _name = 'voucher_type.ebs'
    _description = 'VoucherType'

    name = fields.Char()
    account_id = fields.Many2one(comodel_name='account.account', string='Account')
    analytic_account_id = fields.Many2one(comodel_name='account.analytic.account', string='Budget Line/Analytic Account')
    mode_payment = fields.Many2one(comodel_name='account.journal', string='Payment Account')
    bill_journal = fields.Many2one(comodel_name='account.journal', string='Expense Journal')


class VoucherPayment(models.Model):
    _name = 'voucher_payment.ebs'
    _rec_name = 'name'
    _description = 'payment voucher'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    voucher_type = fields.Many2one(comodel_name="voucher_type.ebs", string='Voucher Type')
    mode_payment = fields.Many2one(comodel_name='account.journal', string='Payment Mode')
    payee_id = fields.Many2one('res.partner', string='Payee', tracking=True, readonly=True,
                               states={'draft': [('readonly', False)], 'Fin Approve': [('readonly', False)]}, )
    cost_centre = fields.Selection(
        string='Cost Centre',
        selection=[('vendor', 'Vendor'),
                   ('disco', 'Disco'),
                   ('genco', 'Genco'),
                   ('employee', 'Employee'),],
        required=False, )
    invoice_id = fields.Many2one(string='Invoice', comodel_name='account.move', )
    rate = fields.Float(string="Amount", required=False, )

# class nbet__process(models.Model):
#     _name = 'nbet__process.nbet__process'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
