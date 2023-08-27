from odoo import api, fields, models, _
import time

from odoo.exceptions import ValidationError


class Interest(models.Model):
    _name = 'interest'
    _description = 'Interest'
    _order = 'active desc, name'

    name = fields.Char(string='Name', required=True)
    rate = fields.Float(compute='_compute_current_rate',
                        string='Current Rate',
                        digits=(16, 2),
                        help='The rate current interest rate')
    rate_ids = fields.One2many('interest.rate', 'interest_id', string='Rates')
    active = fields.Boolean(default=True)
    date = fields.Date(compute='_compute_date')
    company_id = fields.Many2one('res.company',
                                 string='Company',
                                 default=lambda self: self.env.company)

    _sql_constraints = [
        ('unique_name', 'unique (name,company_id)',
         'The interest name must be unique!'),
    ]

    @api.model
    def _get_rate(self, date):
        self.ensure_one()
        rates = self.rate_ids.filtered(lambda rate: rate.name <= date).sorted(
            key='name', reverse=True)
        return rates[0].rate if len(rates) else 0.0

    @api.depends('rate_ids.rate')
    def _compute_current_rate(self):
        date = fields.Date.today()
        for interest in self:
            interest.rate = interest._get_rate(date)

    @api.depends('rate_ids.name')
    def _compute_date(self):
        for interest in self:
            interest.date = interest.rate_ids[:1].name


class InterestAdjusted(models.Model):
    _name = 'interest.adjusted'
    _description = 'Interest Adjusted'
    _order = 'name'

    name = fields.Char('Name',
                       compute='_compute_name',
                       readonly=True,
                       store=True)
    rate = fields.Float(compute='_compute_current_rate',
                        string='Current Rate',
                        digits=(16, 2),
                        help='The rate current interest rate')
    interest_id = fields.Many2one('interest', string='Interest', required=True)
    adjustment_type = fields.Selection(selection=[('plus', 'Plus'),
                                                  ('minus', 'Minus')],
                                       string='Adjustment Type',
                                       default='plus',
                                       required=True)
    adjustment_rate = fields.Float(string='Adjustment Rate',
                                   digits=(16, 2),
                                   default=0.0,
                                   help='The adjustment rate interest rate')
    date = fields.Date(compute='_compute_date')
    company_id = fields.Many2one('res.company',
                                 string='Company',
                                 default=lambda self: self.env.company)

    _sql_constraints = [
        ('unique_name', 'unique (name, company_id)',
         'The name must be unique!'),
    ]

    @api.constrains('adjustment_rate')
    def _check_adjustment_rate(self):
        if self.adjustment_rate < 0 or self.adjustment_rate > 100:
            raise ValidationError(
                _('Adjustment Rate value must be a percent.'))

    @api.depends('interest_id', 'adjustment_rate')
    @api.onchange('interest_id', 'adjustment_rate')
    def _compute_name(self):
        for interest_adjusted in self:
            interest_adjusted.name = _('%s %s%s%%') % (
                interest_adjusted.interest_id.name,
                '+' if interest_adjusted.adjustment_type == 'plus' else '-',
                interest_adjusted.adjustment_rate)

    @api.model
    def _get_rate(self, date):
        self.ensure_one()
        rates = self.interest_id.rate_ids.filtered(
            lambda rate: rate.name <= date).sorted(key='name', reverse=True)
        rate = rates[0].rate if len(rates) else 0.0
        return max(
            rate +
            self.adjustment_rate if self.adjustment_type == 'plus' else rate -
            self.adjustment_rate, 0.0)

    @api.depends('interest_id.rate_ids')
    def _compute_current_rate(self):
        date = fields.Date.today()
        for interest_adjusted in self:
            interest_adjusted.rate = interest_adjusted._get_rate(date)

    @api.depends('interest_id.rate_ids')
    def _compute_date(self):
        for interest_adjusted in self:
            interest_adjusted.date = interest_adjusted.interest_id.rate_ids[:
                                                                            1].name


class InterestRate(models.Model):
    _name = 'interest.rate'
    _description = 'Interest Rate'
    _order = 'name desc'

    name = fields.Date(string='Date',
                       required=True,
                       index=True,
                       default=lambda self: fields.Date.today())
    rate = fields.Float(string='Rate',
                        digits=(16, 2),
                        default=0.0,
                        help='The rate of interest')
    interest_id = fields.Many2one('interest', string='Interest', required=True)

    _sql_constraints = [
        ('unique_name_per_day', 'unique (name,interest_id)',
         'Only one interest rate per day allowed!'),
    ]

    @api.constrains('rate')
    def _check_rate(self):
        if self.rate < 0 or self.rate > 100:
            raise ValidationError(_('Rate value must be a percent.'))

    @api.model
    def _name_search(self,
                     name,
                     args=None,
                     operator='ilike',
                     limit=100,
                     name_get_uid=None):
        if operator in ['=', '!=']:
            try:
                date_format = '%Y-%m-%d'
                if self._context.get('lang'):
                    lang_id = self.env['res.lang']._search(
                        [('code', '=', self._context['lang'])],
                        access_rights_uid=name_get_uid)
                    if lang_id:
                        date_format = self.browse(lang_id).date_format
                name = time.strftime('%Y-%m-%d',
                                     time.strptime(name, date_format))
            except ValueError:
                try:
                    args.append(('rate', operator, float(name)))
                except ValueError:
                    return []
                name = ''
                operator = 'ilike'
        return super(InterestRate,
                     self)._name_search(name,
                                        args=args,
                                        operator=operator,
                                        limit=limit,
                                        name_get_uid=name_get_uid)
