# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from datetime import datetime, timedelta

import pytz

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ScrumMeeting(models.Model):
    _inherit = "project.scrum.meeting"

    @api.onchange("start_datetime", "allday", "stop")
    def onchange_dates(self):
        """Returns duration and/or end date based on values passed
        @param self: The object pointer
        """
        if not self.stop and not self.duration:
            self.duration = 1.00
        if self.allday:  # For all day event
            self.duration = 24.00
            # change start_date's time to 00:00:00 in the user's timezone
            user = self.env.user
            tz = pytz.timezone(user.tz) if user.tz else pytz.utc
            start = pytz.utc.localize(self.start).astimezone(tz)
            # convert start in user's timezone
            start = start.replace(hour=0, minute=0, second=0)
            # change start's time to 00:00:00
            start = start.astimezone(pytz.utc)
            # convert start back to utc
            start_date = start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            self.start_date = start_date
        if self.stop and not self.duration:
            self.duration = self._get_duration(self.start_date, self.stop)
        elif not self.stop:
            end = self.start + timedelta(hours=self.duration)
            self.stop = end.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        elif self.stop and self.duration and not self.allday:
            duration = self._get_duration(self.start_date, self.stop)
            self.duration = duration

    @api.onchange("duration")
    def onchange_duration(self):
        """ This method used to update duration based on
            start and stop detail change """
        if self.duration:
            start = fields.Datetime.from_string(
                datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            )
            if self.start_date:
                start = fields.Datetime.from_string(self.start_date)
            self.start_date = start
            self.stop = fields.Datetime.to_string(
                start + timedelta(hours=self.duration)
            )

    def _get_duration(self, start, stop):
        """ Get the duration value between the 2 given dates.
        @param self: The object pointer
        @start self: Start Date
        @stop self: Stop Date
        """
        if start and stop:
            diff = fields.Datetime.from_string(stop) - fields.Datetime.from_string(
                start
            )
            if diff:
                duration = float(diff.days) * 24 + (float(diff.seconds) / 3600)
                return round(duration, 2)
            return 0.0
