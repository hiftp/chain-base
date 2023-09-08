from odoo import api, fields, models
from num2words import num2words
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _compute_amount_in_word(self):
        for rec in self:
            rounded = round(rec.amount_total, 2)
            rec.num_word = str(rec.currency_id.amount_to_text(rounded)) + ' only'

    num_word = fields.Char(string="Amount In Words:", compute='_compute_amount_in_word')


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    def _compute_amount_in_word(self):
        for rec in self:
            rounded = round(rec.amount_total, 2)
            rec.num_word = str(rec.currency_id.amount_to_text(rounded)) + ' only'

    num_word = fields.Char(string="Amount In Words:", compute='_compute_amount_in_word')


class InvoiceOrder(models.Model):
    _inherit = 'account.move'

    def _compute_amount_in_word(self):
        for rec in self:
            rounded = round(rec.amount_total, 2)
            if rec.currency_id.name == 'SAR':

                def sar_amt2words(amount, currency='Riyals', change='Halala', precision=2):
                    change_amt = round((amount - int(amount)) * pow(10, precision))
                    words = '{main_amt} {main_word}'.format(
                        main_amt=num2words(int(amount)),
                        main_word=currency,
                    )
                    if change_amt > 0:
                        words += ' and {change_amt} {change_word}'.format(
                            change_amt=num2words(change_amt),
                            change_word=change,
                        )
                    return words

                rec.num_word = str(sar_amt2words(rounded)).title() + ' only'

            elif rec.currency_id.name == 'USD':

                def usd_amt2words(amount, currency='Dollars', change='Cents', precision=2):
                    change_amt = round((amount - int(amount)) * pow(10, precision))
                    words = '{main_amt} {main_word}'.format(
                        main_amt=num2words(int(amount)),
                        main_word=currency,
                    )
                    if change_amt > 0:
                        words += ' and {change_amt} {change_word}'.format(
                            change_amt=num2words(change_amt),
                            change_word=change,
                        )
                    return words

                rec.num_word = str(usd_amt2words(rounded)).title() + ' only'

            elif rec.currency_id.name == 'AED':

                def aed_amt2words(amount, currency='Dirham', change='Fils', precision=2):
                    change_amt = round((amount - int(amount)) * pow(10, precision))
                    words = '{main_amt} {main_word}'.format(
                        main_amt=num2words(int(amount)),
                        main_word=currency,
                    )
                    if change_amt > 0:
                        words += ' and {change_amt} {change_word}'.format(
                            change_amt=num2words(change_amt),
                            change_word=change,
                        )
                    return words

                rec.num_word = str(aed_amt2words(rounded)).title() + ' only'

            elif rec.currency_id.name == 'CHF':

                def chf_amt2words(amount, currency='Franc', change='Centimes', precision=2):
                    change_amt = round((amount - int(amount)) * pow(10, precision))
                    words = '{main_amt} {main_word}'.format(
                        main_amt=num2words(int(amount)),
                        main_word=currency,
                    )
                    if change_amt > 0:
                        words += ' and {change_amt} {change_word}'.format(
                            change_amt=num2words(change_amt),
                            change_word=change,
                        )
                    return words

                rec.num_word = str(chf_amt2words(rounded)).title() + ' only'


            elif rec.currency_id.name == 'GBP':

                def gbp_amt2words(amount, currency='Sterling', change='Penny', precision=2):
                    change_amt = round((amount - int(amount)) * pow(10, precision))
                    words = '{main_amt} {main_word}'.format(
                        main_amt=num2words(int(amount)),
                        main_word=currency,
                    )
                    if change_amt > 0:
                        words += ' and {change_amt} {change_word}'.format(
                            change_amt=num2words(change_amt),
                            change_word=change,
                        )
                    return words

                rec.num_word = str(gbp_amt2words(rounded)).title() + ' only'


            elif rec.currency_id.name == 'EUR':

                def eur_amt2words(amount, currency='Euro', change='Cents', precision=2):
                    change_amt = round((amount - int(amount)) * pow(10, precision))
                    words = '{main_amt} {main_word}'.format(
                        main_amt=num2words(int(amount)),
                        main_word=currency,
                    )
                    if change_amt > 0:
                        words += ' and {change_amt} {change_word}'.format(
                            change_amt=num2words(change_amt),
                            change_word=change,
                        )
                    return words

                rec.num_word = str(eur_amt2words(rounded)).title() + ' only'






    num_word = fields.Char(string="Amount In Words:", compute='_compute_amount_in_word')
