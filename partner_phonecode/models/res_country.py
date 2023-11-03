# © 2021 Jerome Guerriat
# © 2021 Niboo SRL (<https://www.niboo.com/>)
# License Other proprietary.

from odoo import models


class ResCountry(models.Model):
    _inherit = "res.country"

    def name_get(self):
        if self.env.context.get("add_phonecode"):
            result = []
            for record in self:
                result.append(
                    (record.id, "+{} ({})".format(record.phone_code, record.name))
                )
        else:
            result = super().name_get()
        return result
