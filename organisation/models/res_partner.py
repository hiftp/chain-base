
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class Partner(models.Model):
    _inherit = "res.partner"

    sale_ids = fields.One2many('sale.order', 'partner_id', string="Orders")
    invoice_ids = fields.One2many('account.move', 'partner_id',
                                  string="Invoices")
    discipline_ids = fields.One2many('organisation.discipline', 'partner_id',
                                     string="Disciplines")
    org_group_selection = fields.Selection([('organisation', 'Organisation'),
        ('ex_coaches', 'External Coaches'), ('parents', 'Parents'),
        ('athletes', 'Athletes'), ('fans', 'Fans')
    ], string='Organisation Group', index=True, copy=False)
    create_booking = fields.Boolean("Booking creation", default=False,
                                    copy=False, store=True)
    member_id = fields.Char(string="Member ID", store=True, copy=False,
                             readonly=False, related="athlete_id.member_id")
    athlete_id = fields.Many2one('organisation.athletes', string="Athlete")
    # parent_id = fields.Many2one('organisation.parents', string="Parent")
    dob = fields.Date(string="DOB", copy=False, readonly=False)
    age = fields.Integer(string="Age",  compute='_compute_age', store=True)
    nationality_id = fields.Many2one('partner.nationality',
                                     string="Nationality")
    vehicle_ids = fields.Many2many('vehicle.registration',
                                   string="Vehicle Registration",
                                   compute='_compute_vehicle_ids')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string="Gender", )
    height = fields.Integer(string="Height (cm)")
    weight = fields.Float(string="Weight (lbs)")
    secondary_mail = fields.Char()

    @api.depends('dob')
    def _compute_age(self):
        # Get the current date
        today = fields.Date.today()
        for rec in self:
            rec.age = 0
            if rec.dob:
                # Get the difference between the current date and the birthday
                age = relativedelta(today, rec.dob)
                rec.age = age.years

    def action_create_athlete(self):
        """ Open the athlete.creation wizard to create athlete.
                :return: An action opening the athlete.creation wizard.
                """
        if not self.email:
            raise ValidationError(_(
                "Your selected contact does not contains a valid email "
                "\n Please provide email address."))
        return {
            'name': _('Create Athlete'),
            'res_model': 'athlete.creation',
            'view_mode': 'form',
            'context': {
                'active_model': 'res.partner',
                'active_id': self.id,
                'partner_id': self.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def action_create_parent(self):
        """ Open the parent.creation wizard to create parent.
                :return: An action opening the parent.creation wizard.
                """
        if not self.email:
            raise ValidationError(_(
                "Your selected contact does not contains a valid email "
                "\n Please provide email address."))
        return {
            'name': _('Create Parent'),
            'res_model': 'parent.creation',
            'view_mode': 'form',
            'context': {
                'active_model': 'res.partner',
                'active_id': self.id,
                'partner_id': self.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def action_create_athletes(self):
        """ Open the athlete.creation wizard to create athletes.
                :return: An action opening the athlete.creation wizard.
                """
        bad_partners = self.filtered(lambda p: p.org_group_selection)
        if bad_partners:
            raise ValidationError(_(
                "Your selected list contains some contacts where Organisation "
                "Group is already set\n Please remove those contacts from your "
                "selection (%(bad_partners)s).",
                bad_partners=', '.join(bad_partners.mapped('name')),
            ))
        no_email_partners = self.filtered(lambda p: not p.email)
        if no_email_partners:
            raise ValidationError(_(
                "Your selected list contains some contacts who don't have a "
                "Valid Email\n Please set Email or remove those contacts from "
                "your selection (%(bad_partners)s).",
                bad_partners=', '.join(no_email_partners.mapped('name')),
            ))
        return {
            'name': _('Create Athlete'),
            'res_model': 'athlete.creation',
            'view_mode': 'form',
            'context': {
                'active_model': 'res.partner',
                'active_ids': self.ids,
                'partner_ids': self.ids,

            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def action_create_parents(self):
        """ Open the parent.creation wizard to create parents.
                :return: An action opening the parent.creation wizard.
                """
        bad_partners = self.filtered(lambda p: p.org_group_selection)
        if bad_partners:
            raise ValidationError(_(
                "Your selected list contains some contacts where Organisation "
                "Group is already set\n Please remove those contacts from your "
                "selection (%(bad_partners)s).",
                bad_partners=', '.join(bad_partners.mapped('name')),
            ))
        no_email_partners = self.filtered(lambda p: not p.email)
        if no_email_partners:
            raise ValidationError(_(
                "Your selected list contains some contacts who don't have a "
                "Valid Email\n Please set Email or remove those contacts from "
                "your selection (%(bad_partners)s).",
                bad_partners=', '.join(no_email_partners.mapped('name')),
            ))
        return {
            'name': _('Create Parent'),
            'res_model': 'parent.creation',
            'view_mode': 'form',
            'context': {
                'active_model': 'res.partner',
                'active_ids': self.ids,
                'partner_ids': self.ids,

            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def _compute_vehicle_ids(self):
        for partner in self:
            vehicles = self.env['vehicle.registration'].search(
                [('athlete_ids', 'in', partner.athlete_id.id)])
            partner.vehicle_ids = vehicles


class Survey(models.Model):
    _inherit = "survey.survey"

    def _get_default_start_url(self):
        return self.get_start_url()

    start_url = fields.Char(string="Start url",
                            compute='_compute_default_start_url')

    @api.depends('access_token')
    def _compute_default_start_url(self):
        for survey in self:
            survey.start_url = survey.get_start_url() if survey else False


class SurveyUserInputLine(models.Model):
    _inherit = "survey.user_input.line"

    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True,
                                 related='user_input_id.partner_id', store=True)


class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"

    barcode = fields.Char(store=True)
    athlete_id = fields.Many2one('organisation.athletes', string="Athlete")
    member_id = fields.Char(string="Member ID", store=True, readonly=False,
                             related='athlete_id.member_id', copy=False)


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    vehicle_id = fields.Many2one('vehicle.registration',  ondelete='cascade',
                                 string="Vehicle Registration", store=True)


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    def attendance_manual(self, next_action, veh_registration=None, entered_pin=None):
        self.ensure_one()
        can_check_without_pin = not self.env.user.has_group('hr_attendance.group_hr_attendance_use_pin') or (self.user_id == self.env.user and entered_pin is None)
        if can_check_without_pin or entered_pin is not None and entered_pin == self.sudo().pin:
            return self._attendance_action(next_action, veh_registration)
        return {'warning': _('Wrong PIN')}

    def _attendance_action(self, next_action, veh_registration):
        """ Changes the attendance of the employee.
            Returns an action to the check in/out message,
            next_action defines which menu the check in/out message should return to. ("My Attendances" or "Kiosk Mode")
        """
        self.ensure_one()
        employee = self.sudo()
        action_message = self.env["ir.actions.actions"]._for_xml_id("hr_attendance.hr_attendance_action_greeting_message")
        action_message['previous_attendance_change_date'] = employee.last_attendance_id and (employee.last_attendance_id.check_out or employee.last_attendance_id.check_in) or False
        action_message['employee_name'] = employee.name
        action_message['barcode'] = employee.barcode
        action_message['next_action'] = next_action
        action_message['hours_today'] = employee.hours_today

        if employee.user_id:
            modified_attendance = employee.with_user(
                employee.user_id)._attendance_action_change(veh_registration)
        else:
            modified_attendance = employee._attendance_action_change(
                veh_registration)
        action_message['attendance'] = modified_attendance.read()[0]
        return {'action': action_message}

    def _attendance_action_change(self, veh_registration):
        """ Check In/Check Out action
            Check In: create a new attendance record
            Check Out: modify check_out field of appropriate attendance record
        """
        self.ensure_one()
        action_date = fields.Datetime.now()

        if self.attendance_state != 'checked_in':
            vals = {
                'employee_id': self.id,
                'check_in': action_date,
                'vehicle_id': veh_registration
            }
            return self.env['hr.attendance'].create(vals)
        attendance = self.env['hr.attendance'].search([('employee_id', '=', self.id), ('check_out', '=', False)], limit=1)
        if attendance:
            attendance.check_out = action_date
        else:
            raise exceptions.UserError(_('Cannot perform check out on %(empl_name)s, could not find corresponding check in. '
                'Your attendances have probably been modified manually by human resources.') % {'empl_name': self.sudo().name, })
        return attendance


class Nationality(models.Model):
    """model for managing vehicle registration"""
    _name = "partner.nationality"
    _description = "Nationality"
    _rec_name = 'name'

    name = fields.Char("Nationality", required=True)
    country = fields.Char("Country", required=True)
    country_code = fields.Char("Country Code", required=True)
    person = fields.Char("Person", required=True)
