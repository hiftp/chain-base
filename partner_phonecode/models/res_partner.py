# © 2020 Jerome Guerriat
# © 2020 Niboo SRL (<https://www.niboo.com/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import phonenumbers

from odoo import _, api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    phone_country_id = fields.Many2one("res.country")
    mobile_country_id = fields.Many2one("res.country")
    mobile_number = fields.Char(string="Mobile Number")
    phone_number = fields.Char(string="Phone Number")
    phone = fields.Char(compute="_compute_phones")
    mobile = fields.Char(compute="_compute_phones")

    @api.depends(
        "phone_country_id", "mobile_country_id", "mobile_number", "phone_number"
    )
    def _compute_phones(self):
        for partner in self:
            phone = partner.phone_number
            if partner.phone_country_id:
                phone = f"+{partner.phone_country_id.phone_code} {phone}"
            partner.phone = phone

            mobile = partner.mobile_number
            if partner.mobile_country_id:
                mobile = f"+{partner.mobile_country_id.phone_code} {mobile}"
            partner.mobile = mobile

    @api.onchange("country_id", "phone_country_id", "phone_number")
    def check_phone(self):
        self.ensure_one()
        if self.country_id and self.phone_country_id.phone_code and self.phone_number:
            number = "+{}{}".format(self.phone_country_id.phone_code, self.phone_number)
            number = number.replace(" ", "")
            partner_phone = phonenumbers.parse(number, self.phone_country_id.code)
            if not phonenumbers.is_valid_number(partner_phone):
                return {
                    "warning": {
                        "title": _("Warning"),
                        "message": _(
                            "Warning: %s does not seem to be a valid "
                            "phone number for country %s"
                        )
                        % (number, self.phone_country_id.name),
                    }
                }

    @api.onchange("country_id", "mobile_country_id", "mobile_number")
    def check_mobile(self):
        self.ensure_one()
        if self.country_id and self.mobile_country_id.phone_code and self.mobile_number:
            number = "+{}{}".format(
                self.mobile_country_id.phone_code, self.mobile_number
            )
            number = number.replace(" ", "")
            partner_mobile = phonenumbers.parse(number, self.mobile_country_id.code)
            if not phonenumbers.is_valid_number(partner_mobile):
                return {
                    "warning": {
                        "title": _("Warning"),
                        "message": _(
                            "Warning: %s does not seem to be a valid "
                            "mobile number for country %s"
                        )
                        % (number, self.mobile_country_id.name),
                    }
                }
