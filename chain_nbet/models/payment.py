from odoo import fields, models, api



class AccountAsset(models.Model):
    _inherit = 'account.payment'

    voucher_payment_id = fields.Many2one(
        comodel_name='payment_voucher.ebs',
        string='Voucher_payment_id',
        required=False)
    approved_by = fields.Many2one('res.users', string='Approved By',
                                  copy=False, tracking=True)
    prepared_by = fields.Many2one('res.users', string='Prepared By',
                                  copy=False, tracking=True, default=lambda self: self.env.user.id)
    entered_by = fields.Many2one('res.users', string='Entered By',
                                 copy=False, tracking=True, default=lambda self: self.env.user.id)
    audited_by = fields.Many2one('res.users', string='Audited By',
                                 copy=False, tracking=True)
    posted_by = fields.Many2one('res.users', string='Posted By',
                                copy=False, tracking=True)
