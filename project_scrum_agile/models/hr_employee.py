# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    product_id = fields.Many2one('product.product', 'Product')
    journal_id = fields.Many2one('account.journal', 'Analytic Journal')
    project_task_id = fields.Many2one('project.task', 'Task')

