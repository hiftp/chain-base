# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class l10nBeMealVoucherReport(models.Model):
    _name = "l10n_be.meal.voucher.report"
    _description = 'Meal Voucher Summary / Report'
    _auto = False

    employee_id = fields.Many2one('hr.employee', string="Employee", readonly=True)
    day = fields.Date(readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        # Note: Each started day (even if sick during the afternoon, ...) is worth
        # a meal voucher from the employer
        self.env['hr.work.entry'].flush()
        self.env['hr.work.entry.type'].flush()
        self._cr.execute("""
            CREATE or REPLACE view %s as (
                WITH hr_time_zone_work_entries AS (
                          SELECT work_entry.employee_id,
                                 timezone(calendar.tz, work_entry.date_start::timestamptz) AS date_start,
                                 timezone(calendar.tz, work_entry.date_stop::timestamptz) AS date_stop,
                                 work_entry_type_id
                            FROM hr_work_entry AS work_entry
                      INNER JOIN hr_contract AS contract ON work_entry.contract_id = contract.id
                      INNER JOIN resource_calendar AS calendar ON contract.resource_calendar_id = calendar.id
                      WHERE      work_entry.state IN ('draft', 'validated')
                )
                SELECT
                    row_number() OVER() AS id,
                    b.date_start_day::date AS day,
                    b.employee_id
                FROM (
                     /* Split work entry by day */
                    SELECT
                        b1.employee_id AS employee_id,
                        GREATEST(s, b1.date_start) AS date_start_day,
                        LEAST(s + interval '1 day', b1.date_stop) AS date_stop_day
                    FROM
                        hr_time_zone_work_entries b1
                    CROSS JOIN generate_series(date_trunc('day', b1.date_start), date_trunc('day', b1.date_stop), interval '1 day') s
                    INNER JOIN hr_work_entry_type t ON t.id = b1.work_entry_type_id
                    WHERE t.meal_voucher = TRUE
                ) AS b
                GROUP BY b.employee_id, b.date_start_day::date, b.date_stop_day::date
                HAVING SUM(date_part('hour', b.date_stop_day - b.date_start_day)) > 0
            );
        """ % self._table)
