# See LICENSE file for full copyright and licensing details.

import re
import time
from datetime import datetime, timedelta

from odoo import api, fields, models, _, tools
from odoo import tools, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class Meeting(models.Model):
    _inherit = "calendar.event"

    @api.depends('allday', 'start', 'stop')
    def _compute_dates(self):
        """ Overriden to make sure duration is set to zero for all day events.
        """
        super()._compute_dates()
        for meeting in self:
            if meeting.allday and meeting.start and meeting.stop:
                meeting.duration = 0.0
            else:
                meeting.duration = self._get_duration(meeting.start, meeting.stop)

    start = fields.Datetime(
        default=datetime.now(),
    )
    stop = fields.Datetime(
        default=datetime.now(),
        )

    status = fields.Selection([
        ('new', 'New'),
        ('confirm', 'Confirmed'),
        ('performed', 'Performed'),
        ('canceled', 'Canceled')],
        'State', index=True,
        default='new'
    )
    project_id = fields.Many2one('project.project', 'Project')
    scrum_meeting_id = fields.Many2one(
        'project.scrum.meeting',
        'Meeting Sprint'
    )
    analytic_timesheet_id = fields.Many2one(
        'account.analytic.line',
        'Related Timeline',
        ondelete='set null'
    )

    def to_extend_sprint(self):
        """ Create Sprint Meeting
        @param self: The object pointer
        """
        vals = {}
        for meeting in self:
            if meeting.duration:
                vals['start'] = meeting.start
                vals['duration'] = meeting.duration
                start_datetime = vals.get('start')
                start_string_date = datetime.strftime(start_datetime, DEFAULT_SERVER_DATETIME_FORMAT)
                stop_date = datetime.strptime(start_string_date,
                                              DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(
                    hours=vals.get('duration'))
                vals['stop_date'] = datetime.strftime(stop_date,
                                                      DEFAULT_SERVER_DATETIME_FORMAT)
            if meeting.allday is True:
                vals['start_date'] = meeting.start_date
                vals['stop_date'] = meeting.stop_date
            if not meeting.scrum_meeting_id:
                vals['meeting_id'] = meeting.id
                self.env['project.scrum.meeting'].create(vals)

    def set_new(self):
        self.write({'status': 'new'})

    def set_cancel(self):
        for meeting in self:
            meeting.analytic_timesheet_id.unlink()
            meeting.write({'status': 'canceled'})

    def set_confirm(self):
        for meeting in self:
            meeting.write({'status': 'confirm'})

    def set_validate(self):
        for meeting in self:
            self.validate(meeting)
            meeting.write({'status': 'performed'})

    def validate(self, meeting):
        """ Create Account Analytic Line from Meeting
        @param self: The object pointer
        """
        project_obj = self.env['project.project']
        vals_line = {}
        if not meeting.project_id:
            raise ValidationError(_('Please select the Project before '
                                    'validating Meeting!!'))
        project = meeting.project_id
        emp_id = self.env.user.employee_id
        if not emp_id.product_id:
            raise ValidationError(_("""Define Product On Employee %s"""
                                    % emp_id.name))
        if not emp_id.journal_id:
            raise ValidationError(_("""Define Journal On Related Employee %s""" % emp_id.name))

        acc_id = emp_id.product_id.property_account_expense_id.id
        if not acc_id:
            acc_id = \
                emp_id.product_id.categ_id.property_account_expense_categ_id.id
            if not acc_id:
                raise ValidationError(
                    _('Please define product and product category \
                        property account on the related employee.\nFill\
                         in the timesheet tab of the employee form.'))
        vals_line['name'] = \
            'Reunion %s: %s' % (tools.ustr(project_obj.name), tools.ustr(
                meeting.name or '/'))
        vals_line['user_id'] = meeting.user_id.id or self.env.user
        vals_line['date'] = meeting.start_date
        vals_line['meeting_id'] = meeting.id
        vals_line['unit_amount'] = 8 if meeting.allday else meeting.duration
        vals_line['product_id'] = emp_id.product_id.id
        vals_line['general_account_id'] = acc_id
        vals_line['product_uom_id'] = emp_id.product_id.uom_id.id
        vals_line['account_id'] = project.analytic_account_id.id
        if vals_line['product_id']:
            amount = \
                self.env['product.product']. \
                    browse(vals_line['product_id']).standard_price
            vals_line['amount'] = amount * vals_line['unit_amount']
        timeline_id = self.env['account.analytic.line'].create(vals_line)
        meeting.write({'analytic_timesheet_id': timeline_id.id})
        return True


class ProjectScrumSprint(models.Model):
    _name = 'project.scrum.sprint'
    _description = 'Project Scrum Sprint'
    _inherit = ['mail.thread']
    _order = "date_start desc"

    def button_open(self):
        for record in self:
            stories = record.product_backlog_ids
            if not stories:
                raise ValidationError(_(
                    "You can not open sprint with no stories affected in"))
            else:
                record.write({'state': 'open'})

    def button_cancel(self):
        for sprint in self:
            sprint.write({'state': 'cancel'})

    def button_draft(self):
        for sprint in self:
            sprint.write({'state': 'draft'})

    def button_close(self):
        for sprint in self:
            sprint.write({'state': 'done'})
            sprint.meeting_ids.write({'status': 'performed'})

    def button_pending(self):
        for sprint in self:
            sprint.write({'state': 'pending'})

    def update_burndownchart(self):
        """ This Method Calculate Burndown Chart Data from Backlogs
        @param self: The object pointer
        """
        for sprint in self:
            today = fields.Date.context_today(self)
            sprint.burndown_ids.unlink()
            date_start = sprint.date_start
            date_stop = sprint.date_stop
            total_days = (date_stop - date_start).days
            sums = sprint.expected_hours
            assign = sums
            for day in range(-1, total_days + 2):
                date_date = (date_start + timedelta(days=day))
                date = date_date
                sum_points = 0
                if date <= today:
                    for backlog in sprint.product_backlog_ids:
                        if (not backlog.date_done) or \
                            (backlog.date_done and
                             backlog.date_done < date):
                            sum_points += backlog.complexity
                        for task in backlog.tasks_id:
                            for work in task.timesheet_ids:
                                if work.date == date:
                                    sums -= work.unit_amount
                                    assign = sums
                else:
                    assign = 0
                data = {
                    'sprint_id': sprint.id,
                    'date': date,
                    'remaining_hours': assign,
                    'remaining_points': sum_points,
                    'date_day': date,
                }
                self.env['project.scrum.sprint.burndown.log'].create(data)

    def _compute_effective_velocity(self):
        """ Calculate complexity of backlog
        @param self: The object pointer
        """
        user_story_obj = self.env['project.scrum.product.backlog']
        for sprint in self:
            user_story_recs = user_story_obj.search_read([
                ('sprint_id', '=', sprint.id)], ['complexity'])
            velocity = \
                sum(rec.get('complexity') for rec in user_story_recs)
            sprint.effective_velocity = velocity

    @api.depends('product_backlog_ids', 'product_backlog_ids.expected_hours',
                 'product_backlog_ids.effective_hours')
    def _compute_hours(self):
        for sprint in self:
            tot = prog = effective = progress = 0.0
            for backlog_id in sprint.product_backlog_ids:
                tot += backlog_id.expected_hours
                effective += backlog_id.effective_hours
                prog += backlog_id.expected_hours * backlog_id.progress / 100.0

            if tot > 0:
                progress = round(prog / tot * 100)
            sprint.progress = progress
            sprint.expected_hours = tot
            sprint.effective_hours = effective

    def _compute_meeting_count(self):
        """ Compute number of Meeting for particular Sprint
        @param self: The object pointer
        """
        for sprint_id in self:
            sprint_id.meeting_count = len(sprint_id.meeting_ids)

    name = fields.Char('Sprint Name')
    date_start = fields.Date(
        'Starting Date',
        default=lambda *a: time.strftime('%Y-%m-%d')
    )
    date_stop = fields.Date('Ending Date')
    release_id = fields.Many2one(
        'project.scrum.release',
        'Release'
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project'
    )
    product_owner_id = fields.Many2one(
        'res.users',
        'Product Owner',
        domain=lambda self: [('groups_id', 'in', self.env.ref(
            'project_scrum_agile.group_scrum_owner').ids)],
        help="The person who is responsible for the product"
    )
    scrum_master_id = fields.Many2one(
        'res.users',
        'Scrum Master',
        domain=lambda self: [('groups_id', 'in', self.env.ref(
            'project_scrum_agile.group_scrum_master').ids)],
        help="The person who maintains the process for the product"
    )
    meeting_ids = fields.One2many(
        'project.scrum.meeting',
        'sprint_id',
        'Daily Scrum'
    )
    review = fields.Text('Sprint Review')
    retrospective_start_to_do = fields.Text('Start to do')
    retrospective_continue_to_do = fields.Text('Continue to do')
    retrospective_stop_to_do = fields.Text('Stop to do')
    effective_hours = fields.Float(
        "Effective hours",
        compute='_compute_hours',
        help="Computed using the sum of the task work done.",
    )
    progress = fields.Float(
        'Progress (0-100)',
        compute='_compute_hours',
        help="Computed as: Time Spent / Total Time.",
        group_operator="avg",
    )
    expected_hours = fields.Float(
        "Expected Hours",
        compute='_compute_hours',
        help='Expected hours to do the task.',
        recursive=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('pending', 'Pending'),
        ('cancel', 'Cancelled'),
        ('done', 'Done')],
        'State', tracking=True,
        default='draft'
    )
    goal = fields.Char("Goal")
    effective_velocity = fields.Integer(
        "Effective Velocity",
        compute='_compute_effective_velocity',
        help="Computed using the sum of the task work done."
    )
    burndown_ids = fields.One2many(
        'project.scrum.sprint.burndown.log',
        'sprint_id',
        'BurndownChart'
    )
    product_backlog_ids = fields.One2many(
        'project.scrum.product.backlog',
        'sprint_id',
        "User Stories",
    )
    sprint_number = fields.Char(
        'Sprint number',
        readonly=True,
        copy=False,
        help="Sprint number sequence"
    )
    color = fields.Integer('Color Index')
    meeting_count = fields.Integer(
        "Number of Meeting",
        compute='_compute_meeting_count',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('sprint_number'):
                vals['sprint_number'] = self.env['ir.sequence'].next_by_code(
                    'product.sprint.number') or '/'
        return super(ProjectScrumSprint, self).create(vals_list)

    @api.depends('name', 'sprint_number')
    def name_get(self):
        res = []
        for sprint in self:
            name = tools.ustr(sprint.name)
            if sprint.sprint_number:
                name = '[' + tools.ustr(sprint.sprint_number) + ']' + ' ' + name
            res.append((sprint.id, name))
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            sprint = self.env['project.scrum.sprint']
            if operator in positive_operators:
                sprint = self.search(
                    [('sprint_number', operator, name)] + args, limit=limit)
                if not sprint:
                    sprint = self.search(args + [
                        ('sprint_number', operator, name)], limit=limit)
                    if not limit or len(sprint) < limit:
                        limit2 = (limit - len(sprint)) if limit else False
                        sprint += self.search(args + [
                            ('name', operator, name)], limit=limit2)
                if not sprint:
                    ptrn = re.compile('(\[(.*?)\])')
                    pattern_name = ptrn.search(name)
                    if pattern_name:
                        sprint = self.search([
                                                 ('sprint_number', '=',
                                                  pattern_name.group(2)
                                                  )] + args,
                                             limit=limit)
        else:
            sprint = self.search(args, limit=limit)
        return sprint.name_get()

    @api.constrains('date_start', 'date_stop')
    def _check_dates(self):
        for sprint in self:
            if sprint.date_start > sprint.date_stop:
                raise ValidationError(_(
                    'The start date must be anterior to the end date !'))

    @api.onchange('project_id')
    def _onchange_project_id(self):
        self.release_id = False

    def unlink(self):
        for sprint in self:
            if sprint.state not in ['draft', 'cancel']:
                raise ValidationError(_('You can delete sprint in '
                                        'draft or cancel state only!!'))
        return super(ProjectScrumSprint, self).unlink()


class ScrumMeeting(models.Model):
    _name = 'project.scrum.meeting'
    _description = 'Project Scrum Meeting'
    _order = 'start_date desc'

    meeting_id = fields.Many2one(
        'calendar.event',
        'Meeting Related',
        delegate=True,
        required=True,ondelete='cascade',
    )
    sprint_id = fields.Many2one('project.scrum.sprint', 'Sprint')
    scrum_master_id = fields.Many2one(
        'res.users',
        'Scrum Master',
        related='sprint_id.scrum_master_id',
    )
    product_owner_id = fields.Many2one(
        'res.users',
        'Product Owner',
        related='sprint_id.product_owner_id',
    )
    question_yesterday = fields.Text('Tasks since yesterday')
    question_today = fields.Text('Tasks for today')
    question_blocks = fields.Text('Blocks encountered')
    what_we_did = fields.Text('What was done during the meeting')
    task_ids = fields.Many2many(
        'project.task',
        'project_scrum_meeting_task_rel',
        'meeting_id', 'task_id',
        'Tasks'
    )
    user_story_ids = fields.Many2many(
        'project.scrum.product.backlog',
        'project_scrum_meeting_story_rel',
        'meeting_id',
        'story_id',
        'Stories'
    )
    sandbox_ids = fields.One2many(
        'project.scrum.sandbox',
        'meeting_id',
        'Sandbox'
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            duration = 0
            if vals.get('duration'):
                duration = vals.get('duration')
            if vals.get('start_date') and vals.get('duration'):
                vals['start_date'] = vals.get('start_date')
                vals['start'] = vals.get('start')
            if vals.get('start_date') and vals.get('duration'):
                start = datetime.strptime(vals.get('start_date'), '%Y-%m-%d')
                start_datetime = datetime.strftime(start, DEFAULT_SERVER_DATETIME_FORMAT)
                stop_date = datetime.strptime(start_datetime,
                                              DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(
                    hours=duration)
                vals['stop_date'] = datetime.strftime(stop_date,
                                                      DEFAULT_SERVER_DATETIME_FORMAT)
            if vals.get('start_date'):
                if isinstance(vals.get('start_date'), str):
                    start = datetime.strptime(vals.get('start_date'), '%Y-%m-%d')
                    start_datetime = datetime.strftime(start, DEFAULT_SERVER_DATETIME_FORMAT)
                    stop_date = datetime.strptime(start_datetime,
                                                  DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(
                        hours=duration)
                    vals['stop_date'] = datetime.strftime(stop_date,
                                                          DEFAULT_SERVER_DATETIME_FORMAT)
                else:
                    start = datetime.strftime(vals.get('start_date'), DEFAULT_SERVER_DATETIME_FORMAT)
                    start_datetime = datetime.strptime(start, DEFAULT_SERVER_DATETIME_FORMAT)
                    stop_date = datetime.strftime(start_datetime,
                                                  DEFAULT_SERVER_DATETIME_FORMAT)
                    vals['stop_date'] = datetime.strptime(stop_date,
                                                          DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(
                        hours=duration)
            if not vals.get('start'):
                vals.update({'start': vals.get('start_date')})
        res = super(ScrumMeeting, self).create(vals_list)
        for rec in res:
            rec.meeting_id.write({'scrum_meeting_id': rec.id})
        return res

    def send_email(self):
        """ Send Email individual to Owner and Master
        @param self: The object pointer
        """
        context = self._context or {}
        if context.get('type') == 'master':
            if self.sprint_id.scrum_master_id.partner_id and self.sprint_id. \
                scrum_master_id.partner_id.email:
                res = self.email_send(self.sprint_id.scrum_master_id.
                                      partner_id)
                if not res:
                    raise ValidationError(_(
                        'Email notification'
                        ' could not be sent to the scrum master %s')
                                          % self.sprint_id.
                                          scrum_master_id.name)
            else:
                raise ValidationError(_(
                    'Please provide email address'
                    ' for scrum master defined on sprint.'))
        if context.get('type') == 'owner':
            if self.sprint_id.product_owner_id.partner_id and self.sprint_id. \
                product_owner_id.partner_id.email:
                res = self.email_send(self.sprint_id.product_owner_id.
                                      partner_id)
                if res is False:
                    raise ValidationError(_(
                        'Email notification could not be sent'
                        ' to the product owner %s') % self.sprint_id.
                                          product_owner_id.name)
            else:
                raise ValidationError(_(
                    'Please provide email address for product owner'
                    ' defined on sprint.'))

    def email_send(self, partner_id):
        """ Send Email To Owner and Master Both From Wizard
        @param self: The object pointer
        """
        email_from = tools.config.get('email_from', False)
        user = self.env.user
        user_email = email_from or user.partner_id.email
        vals = {}
        mail_temp = self.env.ref('project_scrum_agile.email_template_project_scrum', raise_if_not_found=True)
        body = """
                <div>
                Hello %s,
                <br/>
                <p style="margin:10px;">Meeting is done successfully.Details are mentioned below:</p>
                </div>
                <div style="margin:10px;">
                <p>Project  : %s</p>
                <p>Sprint : %s</p>
                <p>Tasks since yesterday : %s</p>
                <p>Task for Today : %s</p>
                <p>Blocking points encountered : %s</p>
                <p>Thank you, %s</p>
                <p>%s</p>
                </div>
                """ \
               % (self.partner_id.name,
                  self.project_id.name,
                  self.sprint_id.name,
                  self.question_yesterday or '',
                  self.question_today or '',
                  self.question_blocks or '',
                  user.name, user.signature
                  )
        vals['email_from'] = user_email
        vals['email_to'] = partner_id.email
        vals['body_html'] = body
        mail_temp.write(vals)
        mail_id = mail_temp.send_mail(self.id, force_send=True)
        return True

    def set_new(self):
        for meeting in self:
            meeting.write({'status': 'new'})

    def set_cancel(self):
        for meeting in self:
            meeting.analytic_timesheet_id.unlink()
            meeting.write({'status': 'canceled'})

    def set_confirm(self):
        for meeting in self:
            meeting.write({'status': 'confirm'})

    def set_validate(self):
        for meeting_id in self:
            self.validate(meeting_id.meeting_id)
            meeting_id.write({'status': 'performed'})

    def unlink(self):
        for meeting in self:
            if meeting.status not in ['new', 'canceled']:
                raise ValidationError(_('You can delete Scrum Meeting in '
                                        'new or cancel state only!!'))
        return super(ScrumMeeting, self).unlink()

    def validate(self, meeting):
        """ Create Analytic Line For Meeting
        @param self: The object pointer
        @param meeting: Meeting Id
        """
        vals_line = {}
        if not meeting.project_id:
            raise ValidationError(_('Please select the Project before '
                                    'validating Meeting!!'))
        project = meeting.project_id
        result = self.get_user_related_details(meeting.user_id and meeting.
                                               user_id.id or self.env.user)
        vals_line['name'] = 'Reunion %s: %s' % (tools.ustr(project.name),
                                                tools.ustr(meeting.name or '/')
                                                )
        vals_line['user_id'] = meeting.user_id and meeting.user_id.id or \
                               self.env.user
        vals_line['product_id'] = result['product_id']
        vals_line['date'] = meeting.start_date
        vals_line['meeting_id'] = meeting.id
        vals_line['unit_amount'] = meeting.allday and 8 or meeting.duration
        vals_line['account_id'] = project.analytic_account_id.id
        vals_line['general_account_id'] = result['general_account_id']
        vals_line['product_uom_id'] = result['product_uom_id']
        if result['product_id']:
            amount = self.env['product.product'].browse(
                result['product_id']).standard_price
            vals_line['amount'] = amount * vals_line['unit_amount']
        timeline_id = self.env['account.analytic.line'].create(vals_line)
        meeting.write({'analytic_timesheet_id': timeline_id.id})
        return True

    def get_user_related_details(self, user_id):
        """ Find User Related Details
        @param self: The object pointer
        @param user_id: User Id
        """
        res = {}
        emp_id = self.env.user.employee_id
        user_id = self.env.user
        if not emp_id.product_id:
            raise ValidationError(_("""Define Product On Employee %s"""
                                    % emp_id.name))
        if not emp_id.journal_id:
            raise ValidationError(_("""Define Journal On Related Employee %s""" % emp_id.name))
        acc_id = emp_id.product_id.property_account_expense_id.id
        if not acc_id:
            acc_id = emp_id.product_id.categ_id. \
                property_account_expense_categ_id.id
            if not acc_id:
                raise ValidationError(
                    _('Please define product and product category property'
                      'account on the related employee.'
                      '\nFill in the timesheet tab of the employee form.'))
        res['product_id'] = emp_id.product_id.id
        res['general_account_id'] = acc_id
        res['journal_id'] = emp_id.journal_id.id
        res['product_uom_id'] = emp_id.product_id.uom_id.id
        return res

    def copy(self, default=None):
        default = dict(default or {})
        default.update({'status': 'new'})
        return super(ScrumMeeting, self).copy(default)

    @api.onchange('project_id')
    def _onchange_project_id(self):
        self.sprint_id = self.env.context.get('default_sprint_id', False)

    @api.onchange('partner_ids')
    def _onchange_partner_ids(self):
        """ The basic purpose of this method is to check that destination
        partners
            effectively have email addresses. Otherwise a warning is thrown.
        @param self: The object pointer
        """
        res = {'value': {}}
        if not self.partner_ids:
            return {}
        res.update(self.check_partners_email(self.partner_ids))
        return res

    def check_partners_email(self, partner_ids):
        """ Verify that selected partner_ids have an email_address defined.
            Otherwise throw a warning.
        @param self: The object pointer
        @param partner_ids: List Of Parters
        """
        partner_email_lst = [partner for partner in partner_ids
                             if not partner.email]
        if not partner_email_lst:
            return {}
        warning_msg = _('The following contacts have no email address :')
        for partner in partner_email_lst:
            warning_msg += '\n- %s' % partner.name
        raise UserError(_('Email addresses not found.\n%s.') % warning_msg)


class ProjectScrumSprintBurndownLog(models.Model):
    _name = 'project.scrum.sprint.burndown.log'
    _description = 'Project Scrum Sprint Burndown Log'

    sprint_id = fields.Many2one('project.scrum.sprint', 'Sprint',
                                required=True)
    date = fields.Date('Date')
    remaining_hours = fields.Float('Hours left')
    remaining_points = fields.Float('Remaining Points')
    real_data = fields.Boolean('Real data')
    date_day = fields.Char("Date Day")


class ProjectScrumProductBacklog(models.Model):
    _name = 'project.scrum.product.backlog'
    _description = "Product backlog where are user stories"
    _inherit = ['mail.thread']
    _order = "priority desc ,sequence"

    @api.depends('name', 'backlog_number')
    def name_get(self):
        res = []
        for record in self:
            name = tools.ustr(record.name)
            if record.backlog_number and name:
                name = '[' + tools.ustr(record.backlog_number) + ']' + ' ' + name
            res.append((record.id, name))
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            backlog = self.env['project.scrum.product.backlog']
            if operator in positive_operators:
                backlog = self.search(
                    [('backlog_number', operator, name)] + args, limit=limit)
                if not backlog:
                    backlog = \
                        self.search(args +
                                    [('backlog_number', operator, name)],
                                    limit=limit)
                    if not limit or len(backlog) < limit:
                        limit2 = (limit - len(backlog)) if limit else False
                        backlog += self.search(args +
                                               [('name', operator, name)],
                                               limit=limit2)
                if not backlog:
                    ptrn = re.compile('(\[(.*?)\])')
                    pattern_name = ptrn.search(name)
                    if pattern_name:
                        backlog = self.search([
                                                  ('backlog_number', '=', pattern_name.group(2))
                                              ] + args, limit=limit)
        else:
            backlog = self.search(args, limit=limit)
        return backlog.name_get()

    @api.depends('tasks_id',
                 'tasks_id.effective_hours', 'tasks_id.planned_hours')
    def _compute_hours(self):
        for backlog in self:
            tot = prog = effective = task_hours = progress = 0.0
            for task in backlog.tasks_id:
                task_hours += task.planned_hours
                effective += task.effective_hours
                tot += task.planned_hours
                prog += task.planned_hours * task.progress / 100.0
            if tot > 0:
                progress = round(prog / tot * 100)
            # TODO display an error message if tot==0
            #             (division by 0 is impossible)
            backlog.progress = progress
            backlog.effective_hours = effective
            backlog.task_hours = task_hours

    def _get_default_stage_id(self):
        """ Gives default stage_id
        @param self: The object pointer
        """
        project_id = self.env.context.get('default_project_id')
        if not project_id:
            return False
        return self.stage_find(project_id, [('fold', '=', False)])

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = ['|', ('default_view', '=', True), ('fold', '=', True)]
        if 'default_project_id' in self.env.context:
            search_domain = \
                ['|', ('project_ids', '=',
                       self.env.context['default_project_id'])] + search_domain
        stage_ids = stages._search(search_domain, order=order,
                                   access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    def stage_find(self, section_id, domain=[], order='sequence'):
        """ Override of the base.stage method
            Parameter of the stage search taken from the lead:
            - section_id: if set, stages must belong to this section or
              be a default stage; if not set, stages must be default
              stages
        """
        # collect all section_ids
        section_ids = []
        if section_id:
            section_ids.append(section_id)
        section_ids.extend(self.mapped('project_id').ids)
        search_domain = []
        if section_ids:
            search_domain = [('|')] * (len(section_ids) - 1)
            for section_id in section_ids:
                search_domain.append(('project_ids', '=', section_id))
        search_domain += list(domain)
        # perform search, return the first found
        return self.env['project.task.type'].search(search_domain, order=order,
                                                    limit=1).id

    name = fields.Char(
        'Title',
        required=True,
        translate=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    for_then = fields.Text(
        'For',
        translate=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    acceptance_testing = fields.Text(
        "Proof of acceptance",
        translate=True,
        readonly=False,
        states={'done': [('readonly', True)]}
    )
    description = fields.Text(
        "Wants",
        translate=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    sequence = fields.Integer(
        'Sequences',
        help="Gives the sequence order when"
             "displaying a list of product backlog.",
        default=1000
    )
    expected_hours = fields.Float(
        'Planned Hours',
        help='Estimated total time to do the Backlog'
    )
    complexity = fields.Integer(
        'Story Points',
        help='Complexity of the User Story'
    )
    active = fields.Boolean(
        'Active',
        help="If Active field is set to true, it will allow you to hide"
             "the product backlog without removing it.",
        default=True
    )
    value_to_user = fields.Integer("Value for the user", default=50)
    open = fields.Boolean('Open', tracking=True, default=True)
    date_open = fields.Date("Start date")
    date_done = fields.Date("End date")
    project_id = fields.Many2one('project.project', "Project", readonly=True,
                                 states={'draft': [('readonly', False)]})
    release_id = fields.Many2one(
        'project.scrum.release',
        "Release",
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    sprint_id = fields.Many2one(
        'project.scrum.sprint',
        "Sprint", readonly=True,
        states={'draft': [('readonly', False)]}
    )
    user_id = fields.Many2one(
        'res.users',
        'Author',
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env.user
    )
    task_id = fields.Many2one(
        'project.task',
        "Related Task",
        ondelete='restrict',
        help='Task-related data of the user story'
    )
    tasks_id = fields.One2many(
        'project.task',
        'product_backlog_id',
        'Tasks Details'
    )
    progress = fields.Float(
        'Progress',
        compute='_compute_hours',
        group_operator="avg",
        help="Computed as: Time Spent / Total Time.",
        compute_sudo=True
    )
    effective_hours = fields.Float(
        'Spent Hours',
        compute='_compute_hours',
        help="Computed using the sum of the time spent"
             "on every related tasks",
        store=True,
    )
    task_hours = fields.Float(
        'Task Hours',
        compute='_compute_hours',
        help='Estimated time of the total hours of the tasks',
        recursive=True,
        compute_sudo=True
    )
    color = fields.Integer('Color Index')
    note = fields.Text('Internal Note', translate=True)
    responsible_id = fields.Many2one(
        'res.users',
        'Responsible',
        tracking=True,
        default=lambda self: self.env.user
    )
    role_job_id = fields.Many2one('hr.job', 'Who')
    role_id = fields.Many2one(
        'res.partner',
        "Listener",
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    delivery_date = fields.Date('Deliver date')
    backlog_number = fields.Char(
        'Number Requirement',
        readonly=True,
        copy=False,
        help="Sequence number of request"
    )
    asked_date = fields.Date('Application Date')
    company_id = fields.Many2one(
        'res.company',
        'Company',
        default=lambda self: self.env.user.company_id
    )
    kanban_state = fields.Selection([
        ('normal', 'Normal'),
        ('blocked', 'Blocked'),
        ('done', 'Ready for next stage')],
        'Kanban State',
        tracking=True,
        help="A task's kanban state indicates special"
             "situations affecting it:\n"
             " * Normal is the default situation\n"
             " * Blocked indicates something is preventing"
             "the progress of this task\n"
             " * Ready for next stage indicates the"
             "task is ready to be pulled to the next stage",
        readonly=True,
        default='normal'
    )
    # remove below field "backlog_stage_state" from next version onwards
    backlog_stage_state = fields.Selection(related='stage_id.state')
    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'In Progress'),
        ('pending', 'Pending'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')],
        "Status",
        store=True,
        tracking=True,
        readonly=True,
        help='The status is set to \'Draft\', when a case is created.\
        If the case is in progress the status is set to \'Open\'.\
        When the case is over, the status is set to \'Done\'.\
        If the case needs to be reviewed then the status is \
        set to \'Pending\'.',
        default='draft'
    )
    stage_id = fields.Many2one(
        'project.task.type',
        'Stage',
        tracking=True,
        index=True,
        default=_get_default_stage_id,
        domain="['&', ('fold', '=', False), ('project_ids', '=', project_id)]",
        group_expand='_read_group_stage_ids',
        copy=False
    )
    categ_ids = fields.Many2many('project.tags', string='Tags')
    priority = fields.Selection(selection_add=[('0', 'Deferred Priority'),
                                 ('1', 'Low Priority'),
                                 ('2', 'Medium Priority'),
                                 ('3', 'High Priority'),
                                 ('4', 'Critical Priority'),
                                 ('5', 'Blocker Priority'),
                                 ], default='0', string="Priority", index=True, tracking=True)

    @api.onchange('project_id')
    def _onchange_project(self):
        self.release_id = False
        if self.project_id:
            self.stage_id = self.stage_find(self.project_id.id, [
                ('fold', '=', False)])
        else:
            self.stage_id = False

    @api.onchange('release_id')
    def onchange_release_id(self):
        self.sprint_id = False

    def set_hours(self):
        context = self._context
        remain_time = 1.0
        remain_time = 1.0 if context.get('context_id') == 1.0 else remain_time
        remain_time = 2.0 if context.get('context_id') == 2.0 else remain_time
        remain_time = 4.0 if context.get('context_id') == 4.0 else remain_time
        remain_time = 8.0 if context.get('context_id') == 8.0 else remain_time
        remain_time = 16.0 if context. \
                                  get('context_id') == 16.0 else remain_time
        remain_time = 32.0 if context. \
                                  get('context_id') == 32.0 else remain_time
        remain_time = 64.0 if context. \
                                  get('context_id') == 64.0 else remain_time
        self.write({'expected_hours': remain_time})

    def write(self, vals):
        """ Add Message Follower when user and responsible user changed
        @param self: The object pointer
        """
        if 'user_id' in vals:
            user = self.env['res.users'].browse(vals.get('user_id'))
            for req in self:
                message_follower_ids = req.message_follower_ids or []
                for partner_ids in message_follower_ids:
                    if user.partner_id.id != partner_ids.partner_id.id:
                        self.env['mail.followers']._insert_followers(
                            self._name, [req.id], [user.partner_id.id],
                            None, {}, None, [])

        if 'responsible_id' in vals:
            user = self.env['res.users'].browse(vals.get('responsible_id'))
            for req in self:
                message_follower_ids = req.message_follower_ids or []
                for partner_ids in message_follower_ids:
                    if user.partner_id.id != partner_ids.partner_id.id:
                        self.env['mail.followers']._insert_followers(
                            self._name, [req.id], [user.partner_id.id], None,
                            {}, None, [])
        return super(ProjectScrumProductBacklog, self).write(vals)

    def button_open(self):
        for backlog_id in self:
            stage_id = self.env['project.task.type'].search(
                [('state', '=', 'in_progress')], limit=1)
            if not stage_id:
                raise ValidationError(_(
                    'In Progress stage not found! Please Create one'))
            if not backlog_id.sprint_id or not backlog_id.acceptance_testing:
                raise ValidationError(_("""
                One of the following configuration is still missing.\n
                    Please configure all the following details \n
                    * You must affect this user story in a
                    sprint before open it.
                    * You must define acceptance testing
                    before open this user story
                                        """))

            date = fields.Date.today()
            backlog_id.write({'state': 'open',
                              'date_open': date,
                              'stage_id': stage_id.id
                              })
            for tasks_id in backlog_id.tasks_id:
                tasks_id.write({'stage_id': stage_id.id, 'active': True})

    def button_cancel(self):
        stage_id = self.env['project.task.type'].search(
            [('state', '=', 'cancelled')], limit=1)
        if not stage_id:
            raise ValidationError(_(
                'Cancelled stage not found! Please Create one'))
        for backlog in self:
            backlog.write({
                'stage_id': stage_id.id,
                'state': 'cancelled',
                'active': True
            })
            for tasks_id in backlog.tasks_id:
                tasks_id.write({'stage_id': stage_id.id, 'active': True})

    def button_close(self):
        stage_id = self.env['project.task.type'].search(
            [('state', '=', 'done')], limit=1)
        if not stage_id:
            raise ValidationError(_('Done Stage Not Found! Please Create one'))
        for backlog in self:
            for task in backlog.tasks_id:
                if task.stage_id.state != 'done':
                    raise ValidationError(_('All tasks must be completed'))
                else:
                    self._get_velocity_sprint_done()
                    for (sprint_id, name) in backlog.sprint_id.name_get():
                        self.message_post(body=_(
                            "The sprint '%s' has been closed." % name),
                            subject="Record Updated")
            backlog.write({'stage_id': stage_id.id})

    def button_reactivate(self):
        stage_id = self.env['project.task.type'].search(
            [('state', '=', 'design')], limit=1)
        if not stage_id:
            raise ValidationError(_('Design Stage Not Found! Please Create one'))
        for backlog in self:
            backlog.write({
                'stage_id': stage_id.id,
                'state': 'open',
                'active': True
            })
            for task_id in backlog.tasks_id:
                task_id.write({'active': True})
                if task_id.stage_id.name != 'Done':
                    task_id.write({'active': True})

    def _get_velocity_sprint_done(self):
        velocity = 0
        stage_id = self.env['project.task.type'].search(
            [('state', '=', 'design')], limit=1)
        if not stage_id:
            raise ValidationError(_('Design Stage Not Found! Please Create one'))
        for backlog_id in self.search([('sprint_id', '=', self.sprint_id.id)]):
            backlog_id.write({'stage_id': stage_id.id, 'state': 'open'})
            velocity += backlog_id.complexity
        self.sprint_id.write({'effective_velocity': velocity})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('backlog_number'):
                vals['backlog_number'] = self.env['ir.sequence'].next_by_code(
                    'product.backlog.number') or '/'
        return super(ProjectScrumProductBacklog, self).create(vals_list)

    @api.constrains('date_open', 'date_done')
    def _check_dates(self):
        for backlog in self:
            if (backlog.date_open and backlog.date_done) and (
                backlog.date_open > backlog.date_done):
                raise ValidationError(_(
                    'The start date must be anterior to the end date !'))


class ProjectTask(models.Model):
    _inherit = 'project.task'

    name = fields.Char('Homework', translate=True)
    product_backlog_id = fields.Many2one(
        'project.scrum.product.backlog',
        'Product Backlog',
        help="Related product backlog that contains this task."
             "Used in SCRUM methodology"
    )
    sprint_id = fields.Many2one(
        'project.scrum.sprint',
        'Sprint',
        related='product_backlog_id.sprint_id',
        store=True,
        readonly=True
    )
    release_id = fields.Many2one(
        'project.scrum.release',
        'Release',
        related='sprint_id.release_id',
        store=True,
        readonly=True
    )
    description = fields.Html('Description', translate=True)
    warn = fields.Boolean('Email alert')
    creator_id = fields.Many2one('res.users', 'Created By')
    email = fields.Char(
        'Send mail',
        help='An email will be sent upon completion and upon validation of the'
             'Task to the following recipients. Separate with comma (,)'
             'each recipient ex: example@email.com, test@email.com'
    )
    write_date = fields.Date('Modified Date')
    partner_ids = fields.Many2many(
        'res.partner',
        'task_mail_compose_message_res_partner_rel',
        'task_id',
        'partner_id',
        'Contacts to notify'
    )
    incidents = fields.One2many('project.task', 'task_id', 'Incidents')
    task_id = fields.Many2one('project.task', 'Task')
    task_number = fields.Char(
        'Task Number',
        readonly=True,
        copy=False,
        help="Sequence of the task number"
    )
    type = fields.Selection([
        ('task', 'Task'),
        ('issue', 'Issue'),
    ], required=True, default='task',
        help="The 'Type' is used for bifurcation of "
             "Task and Issue.")
    priority = fields.Selection(selection_add=[('0', 'Deferred Priority'),
                                 ('1', 'Low Priority'),
                                 ('2', 'Medium Priority'),
                                 ('3', 'High Priority'),
                                 ('4', 'Critical Priority'),
                                 ('5', 'Blocker Priority'),
                                 ], string="Priority")

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'kanban_state' in init_values and self.kanban_state == 'blocked':
            return self.env.ref('project.mt_task_blocked')
        elif 'kanban_state' in init_values and self.kanban_state == 'done':
            return self.env.ref('project_scrum_agile.mt_task_started')
        elif 'user_id' in init_values and self.user_id:  # assigned -> new
            return self.env.ref('project.mt_task_new')
        elif 'stage_id' in init_values and self.stage_id and self.stage_id. \
            sequence <= 1:  # start stage -> new
            return self.env.ref('project.mt_task_new')
        elif 'stage_id' in init_values:
            return self.env.ref('project.mt_task_stage')
        return super(ProjectTask, self)._track_subtype(init_values)

    @api.depends('name', 'task_number')
    def name_get(self):
        res = []
        for task_id in self:
            name = tools.ustr(task_id.name)
            if task_id.task_number:
                name = '[' + tools.ustr(task_id.task_number) + ']' + ' ' + name
            res.append((task_id.id, name))
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            tasks = self.env['project.task']
            if operator in positive_operators:
                tasks = self.search(
                    [('task_number', operator, name)] + args, limit=limit)
                if not tasks:
                    tasks = self.search(args +
                                        [('task_number', operator, name)],
                                        limit=limit)
                    if not limit or len(tasks) < limit:
                        limit2 = (limit - len(tasks)) if limit else False
                        tasks += self.search(args +
                                             [('name', operator, name)],
                                             limit=limit2)
                if not tasks:
                    ptrn = re.compile('(\[(.*?)\])')
                    pattern_name = ptrn.search(name)
                    if pattern_name:
                        tasks = self.search([
                                                ('task_number', '=', pattern_name.group(2))
                                            ] + args, limit=limit)
        else:
            tasks = self.search(args, limit=limit)
        return tasks.name_get()

    @api.onchange('product_backlog_id')
    def _onchange_backlog_id(self):
        if not self.product_backlog_id:
            return {}
        self.project_id = self.product_backlog_id.project_id.id

    @api.onchange('type')
    def _onchange_type(self):
        if self.type == 'issue' and self.incidents:
            self.incidents = [(5,)]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('task_number'):
                vals['task_number'] = self.env['ir.sequence'].next_by_code(
                    'project.task.number') or '/'
        return super(ProjectTask, self).create(vals_list)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    date_to = fields.Datetime(
        'Date Up',
        default=lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    )
    meeting_id = fields.Many2one('calendar.event', 'Related Meeting')
    task_id = fields.Many2one('project.task', 'Related Tasks')
    date = fields.Date('Date', required=True)
    project_id = fields.Many2one(
        'project.project',
        'Project'
    )


class MailAlias(models.Model):
    _inherit = 'mail.alias'

    @api.model_create_multi
    def create(self, vals_list):
        """ Creates an email.alias record according to the values provided in ``vals``,
            with 2 alterations: the ``alias_name`` value may be suffixed in order to
            make it unique (and certain unsafe characters replaced), and
            he ``alias_model_id`` value will set to the model ID of the ``model_name``
            context value, if provided.
        """
        model_name = self._context.get('alias_model_name')
        parent_model_name = self._context.get('alias_parent_model_name')
        for vals in vals_list:
            if vals.get('alias_name'):
                vals['alias_name'] = self._clean_and_check_unique(vals.get('alias_name'))
            if model_name:
                model = self.env['ir.model']._get(model_name)
                vals['alias_model_id'] = model.id
            if parent_model_name:
                model = self.env['ir.model']._get(parent_model_name)
                vals['alias_parent_model_id'] = model.id
        return super(MailAlias, self).create(vals_list)


class ProjectProject(models.Model):
    _inherit = 'project.project'

    release_ids = fields.One2many(
        'project.scrum.release',
        'project_id',
        "Releases",
        readonly=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ProjectProject, self).create(vals_list)
        for rec in res:
            default_alias_name = self.env['mail.alias']. \
                with_context(alias_model_name='project.task',
                             alias_parent_model_name='project.project').create(
                {'alias_name': rec.alias_name})
            rec.update({
                'alias_name': default_alias_name.alias_name if not rec.alias_name
                else rec.alias_name
            })
        return res
