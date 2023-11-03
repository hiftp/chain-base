# See LICENSE file for full copyright and licensing details.

from odoo import api, models


class AnalyticTimesheetInvoiceStartTime(models.TransientModel):
    _name = 'hr.analytic.timesheet.start_time'
    _description = 'HR analytic timesheet start time'

    def button_get_start_time(self):
        """ Set Meeting or Task or Sheet Date to Analytic Line
        @param self: The object pointer
        """
        context = self._context or {}
        sheet_ids = context.get('active_ids', [])
        data_id = self.id or False
        if not data_id or not sheet_ids:
            return False
        for sheet in self.env['account.analytic.line'].browse(sheet_ids):
            date = False
            if sheet.meeting_id:
                date = sheet.meeting_id.start_date
            elif sheet.task_id:
                task_work_id = sheet.task_id[0]
                date = task_work_id.date_assign
            if date:
                sheet.write({'date': date})
        return {'type': 'ir.actions.act_window_close'}
