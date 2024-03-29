# -*- coding: utf-8 -*-
# © 2016 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import datetime
import time
# https://github.com/odoochain/avanzosc-odoo-addons/commit/5f221ca32698326a86fb6cecaedc5d97e0e2153b
# import odoo.addons.decimal_precision as dp
# from odoo import fields, models, api, _
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrContractCn(models.Model):
    _inherit = 'hr.contract'

    social_insurance_amount = fields.Float(
        'Social Insurance Base',
        digits='Payroll'
    )
    housing_fund_base_amount = fields.Float(
        'Housing Fund Base',
        digits='Payroll',
        default=0
    )
    pit_base_amount = fields.Float(
        'PIT Base',
        digits='Payroll',
        default=0
    )
    pit_exemption_amount = fields.Float(
        'Individual Income Tax Threshold',
        required=True,
        digits='Payroll',
        default=5000.00
    )

    @api.constrains('pit_base_amount')
    def _pit_base_amount_check(self):
        for rec in self:
            if not rec.pit_base_amount > 0:
                raise ValidationError(_('PIT Base must be greater than 0.'))


class HrPayrollStructure(models.Model):
    _inherit = "hr.payroll.structure"

    name = fields.Char('Name', required=True, translate=True)


class HrSalaryRuleCategory(models.Model):
    _inherit = "hr.salary.rule.category"

    name = fields.Char('Name', required=True, translate=True)


class HrSalaryRule(models.Model):
    _inherit = "hr.salary.rule"
    _order = "sequence"

    name = fields.Char('Name', required=True, translate=True)


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def compute_sheet(self):
        workday_obj = self.env['hr.payslip.worked_days']
        leaves = {
            'SickLeave': _('Sick Leave'),
            'LongSickLeave': _('Long Sick Leave'),
            'Unpaid': _('Unpaid Leave'),
        }
        for rec in self:
            for (code, name) in leaves.items():
                num = len(
                    [x for x in rec.worked_days_line_ids if x.code == code])
                if not num:
                    vals = {
                        'payslip_id': rec.id,
                        'sequence': 1,
                        'code': code,
                        'name': name,
                        'number_of_days': 0,
                        'number_of_hours': 0,
                        'contract_id': rec.contract_id.id,
                    }
                    workday_obj.create(vals)
        return super(HrPayslip, self).compute_sheet()


class HrPayslipLine(models.Model):
    _inherit = "hr.payslip.line"
    _order = "sequence"


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    _defaults = {
        'entry_date': time.strftime('%Y-%m-%d')
    }

    entry_date = fields.Date(string="Entry Date")
    worked_years = fields.Integer(
        string='Worked Years',
        compute='_compute_worked_years'
    )

    @api.depends('entry_date')
    def _compute_worked_years(self):
        for rec in self:
            if rec.entry_date:
                rec.worked_years = (
                                           datetime.datetime.now() - datetime.datetime.strptime(
                                       str(rec.entry_date), '%Y-%m-%d')
                                   ).days / 360
