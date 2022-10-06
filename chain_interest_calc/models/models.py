# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo import models, fields, api, tools
import re


class NiborRate(models.Model):
    _name = 'nibor.rate'
    _description = 'Nibor Rate'

    name = fields.Date(string='Date', required=True, index=True,
                       default=fields.Date.context_today)
    rate = fields.Float(digits=(12, 6), default=1.0, help='The rate of the currency to the currency of rate 1')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id)


    _sql_constraints = [
        ('unique_name_per_day', 'unique (name,company_id)', 'Only one Nibor rate per day allowed!'),
        ('currency_rate_check', 'CHECK (rate>0)', 'The Nibor rate must be strictly positive.'),
    ]


class InterestRate(models.Model):
    _name = 'interest.rate'
    _description = 'Interest Rate'

    name = fields.Char()
    add_rate = fields.Float(digits=(12, 6), default=1.0, string='Additional Rate')
    nibor_rate = fields.Float(compute='_get_latest_rate')
    interest_total_rate = fields.Float(compute='_get_rate')

    @api.depends('nibor_rate')
    def _get_rate(self):
        self.interest_total_rate = self.nibor_rate + self.add_rate

    def _get_latest_rate(self):
        rates = self.env['nibor.rate'].search([])[-1]
        self.nibor_rate = rates.rate


class ResPartner(models.Model):
    _inherit = 'res.partner'

    interest_rate = fields.Many2one(
        comodel_name='interest.rate',
        string='Interest rate',
        required=False)
    interest_ids = fields.One2many(
        comodel_name='interest.calculation',
        inverse_name='disco',
        string='Interest ',
        required=False)


class InterestCalculations(models.Model):
    _name = 'interest.calculation'
    _description = 'Interest Calculations'

    name = fields.Date(string='Date', required=True, index=True,
                       default=fields.Date.context_today)
    nibor_rate = fields.Float()
    interest_rate = fields.Float()
    interest = fields.Float()
    outstanding = fields.Float(
        string='Outstanding',
        required=False)
    cumulative_interest = fields.Float(compute='cumulative_interest')
    previous_balance = fields.Float(string='previous balance', compute='_previous_record', store=True)
    disco = fields.Many2one(
        comodel_name='res.partner',
        string='Disco',
        required=False)
    # add_rate = fields.Float(digits=(12, 6), default=1.0, string='Additional Rate')

    def create_interest(self):
        disco = self.env['res.partner'].search([('customer', '=', True),])
        disco_outstanding = []
        interest_env = self.env['interest.calculation']
        for rec in disco:
            interest = rec.credit * rec.interest_rate.interest_total_rate / 100
            real_interest = interest / 365
            vals = {
                'disco': rec.id,
                'outstanding': rec.credit,
                'interest_rate': rec.interest_rate.interest_total_rate,
                'interest': real_interest,
                'nibor_rate': rec.interest_rate.nibor_rate,


            }
            disco_outstanding.append(vals)
            interest_env.create(disco_outstanding)

    # @api.one
    # @api.depends('disco', )
    # def _previous_record(self):
    #     for record in self:
    #         balance_ids = self.env['interest.calculation'].search([('disco', '=', self.disco.id), ('id', '<', record.id)],
    #                                                      order='id desc', limit=1)
    #         previous_record = balance_ids[0]['cumulative_interest'] if balance_ids else 0
    #         self.previous_balance = previous_record

    @api.depends('previous_balance')
    def cumulative_interest(self):
        self.cumulative_interest = self.previous_balance + self.interest



    # def _get_rate(self):
    #     self.interest_rate = self.nibor_rate + self.add_rate

    @api.depends('interest_rate')
    def compute_interest(self):
        outstanding = self.outstanding
        interest_rate = self.interest_rate / 100
        self.interest = outstanding * interest_rate / 365

# class interest_calc(models.Model):
#     _name = 'interest_calc.interest_calc'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100