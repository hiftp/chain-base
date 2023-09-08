# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # athlete dashboard configuration
    athlete_profile = fields.Boolean(string="Profile", default=True,
                                     help="Check to enable PROFILE DASHBOARD"
                                          "tab for ATHLETES")
    athlete_booking = fields.Boolean(string="Booking", default=True,
                                     help="Check to enable BOOKING DASHBOARD"
                                          "tab for ATHLETES")
    athlete_calendar = fields.Boolean(string="Calendar", default=True,
                                      help="Check to enable CALENDAR DASHBOARD"
                                           "tab for ATHLETES")
    athlete_products = fields.Boolean(string="Products", default=True,
                                      help="Check to enable PRODUCTS DASHBOARD"
                                           "tab for ATHLETES")
    athlete_forms = fields.Boolean(string="Forms", default=True,
                                   help="Check to enable FORMS DASHBOARD"
                                          "tab for ATHLETES")
    athlete_documents = fields.Boolean(string="Documents", default=True,
                                       help="Check to enable DOCUMENTS "
                                            "DASHBOARD tab for ATHLETES")
    athlete_timesheet = fields.Boolean(string="Timesheet", default=True,
                                       help="Check to enable TIMESHEET "
                                            "DASHBOARD tab for ATHLETES")
    athlete_coaches = fields.Boolean(string="Coaches", default=True,
                                     help="Check to enable COACH DASHBOARD"
                                          "tab for ATHLETES")
    athlete_invoices = fields.Boolean(string="Invoices", default=True,
                                      help="Check to enable INVOICE DASHBOARD"
                                           "tab for ATHLETES")
    athlete_parents = fields.Boolean(string="Parents", default=True,
                                     help="Check to enable PARENT DASHBOARD"
                                          "tab for ATHLETES")
    athlete_chat_hub = fields.Boolean(string="Chat-Hub", default=True,
                                      help="Check to enable CHAT-HUB DASHBOARD"
                                           "tab for ATHLETES")
    athlete_assignments = fields.Boolean(string="Assignments", default=True,
                                         help="Check to enable ASSIGNMENTS "
                                              "DASHBOARD tab for ATHLETES")
    athlete_attendance = fields.Boolean(string="Attendance", default=True,
                                        help="Check to enable ATTENDANCE "
                                             "DASHBOARD tab for ATHLETES")
    # parent dashboard configuration
    parents = fields.Boolean(string="Parents", default=True,
                             help="Check to enable PARENTS")
    parent_profile = fields.Boolean(string="Profile", default=True,
                                    help="Check to enable PROFILE DASHBOARD"
                                         "tab for PARENTS")
    parent_invoices = fields.Boolean(string="Invoice", default=True,
                                     help="Check to enable INVOICE DASHBOARD"
                                     "tab for PARENTS")
    parent_chat_hub = fields.Boolean(string="Chat-Hub", default=True,
                                     help="Check to enable CHAT-HUB DASHBOARD"
                                     "tab for PARENTS")
    parent_attendance = fields.Boolean(string="Attendance", default=True,
                                       help="Check to enable ATTENDANCE DASHBOARD"
                                            "tab for PARENTS")
    # fan dashboard configuration
    fans = fields.Boolean(string="Fans", default=True,
                          help="Check to enable FANS")
    fan_profile = fields.Boolean(string="Profile", default=True,
                                 help="Check to enable PROFILE DASHBOARD"
                                      "tab for FANS")
    fan_calendar = fields.Boolean(string="Calendar", default=True,
                                  help="Check to enable CALENDAR DASHBOARD"
                                       "tab for FANS")
    fan_booking = fields.Boolean(string="Booking", default=True,
                                 help="Check to enable BOOKING DASHBOARD"
                                      "tab for FANS")
    # coach dashboard configuration
    coach_profile = fields.Boolean(string="Profile", default=True,
                                   help="Check to enable PROFILE DASHBOARD"
                                          "tab for COACHES")
    coach_booking = fields.Boolean(string="Booking", default=True,
                                   help="Check to enable Booking DASHBOARD"
                                        "tab for COACHES")
    coach_calendar = fields.Boolean(string="Calendar", default=True,
                                    help="Check to enable CALENDAR DASHBOARD"
                                         "tab for COACHES")
    coach_assignments = fields.Boolean(string="Assignments", default=True,
                                       help="Check to enable ASSIGNMENTS "
                                            "DASHBOARD tab for COACHES")
    coach_forms = fields.Boolean(string="Forms", default=True,
                                 help="Check to enable FORMS DASHBOARD"
                                      "tab for COACHES")
    coach_chat_hub = fields.Boolean(string="Chat-hub", default=True,
                                    help="Check to enable CHAT-HUB DASHBOARD"
                                         "tab for COACHES")
    coach_timesheet = fields.Boolean(string="Timesheet", default=True,
                                     help="Check to enable TIMESHEET DASHBOARD"
                                          "tab for COACHES")
    coach_invoice = fields.Boolean(string="Invoice", default=True,
                                   help="Check to enable INVOICE DASHBOARD"
                                        "tab for COACHES")
    coach_attendance = fields.Boolean(string="Attendance", default=True,
                                      help="Check to enable ATTENDANCE "
                                           "DASHBOARD tab for COACHES")
    default_org_id = fields.Many2one('organisation.organisation', default=False,
                                     string="Default Organisation",
                                     default_model='res.company',
                                     related='company_id.org_id',
                                     readonly=False)
    athlete_from_fan = fields.Boolean(string="Create Athlete from Fan",
                                      default=False,
                                      help="Check this field to enable the "
                                           "smart button to create a new "
                                           "Athlete from fan record")
    fan_from_athlete = fields.Boolean(string="Create Fan from Athlete",
                                      default=True,
                                      help="Check this field to enable the "
                                           "smart button to create a new "
                                           "Fan from athlete record")
    # ui
    mobile = fields.Selection(selection=[('12', 'One'), ('6', 'Two')],
                              string='Mobile Device', default='12')

    tablet = fields.Selection(selection=[('6', 'Two'), ('4', 'Three')],
                              string='Tablet Device', default='6')

    desktop = fields.Selection(selection=[('4', 'Three'), ('3', 'Four')],
                               string='Desktop Device', default='4')

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        # self.env['ir.config_parameter'].set_param(
        #     'organisation.default_org_id', self.default_org_id.id)
        self.env['ir.config_parameter'].set_param(
            'organisation.athlete_profile', self.athlete_profile)
        self.env['ir.config_parameter'].set_param(
            'organisation.athlete_booking', self.athlete_booking)
        self.env['ir.config_parameter'].set_param(
            'organisation.athlete_calendar', self.athlete_calendar)
        self.env['ir.config_parameter'].set_param(
            'organisation.athlete_products', self.athlete_products)
        self.env['ir.config_parameter'].set_param(
            'organisation.athlete_forms', self.athlete_forms)
        self.env['ir.config_parameter'].set_param(
            'organisation.athlete_documents', self.athlete_documents)
        self.env['ir.config_parameter'].set_param(
            'organisation.athlete_timesheet', self.athlete_timesheet)
        self.env['ir.config_parameter'].set_param(
            'organisation.athlete_coaches', self.athlete_coaches)
        self.env['ir.config_parameter'].set_param(
            'organisation.athlete_invoices', self.athlete_invoices)
        self.env['ir.config_parameter'].set_param(
            'organisation.athlete_parents', self.athlete_parents)
        self.env['ir.config_parameter'].set_param(
            'organisation.athlete_chat_hub', self.athlete_chat_hub)
        self.env['ir.config_parameter'].set_param(
            'organisation.athlete_assignments', self.athlete_assignments)
        self.env['ir.config_parameter'].set_param(
            'organisation.athlete_attendance', self.athlete_attendance)
        self.env['ir.config_parameter'].set_param(
            'organisation.parents', self.parents)
        self.env['ir.config_parameter'].set_param(
            'organisation.parent_profile', self.parent_profile)
        self.env['ir.config_parameter'].set_param(
            'organisation.parent_invoices', self.parent_invoices)
        self.env['ir.config_parameter'].set_param(
            'organisation.parent_chat_hub', self.parent_chat_hub)
        self.env['ir.config_parameter'].set_param(
            'organisation.parent_attendance', self.parent_attendance)
        self.env['ir.config_parameter'].set_param(
            'organisation.fans', self.fans)
        self.env['ir.config_parameter'].set_param(
            'organisation.fan_profile', self.fan_profile)
        self.env['ir.config_parameter'].set_param(
            'organisation.fan_booking', self.fan_booking)
        self.env['ir.config_parameter'].set_param(
            'organisation.fan_calendar', self.fan_calendar)
        self.env['ir.config_parameter'].set_param(
            'organisation.coach_profile', self.coach_profile)
        self.env['ir.config_parameter'].set_param(
            'organisation.coach_booking', self.coach_booking)
        self.env['ir.config_parameter'].set_param(
            'organisation.coach_calendar', self.coach_calendar)
        self.env['ir.config_parameter'].set_param(
            'organisation.coach_assignments', self.coach_assignments)
        self.env['ir.config_parameter'].set_param(
            'organisation.coach_forms', self.coach_forms)
        self.env['ir.config_parameter'].set_param(
            'organisation.coach_chat_hub', self.coach_chat_hub)
        self.env['ir.config_parameter'].set_param(
            'organisation.coach_timesheet', self.coach_timesheet)
        self.env['ir.config_parameter'].set_param(
            'organisation.coach_invoice', self.coach_invoice)
        self.env['ir.config_parameter'].set_param(
            'organisation.coach_attendance', self.coach_attendance)
        self.env['ir.config_parameter'].set_param(
            'organisation.athlete_from_fan', self.athlete_from_fan)
        self.env['ir.config_parameter'].set_param(
            'organisation.fan_from_athlete', self.fan_from_athlete)
        # ui
        self.env['ir.config_parameter'].set_param(
            'organisation.mobile', self.mobile)
        self.env['ir.config_parameter'].set_param(
            'organisation.tablet', self.tablet)
        self.env['ir.config_parameter'].set_param(
            'organisation.desktop', self.desktop)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            # default_org_id=params.get_param('organisation.default_org_id'),
            athlete_profile=params.get_param('organisation.athlete_profile'),
            athlete_booking=params.get_param('organisation.athlete_booking'),
            athlete_calendar=params.get_param('organisation.athlete_calendar'),
            athlete_products=params.get_param('organisation.athlete_products'),
            athlete_forms=params.get_param('organisation.athlete_forms'),
            athlete_documents=params.get_param(
                'organisation.athlete_documents'),
            athlete_timesheet=params.get_param(
                'organisation.athlete_timesheet'),
            athlete_coaches=params.get_param('organisation.athlete_coaches'),
            athlete_invoices=params.get_param('organisation.athlete_invoices'),
            athlete_parents=params.get_param('organisation.athlete_parents'),
            athlete_chat_hub=params.get_param('organisation.athlete_chat_hub'),
            athlete_assignments=params.get_param(
                'organisation.athlete_assignments'),
            athlete_attendance=params.get_param(
                'organisation.athlete_attendance'),
            parents=params.get_param('organisation.parents'),
            parent_profile=params.get_param('organisation.parent_profile'),
            parent_invoices=params.get_param('organisation.parent_invoices'),
            parent_chat_hub=params.get_param('organisation.parent_chat_hub'),
            parent_attendance=params.get_param(
                'organisation.parent_attendance'),
            fans=params.get_param('organisation.fans'),
            fan_profile=params.get_param('organisation.fan_profile'),
            fan_booking=params.get_param('organisation.fan_booking'),
            fan_calendar=params.get_param('organisation.fan_calendar'),
            coach_profile=params.get_param('organisation.coach_profile'),
            coach_booking=params.get_param('organisation.coach_booking'),
            coach_calendar=params.get_param('organisation.coach_calendar'),
            coach_assignments=params.get_param(
                'organisation.coach_assignments'),
            coach_forms=params.get_param('organisation.coach_forms'),
            coach_chat_hub=params.get_param('organisation.coach_chat_hub'),
            coach_timesheet=params.get_param('organisation.coach_timesheet'),
            coach_invoice=params.get_param('organisation.coach_invoice'),
            coach_attendance=params.get_param('organisation.coach_attendance'),
            athlete_from_fan=params.get_param('organisation.athlete_from_fan'),
            fan_from_athlete=params.get_param('organisation.fan_from_athlete'),
            # ui
            mobile=params.get_param('organisation.mobile'),
            tablet=params.get_param('organisation.tablet'),
            desktop=params.get_param('organisation.desktop'),
        )
        return res


