
from operator import itemgetter

from werkzeug.exceptions import Forbidden, NotFound
from odoo import fields, _
from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request, route
from datetime import datetime
from collections import OrderedDict
from odoo.exceptions import UserError
import pytz
import base64
from odoo.tools import groupby as groupbyelem
from odoo.exceptions import ValidationError


class CustomerPortalDashboard(CustomerPortal):

    @route(['/partner/update'], type='json', auth='user', website=True)
    def update_email(self, **post):
        print("post", post)
        if post.get('email'):
            request.env.user.partner_id.write({
                'secondary_mail': post.get('email'),
            })
            print(request.env.user.partner_id, "partner")
            return True
        else:
            return False

    def _athlete_profile_get_page_view_values(self, athlete, access_token):
        values = {
            'athlete': athlete,
            'page_name': 'athlete_profile',
        }
        return self._get_page_view_values(athlete, access_token, values,
                                          'athlete_dashboard_profile', False)

    def _athlete_calendar_get_page_view_values(self, athlete, access_token):
        values = {
            'athlete': athlete,
            'page_name': 'athlete_calendar',
        }
        return self._get_page_view_values(athlete, access_token, values,
                                          'athlete_dashboard_calendar', False)

    def _athlete_product_get_page_view_values(self, athlete, access_token):
        values = {
            'athlete': athlete,
            'page_name': 'athlete_product',
        }
        return self._get_page_view_values(athlete, access_token, values,
                                          'athlete_dashboard_products', False)

    def _athlete_forms_get_page_view_values(self, athlete, access_token):
        values = {
            'athlete': athlete,
            'page_name': 'athlete_forms',
        }
        return self._get_page_view_values(athlete, access_token, values,
                                          'athlete_dashboard_forms', False)

    def _athlete_documents_get_page_view_values(self, athlete, access_token):
        values = {
            'athlete': athlete,
            'page_name': 'athlete_documents',
        }
        return self._get_page_view_values(athlete, access_token, values,
                                          'athlete_dashboard_documents', False)

    def _athlete_timesheet_get_page_view_values(self, athlete, access_token):
        values = {
            'athlete': athlete,
            'page_name': 'athlete_timesheet',
        }
        return self._get_page_view_values(athlete, access_token, values,
                                          'athlete_dashboard_timesheet', False)

    def _athlete_subscriptions_get_page_view_values(self, athlete, access_token):
        values = {
            'athlete': athlete,
            'page_name': 'athlete_subscriptions',
        }
        return self._get_page_view_values(athlete, access_token, values,
                                          'athlete_dashboard_subscriptions', False)

    def _athlete_parent_get_page_view_values(self, athlete, access_token):
        values = {
            'athlete': athlete,
            'page_name': 'athlete_parent',
        }
        return self._get_page_view_values(athlete, access_token, values,
                                          'athlete_dashboard_parent', False)

    def _coach_profile_get_page_view_values(self, coach, access_token):
        values = {
            'coach': coach,
            'page_name': 'coach_dashboard',
            'coach_profile_page': True
        }
        return self._get_page_view_values(coach, access_token, values,
                                          'my_dashboard_profile', False)

    def _coach_calendar_get_page_view_values(self, coach, access_token):
        values = {
            'coach': coach,
            'page_name': 'coach_dashboard',
            'coach_calendar_page': True
        }
        return self._get_page_view_values(coach, access_token, values,
                                          'my_dashboard_calendar', False)

    def _coach_chat_hub_get_page_view_values(self, coach, access_token):
        values = {
            'coach': coach,
            'page_name': 'coach_dashboard',
            'coach_chathub_page': True
        }
        return self._get_page_view_values(coach, access_token, values,
                                          'my_dashboard_chathub', False)

    def _coach_timesheet_get_page_view_values(self, coach, access_token):
        values = {
            'coach': coach,
            'page_name': 'coach_dashboard',
            'coach_timesheet_page': True
        }
        return self._get_page_view_values(coach, access_token, values,
                                          'my_dashboard_timesheet', False)

    def _coach_athlete_subscriptions_get_page_view_values(self, coach, access_token):
        values = {
            'coach': coach,
            'page_name': 'coach_subscriptions',
            'coach_documents_page': True
        }
        return self._get_page_view_values(coach, access_token, values,
                                          'coach_dashboard_subscriptions', False)

    def _parent_athlete_subscriptions_get_page_view_values(self, parent, access_token):
        values = {
            'parent': parent,
            'page_name': 'parent_athlete_subscriptions',
            'parent_athlete_subscriptions': True
        }
        return self._get_page_view_values(parent, access_token, values,
                                          'parent_dashboard_subscriptions', False)

    def _coach_documents_get_page_view_values(self, coach, access_token):
        values = {
            'coach': coach,
            'page_name': 'coach_dashboard',
            'coach_documents_page': True
        }
        return self._get_page_view_values(coach, access_token, values,
                                          'my_dashboard_documents', False)

    def _parent_profile_get_page_view_values(self, parent, access_token):
        values = {
            'parent': parent,
            'page_name': 'parent_dashboard',
            'parent_profile_page': True
        }
        return self._get_page_view_values(parent, access_token, values,
                                          'parent_dashboard_profile', False)

    def _parent_chat_hub_get_page_view_values(self, parent, access_token):
        values = {
            'parent': parent,
            'page_name': 'parent_dashboard',
            'parent_chathub_page': True
        }
        return self._get_page_view_values(parent, access_token, values,
                                          'my_dashboard_chathub', False)

    def _parent_invoice_get_page_view_values(self, parent, access_token):
        values = {
            'parent': parent,
            'page_name': 'parent_dashboard',
            'parent_invoices_page': True
        }
        return self._get_page_view_values(parent, access_token, values,
                                          'my_dashboard_invoice', False)

    def _parent_athlete_get_page_view_values(self, athlete, access_token):
        values = {
            'athlete': athlete,
            'page_name': 'parent_athlete_dashboard',
            'parent_athlete_dashboard': True
        }
        return self._get_page_view_values(athlete, access_token, values,
                                          'parent_athlete_dashboard', False)

    def _coach_athlete_get_page_view_values(self, athlete, access_token):
        values = {
            'athlete': athlete,
            'page_name': 'coach_athlete_list',
            'coach_athlete': True
        }
        return self._get_page_view_values(athlete, access_token, values,
                                          'coach_athlete_dashboard', False)

    def _parent_athlete_profile_get_page_view_values(self, athlete, access_token):
        values = {
            'athlete': athlete,
            'page_name': 'parent_athlete_dashboard',
            'parent_athlete_profile': True,
        }
        return self._get_page_view_values(athlete, access_token, values,
                                          'parent_athlete_profile', False)

    def _coach_athlete_profile_get_page_view_values(self, athlete, access_token):
        values = {
            'athlete': athlete,
            'page_name': 'coach_athlete_list',
            'coach_athlete': True,
            'coach_athlete_profile': True,
        }
        return self._get_page_view_values(athlete, access_token, values,
                                          'coach_athlete_profile', False)

    def _parent_athlete_calendar_get_page_view_values(self, athlete,
                                                      access_token):
        values = {
            'athlete': athlete,
            'page_name': 'parent_athlete_dashboard',
            'parent_athlete_calendar': True,
        }
        return self._get_page_view_values(athlete, access_token, values,
                                          'parent_athlete_calendar', False)

    def _coach_athlete_calendar_get_page_view_values(self, athlete,
                                                     access_token):
        values = {
            'athlete': athlete,
            'page_name': 'coach_athlete_list',
            'coach_athlete': True,
            'coach_athlete_calendar': True,
        }
        return self._get_page_view_values(athlete, access_token, values,
                                          'coach_athlete_calendar', False)

    def _parent_athlete_product_get_page_view_values(self, athlete,
                                                     access_token):
        values = {
            'athlete': athlete,
            'page_name': 'parent_athlete_dashboard',
            'parent_athlete_product': True,
        }
        return self._get_page_view_values(athlete, access_token, values,
                                          'parent_athlete_product', False)

    def _coach_athlete_product_get_page_view_values(self, athlete,
                                                     access_token):
        values = {
            'athlete': athlete,
            'page_name': 'coach_athlete_list',
            'coach_athlete': True,
            'coach_athlete_product': True,
        }
        return self._get_page_view_values(athlete, access_token, values,
                                          'parent_athlete_product', False)

    def _parent_athlete_forms_get_page_view_values(self, athlete,
                                                     access_token):
        values = {
            'athlete': athlete,
            'page_name': 'parent_athlete_dashboard',
            'parent_athlete_forms': True,
        }
        return self._get_page_view_values(athlete, access_token, values,
                                          'parent_athlete_forms', False)

    def _coach_athlete_forms_get_page_view_values(self, athlete,
                                                     access_token):
        values = {
            'athlete': athlete,
            'page_name': 'coach_athlete_list',
            'coach_athlete': True,
            'coach_athlete_forms': True,
        }
        return self._get_page_view_values(athlete, access_token, values,
                                          'coach_athlete_forms', False)

    def _parent_athlete_document_get_page_view_values(self, athlete,
                                                      access_token):
        values = {
            'athlete': athlete,
            'page_name': 'parent_athlete_dashboard',
            'parent_athlete_document': True,
        }
        return self._get_page_view_values(athlete, access_token, values,
                                          'parent_athlete_document', False)

    def _coach_athlete_document_get_page_view_values(self, athlete,
                                                      access_token):
        values = {
            'athlete': athlete,
            'page_name': 'coach_athlete_list',
            'coach_athlete': True,
            'coach_athlete_document': True,
        }
        return self._get_page_view_values(athlete, access_token, values,
                                          'coach_athlete_document', False)

    def _parent_athlete_diaries_get_page_view_values(self, athlete,
                                                     access_token):
        values = {
            'athlete': athlete,
            'page_name': 'parent_athlete_diaries',
            'parent_athlete_diaries': True,
        }
        return self._get_page_view_values(athlete, access_token, values,
                                          'parent_athlete_diaries', False)
    def _athlete_diaries_get_page_view_values(self, athlete,
                                                     access_token):
        values = {
            'athlete': athlete,
            'page_name': 'athlete_diaries',
            'parent_athlete_diaries': True,
        }
        return self._get_page_view_values(athlete, access_token, values,
                                          'portal_athlete_diaries_dashboard', False)

    def _coach_athlete_diaries_get_page_view_values(self, athlete,
                                                     access_token):
        values = {
            'athlete': athlete,
            'page_name': 'coach_athlete_list',
            'coach_athlete': True,
            'coach_athlete_forms': True,
        }
        return self._get_page_view_values(athlete, access_token, values,
                                          'coach_athlete_diaries', False)

    def _parent_athlete_timesheet_get_page_view_values(self, athlete,
                                                       access_token):
        values = {
            'athlete': athlete,
            'page_name': 'parent_athlete_dashboard',
            'parent_athlete_timesheet': True,
        }
        return self._get_page_view_values(athlete, access_token, values,
                                          'parent_athlete_timesheet', False)

    def _coach_athlete_timesheet_get_page_view_values(self, athlete,
                                                       access_token):
        values = {
            'athlete': athlete,
            'page_name': 'coach_athlete_list',
            'coach_athlete': True,
            'coach_athlete_timesheet': True,
        }
        return self._get_page_view_values(athlete, access_token, values,
                                          'coach_athlete_timesheet', False)

    def _parent_athlete_coach_get_page_view_values(self, athlete, access_token):
        values = {
            'athlete': athlete,
            'page_name': 'parent_athlete_dashboard',
            'parent_athlete_coach': True,
        }
        return self._get_page_view_values(athlete, access_token, values,
                                          'parent_athlete_coach', False)

    @route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        if partner.org_group_selection == 'parents':
            parent = request.env['organisation.parents'].sudo().search(
                [('partner_id', '=', partner.id)])
            athletes = parent.athlete_ids
            values.update({
                'partner': partner,
                'athletes': athletes,
                'page_name': 'athlete_list'
            })
            response = request.render("organisation.portal_athlete_list",
                                      values)
            return response
        if partner.org_group_selection == 'athletes':
            athlete = request.env['organisation.athletes'].sudo().search(
                [('partner_id', '=', partner.id)])
            tasks = athlete.task_ids
            links = request.env['athlete.dashboard.link'].sudo().search([])
            values.update({
                'partner': partner,
                'athlete': athlete,
                'tasks': tasks,
                'links': links,
            })
            params = request.env['ir.config_parameter'].sudo()
            athlete_profile = params.get_param('organisation.athlete_profile')
            athlete_booking = params.get_param('organisation.athlete_booking')
            athlete_calendar = params.get_param('organisation.athlete_calendar')
            athlete_products = params.get_param('organisation.athlete_products')
            athlete_forms = params.get_param('organisation.athlete_forms')
            athlete_documents = params.get_param(
                'organisation.athlete_documents')
            athlete_timesheet = params.get_param(
                'organisation.athlete_timesheet')
            athlete_coaches = params.get_param('organisation.athlete_coaches')
            athlete_invoices = params.get_param('organisation.athlete_invoices')
            athlete_parents = params.get_param('organisation.athlete_parents')
            athlete_chat_hub = params.get_param('organisation.athlete_chat_hub')
            athlete_assignments = params.get_param(
                'organisation.athlete_assignments')
            athlete_attendance = params.get_param(
                'organisation.athlete_attendance')
            mobile = params.get_param('organisation.mobile')
            tablet = params.get_param('organisation.tablet')
            desktop = params.get_param('organisation.desktop')
            values.update({
                'athlete_profile': athlete_profile,
                'athlete_booking': athlete_booking,
                'athlete_calendar': athlete_calendar,
                'athlete_products': athlete_products,
                'athlete_forms': athlete_forms,
                'athlete_documents': athlete_documents,
                'athlete_timesheet': athlete_timesheet,
                'athlete_coaches': athlete_coaches,
                'athlete_invoices': athlete_invoices,
                'athlete_parents': athlete_parents,
                'athlete_chat_hub': athlete_chat_hub,
                'athlete_assignments': athlete_assignments,
                'athlete_attendance': athlete_attendance,
                'mobile': mobile,
                'tablet': tablet,
                'desktop': desktop
            })
            response = request.render(
                "organisation.portal_organisation_dashboard", values)
            return response
        if partner.org_group_selection == 'fans':
            fan = request.env['organisation.fans'].sudo().search(
                [('partner_id', '=', partner.id)])
            links = request.env['fan.dashboard.link'].sudo().search([])
            values.update({
                'links': links,
                'partner': partner,
                'fan': fan,
            })
            params = request.env['ir.config_parameter'].sudo()
            fan_profile = params.get_param('organisation.fan_profile')
            fan_booking = params.get_param('organisation.fan_booking')
            fan_calendar = params.get_param('organisation.fan_calendar')
            mobile = params.get_param('organisation.mobile')
            tablet = params.get_param('organisation.tablet')
            desktop = params.get_param('organisation.desktop')
            values.update({
                'fan_profile': fan_profile,
                'fan_booking': fan_booking,
                'fan_calendar': fan_calendar,
                'mobile': mobile,
                'tablet': tablet,
                'desktop': desktop,
            })
            response = request.render(
                "organisation.portal_fans_dashboard", values)
            return response
        values.update({
            'partner': partner
        })
        return request.render("portal.portal_my_home", values)

    @route(['/my/athletes'], type='http', auth='user', website=True)
    def athletes(self):
        values = {}
        partner = request.env.user.partner_id
        org_group_selection = partner.org_group_selection
        if org_group_selection == 'ex_coaches':
            coach = request.env['organisation.coaches'].sudo().search(
                [('partner_id', '=', partner.id)])
            athletes = coach.athlete_ids
            values.update({
                'partner': partner,
                'athletes': athletes,
                'page_name': 'coach_athlete_list'
            })
            response = request.render("organisation.portal_athlete_list", values)
        elif org_group_selection == 'parents':
            parent = request.env['organisation.parents'].sudo().search(
                [('partner_id', '=', partner.id)])
            athletes = parent.athlete_ids
            values.update({
                'partner': partner,
                'athletes': athletes,
            })
            response = request.render("organisation.portal_athlete_list", values)
        elif org_group_selection == 'athletes':
            athlete = request.env['organisation.athletes'].sudo().search(
                [('partner_id', '=', partner.id)])
            values.update({
                'partner': partner,
                'athletes': athlete,
            })
            response = request.render("organisation.portal_athlete_list", values)
        else:
            response = request.render("organisation.no_access_template", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/athlete-<int:athlete_id>',
            '/athlete-<int:athlete_id>'], type='http', auth='user', website=True)
    def dashboard(self, athlete_id=None, access_token=None, **post):
        athlete = request.env['organisation.athletes'].sudo().search(
            [('id', '=', athlete_id)])
        links = request.env['athlete.dashboard.link'].sudo().search([])
        if not athlete:
            return request.redirect("/my")
        tasks = athlete.task_ids
        partner = request.env.user.partner_id
        if partner.org_group_selection == 'parents':
            parent = request.env['organisation.parents'].sudo().search([
                ('partner_id', '=', partner.id)
            ])
            parent_athletes = parent.athlete_ids
            if athlete.id not in parent_athletes.mapped('id'):
                return Forbidden()
            values = self._parent_athlete_get_page_view_values(athlete,
                                                              access_token)
        elif partner.org_group_selection == 'ex_coaches':
            coach = request.env['organisation.coaches'].sudo().search([
                ('partner_id', '=', partner.id)
            ])
            coach_athletes = coach.athlete_ids
            if athlete.id not in coach_athletes.mapped('id'):
                return Forbidden()
            values = self._coach_athlete_get_page_view_values(athlete,
                                                              access_token)
        else:
            return request.redirect("/my")
        values.update({
            'links': links,
            'partner': partner,
            'tasks': tasks
        })
        params = request.env['ir.config_parameter'].sudo()
        athlete_profile = params.get_param('organisation.athlete_profile')
        athlete_booking = params.get_param('organisation.athlete_booking')
        athlete_calendar = params.get_param('organisation.athlete_calendar')
        athlete_products = params.get_param('organisation.athlete_products')
        athlete_forms = params.get_param('organisation.athlete_forms')
        athlete_documents = params.get_param('organisation.athlete_documents')
        athlete_timesheet = params.get_param('organisation.athlete_timesheet')
        athlete_coaches = params.get_param('organisation.athlete_coaches')
        athlete_invoices = params.get_param('organisation.athlete_invoices')
        athlete_parents = params.get_param('organisation.athlete_parents')
        athlete_chat_hub = params.get_param('organisation.athlete_chat_hub')
        athlete_assignments = params.get_param(
            'organisation.athlete_assignments')
        athlete_attendance = params.get_param(
            'organisation.athlete_attendance')
        mobile = params.get_param('organisation.mobile')
        tablet = params.get_param('organisation.tablet')
        desktop = params.get_param('organisation.desktop')
        values.update({
            'athlete_profile': athlete_profile,
            'athlete_booking': athlete_booking,
            'athlete_calendar': athlete_calendar,
            'athlete_products': athlete_products,
            'athlete_forms': athlete_forms,
            'athlete_documents': athlete_documents,
            'athlete_timesheet': athlete_timesheet,
            'athlete_coaches': athlete_coaches,
            'athlete_invoices': athlete_invoices,
            'athlete_parents': athlete_parents,
            'athlete_chat_hub': athlete_chat_hub,
            'athlete_assignments': athlete_assignments,
            'athlete_attendance': athlete_attendance,
            'mobile': mobile,
            'tablet': tablet,
            'desktop': desktop,
        })
        response = request.render("organisation.portal_organisation_dashboard",
                                  values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/athlete-<int:athlete_id>/profile',
            '/athlete/athlete-<int:athlete_id>/profile',
            '/my/athlete-<int:athlete_id>/profile',
            '/athlete-<int:athlete_id>/profile'], type='http', auth='user',
           website=True)
    def dashboard_profile(self, athlete_id=None, access_token=None, **post):
        athlete = request.env['organisation.athletes'].sudo().search(
            [('id', '=', athlete_id)])
        if not athlete:
            return request.redirect("/my")
        athlete_partner = athlete.partner_id
        partner = request.env.user.partner_id
        if partner.org_group_selection == 'athletes':
            if athlete.partner_id != partner:
                return Forbidden()
            values = self._athlete_profile_get_page_view_values(athlete,
                                                                access_token)
        elif partner.org_group_selection == 'parents':
            parent = request.env['organisation.parents'].sudo().search([
                ('partner_id', '=', partner.id)
            ])
            parent_athletes = parent.athlete_ids
            if athlete.id not in parent_athletes.mapped('id'):
                return Forbidden()
            values = self._parent_athlete_profile_get_page_view_values(
                athlete, access_token)
        elif partner.org_group_selection == 'ex_coaches':
            coach = request.env['organisation.coaches'].sudo().search([
                ('partner_id', '=', partner.id)
            ])
            coach_athletes = coach.athlete_ids
            if athlete.id not in coach_athletes.mapped('id'):
                return Forbidden()
            values = self._coach_athlete_profile_get_page_view_values(
                athlete, access_token)
        else:
            values = {}
        values.update({
            'athlete': athlete,
            'employee': athlete.employee_id,
            'athlete_partner': athlete_partner,
            'vehicle_regs': athlete.vehicle_ids
        })
        response = request.render(
            "organisation.portal_athlete_profile_dashboard", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/athlete-<int:athlete_id>/booking',
            '/athlete/athlete-<int:athlete_id>/booking',
            '/my/athlete-<int:athlete_id>/booking',
            '/athlete-<int:athlete_id>/booking'], type='http',
           auth='user',
           website=True)
    def dashboard_booking(self, athlete_id=None):
        return

    @route(['/my/athlete-<int:athlete_id>/attendance',
            '/athlete/athlete-<int:athlete_id>/attendance',
            '/my/athlete-<int:athlete_id>/attendance',
            '/athlete-<int:athlete_id>/attendance'], type='http',
           auth='user',
           website=True)
    def dashboard_attendance(self, athlete_id=None):
        return

    @route(['/my/athlete-<int:athlete_id>/discipline',
            '/athlete/athlete-<int:athlete_id>/discipline',
            '/my/athlete-<int:athlete_id>/discipline',
            '/athlete-<int:athlete_id>/discipline'], type='http',
           auth='user',
           website=True)
    def dashboard_discipline(self, athlete_id=None):
        athlete = request.env['organisation.athletes'].sudo().search(
            [('id', '=', athlete_id)])
        partner = request.env.user.partner_id
        if not athlete:
            return request.redirect("/my")
        if athlete.partner_id != partner:
            return Forbidden()
        disciplines = athlete.discipline_ids
        values = {}
        values.update({
            'athlete': athlete,
            'disciplines': disciplines
        })
        response = request.render(
            "organisation.portal_athlete_discipline_dashboard", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/athlete-<int:athlete_id>/calendar',
            '/athlete/athlete-<int:athlete_id>/calendar',
            '/my/athlete-<int:athlete_id>/calendar',
            '/athlete-<int:athlete_id>/calendar'], type='http',
           auth='user',
           website=True)
    def dashboard_calendar(self, athlete_id=None, access_token=None, **post):
        athlete = request.env['organisation.athletes'].sudo().search(
            [('id', '=', athlete_id)])
        if not athlete:
            return request.redirect("/my")
        partner = request.env.user.partner_id
        if partner.org_group_selection == 'athletes':
            if athlete.partner_id != partner:
                return Forbidden()
            values = self._athlete_calendar_get_page_view_values(athlete,
                                                                 access_token)
        elif partner.org_group_selection == 'parents':
            parent = request.env['organisation.parents'].sudo().search([
                ('partner_id', '=', partner.id)
            ])
            parent_athletes = parent.athlete_ids
            if athlete.id not in parent_athletes.mapped('id'):
                return Forbidden()
            values = self._parent_athlete_calendar_get_page_view_values(
                athlete, access_token)
        elif partner.org_group_selection == 'ex_coaches':
            coach = request.env['organisation.coaches'].sudo().search([
                ('partner_id', '=', partner.id)
            ])
            coach_athletes = coach.athlete_ids
            if athlete.id not in coach_athletes.mapped('id'):
                return Forbidden()
            values = self._coach_athlete_calendar_get_page_view_values(
                athlete, access_token)
        else:
            values = {}
        events = athlete.event_ids
        length = len(events)
        today = str(fields.Date.today())
        values.update({
            'athlete': athlete,
            'events': events,
            'length': length,
            'today': today
        })
        events_info = []
        for ev in events:
            tz = pytz.timezone((ev.event_tz or ev.env.context.get('tz') or 'UTC'))
            start = pytz.utc.localize(ev.start).astimezone(tz).strftime("%Y-%m-%d %H:%M:%S")
            stop = pytz.utc.localize(ev.stop).astimezone(tz).strftime("%Y-%m-%d %H:%M:%S")
            events_info.append({'title': ev.event_description,
                                'start': start,
                                'end': stop})
        values.update({
            'events_info': events_info,
        })
        response = request.render(
            "organisation.portal_athlete_calendar_dashboard", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/athlete-<int:athlete_id>/assignment',
            '/athlete/athlete-<int:athlete_id>/assignment',
            '/my/athlete-<int:athlete_id>/assignment',
            '/athlete-<int:athlete_id>/assignment'], type='http',
           auth='user',
           website=True)
    def dashboard_assignment(self, athlete_id=None, **post):
        athlete = request.env['organisation.athletes'].sudo().search(
            [('id', '=', athlete_id)])
        partner = request.env.user.partner_id
        if not athlete:
            return request.redirect("/my")
        # if athlete.partner_id != partner:
        #     return Forbidden()
        values = {}
        values.update({
            'athlete': athlete,

        })
        # response = request.render(
        #     "organisation.portal_athlete_assignment_dashboard", values)
        # response.headers['X-Frame-Options'] = 'DENY'
        # return response

    @route(['/my/athlete-<int:athlete_id>/invoice',
            '/athlete/athlete-<int:athlete_id>/invoice',
            '/my/athlete-<int:athlete_id>/invoice',
            '/athlete-<int:athlete_id>/invoice'], type='http',
           auth='user',
           website=True)
    def dashboard_invoice(self, athlete_id=None, access_token=None, **post):
        athlete = request.env['organisation.athletes'].sudo().search(
            [('id', '=', athlete_id)])
        if not athlete:
            return request.redirect("/my")
        partner = request.env.user.partner_id
        if partner.org_group_selection == 'athletes':
            if athlete.partner_id != partner:
                return Forbidden()
            values = self._athlete_product_get_page_view_values(athlete,
                                                                access_token)
        elif partner.org_group_selection == 'parents':
            parent = request.env['organisation.parents'].sudo().search([
                ('partner_id', '=', partner.id)
            ])
            parent_athletes = parent.athlete_ids
            if athlete.id not in parent_athletes.mapped('id'):
                return Forbidden()
            values = self._parent_athlete_product_get_page_view_values(
                athlete, access_token)
        elif partner.org_group_selection == 'ex_coaches':
            coach = request.env['organisation.coaches'].sudo().search([
                ('partner_id', '=', partner.id)
            ])
            coach_athletes = coach.athlete_ids
            if athlete.id not in coach_athletes.mapped('id'):
                return Forbidden()
            values = self._coach_athlete_product_get_page_view_values(
                athlete, access_token)
        else:
            values = {}
        products = athlete.product_ids
        values.update({
            'athlete': athlete,
            'products': products
        })
        response = request.render(
            "organisation.portal_athlete_invoice_dashboard", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route(['/my/athlete-<int:athlete_id>/forms',
                 '/athlete/athlete-<int:athlete_id>/forms',
                 '/my/athlete-<int:athlete_id>/forms',
                 '/athlete-<int:athlete_id>/forms'],
                type='http', auth="user", website=True)
    def dashboard_forms(self, athlete_id=None, access_token=None, **post):
        athlete = request.env['organisation.athletes'].sudo().search(
            [('id', '=', athlete_id)])
        if not athlete:
            return request.redirect("/my")
        partner = request.env.user.partner_id
        if partner.org_group_selection == 'athletes':
            if athlete.partner_id != partner:
                return Forbidden()
            values = self._athlete_forms_get_page_view_values(athlete,
                                                              access_token)
        elif partner.org_group_selection == 'parents':
            parent = request.env['organisation.parents'].sudo().search([
                ('partner_id', '=', partner.id)
            ])
            parent_athletes = parent.athlete_ids
            if athlete.id not in parent_athletes.mapped('id'):
                return Forbidden()
            values = self._parent_athlete_forms_get_page_view_values(
                athlete, access_token)
        elif partner.org_group_selection == 'ex_coaches':
            coach = request.env['organisation.coaches'].sudo().search([
                ('partner_id', '=', partner.id)
            ])
            coach_athletes = coach.athlete_ids
            if athlete.id not in coach_athletes.mapped('id'):
                return Forbidden()
            values = self._coach_athlete_forms_get_page_view_values(
                athlete, access_token)
        else:
            values = {}
        values.update({
            'partner': partner,
            'forms': athlete.form_ids,
            'surveys': athlete.survey_ids
        })
        return request.render("organisation.portal_athlete_form_dashboard",
                              values)

    @http.route(['/my/athlete-<int:athlete_id>/my_subscriptions',
                 '/athlete/athlete-<int:athlete_id>/my_subscriptions',
                 '/my/athlete-<int:athlete_id>/my_subscriptions',
                 '/athlete-<int:athlete_id>/my_subscriptions'],
                type='http', auth="user", website=True)
    def dashboard_subscriptions(self, athlete_id=None, access_token=None, **post):
        athlete = request.env['organisation.athletes'].sudo().search(
            [('id', '=', athlete_id)])
        if not athlete:
            return request.redirect("/my")
        partner = request.env.user.partner_id
        if partner.org_group_selection == 'athletes':
            if athlete.partner_id != partner:
                return Forbidden()
            values = self._athlete_subscriptions_get_page_view_values(athlete,
                                                              access_token)
        elif partner.org_group_selection == 'parents':
            parent = request.env['organisation.parents'].sudo().search([
                ('partner_id', '=', partner.id)
            ])
            parent_athletes = parent.athlete_ids
            if athlete.id not in parent_athletes.mapped('id'):
                return Forbidden()
            values = self._parent_athlete_subscriptions_get_page_view_values(
                athlete, access_token)
        elif partner.org_group_selection == 'ex_coaches':
            coach = request.env['organisation.coaches'].sudo().search([
                ('partner_id', '=', partner.id)
            ])
            coach_athletes = coach.athlete_ids
            if athlete.id not in coach_athletes.mapped('id'):
                return Forbidden()
            values = self._coach_athlete_subscriptions_get_page_view_values(
                athlete, access_token)
        else:
            values = {}
        values.update({
            'partner': partner,
            'subscriptions': athlete.subscription_ids
        })
        return request.render("organisation.portal_athlete_subscription_dashboard",
                              values)

    @http.route(['/my/athlete-<int:athlete_id>/my_diaries',
                 '/athlete/athlete-<int:athlete_id>/my_diaries',
                 '/my/athlete-<int:athlete_id>/my_diaries',
                 '/athlete-<int:athlete_id>/my_diaries'],
                type='http', auth="user", website=True)
    def dashboard_diaries(self, athlete_id=None, access_token=None, **post):
        athlete = request.env['organisation.athletes'].sudo().search(
            [('id', '=', athlete_id)])
        print("athlete", athlete)
        if not athlete:
            return request.redirect("/my")
        partner = request.env.user.partner_id
        if partner.org_group_selection == 'athletes':
            if athlete.partner_id != partner:
                return Forbidden()
            values = self._athlete_diaries_get_page_view_values(athlete,
                                                                access_token)
        elif partner.org_group_selection == 'parents':
            parent = request.env['organisation.parents'].sudo().search([
                ('partner_id', '=', partner.id)
            ])
            parent_athletes = parent.athlete_ids
            if athlete.id not in parent_athletes.mapped('id'):
                return Forbidden()
            values = self._parent_athlete_diaries_get_page_view_values(
                athlete, access_token)
        elif partner.org_group_selection == 'ex_coaches':
            coach = request.env['organisation.coaches'].sudo().search([
                ('partner_id', '=', partner.id)
            ])
            coach_athletes = coach.athlete_ids
            if athlete.id not in coach_athletes.mapped('id'):
                return Forbidden()
            values = self._coach_athlete_diaries_get_page_view_values(
                athlete, access_token)
        else:
            values = {}
        values.update({
            'partner': partner,
            'surveys': request.env['survey.survey'].sudo().search([
                ('is_diary', '=', True)])
        })
        return request.render("organisation.portal_athlete_diaries_dashboard",
                              values)

    @http.route(['/my/athlete-<int:athlete_id>/documents',
                 '/athlete/athlete-<int:athlete_id>/documents',
                 '/my/athlete-<int:athlete_id>/documents',
                 '/athlete-<int:athlete_id>/documents'],
                type='http', auth="user", website=True)
    def dashboard_documents(self, athlete_id=None, access_token=None, **post):
        athlete = request.env['organisation.athletes'].sudo().search(
            [('id', '=', athlete_id)])
        if not athlete:
            return request.redirect("/my")
        partner = request.env.user.partner_id
        if partner.org_group_selection == 'athletes':
            if athlete.partner_id != partner:
                return Forbidden()
            values = self._athlete_documents_get_page_view_values(
                athlete, access_token)
        elif partner.org_group_selection == 'parents':
            parent = request.env['organisation.parents'].sudo().search([
                ('partner_id', '=', partner.id)
            ])
            parent_athletes = parent.athlete_ids
            if athlete.id not in parent_athletes.mapped('id'):
                return Forbidden()
            values = self._parent_athlete_document_get_page_view_values(
                athlete, access_token)
        elif partner.org_group_selection == 'ex_coaches':
            coach = request.env['organisation.coaches'].sudo().search([
                ('partner_id', '=', partner.id)
            ])
            coach_athletes = coach.athlete_ids
            if athlete.id not in coach_athletes.mapped('id'):
                return Forbidden()
            values = self._coach_athlete_document_get_page_view_values(
                athlete, access_token)
        else:
            values = {}
        document = athlete.document_ids
        values.update({
            'documents': document,
            'athlete': athlete,
            'partner': partner,
        })
        return request.render(
            "organisation.portal_athlete_document_dashboard", values)

    @route(['/my/athlete-<int:athlete_id>/timesheet',
            '/athlete/athlete-<int:athlete_id>/timesheet',
            '/my/athlete-<int:athlete_id>/timesheet',
            '/athlete-<int:athlete_id>/timesheet'], type='http',
           auth='user',
           website=True)
    def dashboard_timesheet(self, athlete_id=None, access_token=None):
        athlete = request.env['organisation.athletes'].sudo().search(
            [('id', '=', athlete_id)])
        partner = request.env.user.partner_id
        if partner.org_group_selection == 'athletes':
            if athlete.partner_id != partner:
                return Forbidden()
            values = self._athlete_timesheet_get_page_view_values(
                athlete, access_token)
        elif partner.org_group_selection == 'parents':
            parent = request.env['organisation.parents'].sudo().search([
                ('partner_id', '=', partner.id)
            ])
            parent_athletes = parent.athlete_ids
            if athlete.id not in parent_athletes.mapped('id'):
                return Forbidden()
            values = self._parent_athlete_timesheet_get_page_view_values(
                athlete, access_token)
        elif partner.org_group_selection == 'ex_coaches':
            coach = request.env['organisation.coaches'].sudo().search([
                ('partner_id', '=', partner.id)
            ])
            coach_athletes = coach.athlete_ids
            if athlete.id not in coach_athletes.mapped('id'):
                return Forbidden()
            values = self._coach_athlete_timesheet_get_page_view_values(
                athlete, access_token)
        else:
            values = {}
        tasks = athlete.task_ids
        values.update({
            'athlete': athlete,
            'tasks': tasks,
            'partner': partner
        })
        response = request.render(
            "organisation.portal_athlete_timesheet_dashboard", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/athlete-<int:athlete_id>/chat_hub'], type='http',
           auth='user',
           website=True)
    def dashboard_athlete_chat_hub(self, athlete_id=None):
        athlete = request.env['organisation.athletes'].sudo().search(
            [('id', '=', athlete_id)])
        partner = request.env.user.partner_id
        channels = request.env['chat.hub'].sudo().search(
            [('partner_ids', 'in', partner.id)])
        values = {}
        values.update({
            'channels': channels,
        })
        response = request.render(
            "organisation.portal_athlete_chat_hub", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/athlete-<int:athlete_id>/coach',
            '/athlete/athlete-<int:athlete_id>/coach'], type='http',
           auth='user',
           website=True)
    def dashboard_coach(self, athlete_id=None, access_token=None):
        athlete = request.env['organisation.athletes'].sudo().search(
            [('id', '=', athlete_id)])
        partner = request.env.user.partner_id
        if partner.org_group_selection == 'parents':
            parent = request.env['organisation.parents'].sudo().search([
                ('partner_id', '=', partner.id)
            ])
            parent_athletes = parent.athlete_ids
            if athlete.id not in parent_athletes.mapped('id'):
                return Forbidden()
            values = self._parent_athlete_coach_get_page_view_values(
                athlete, access_token)
        else:
            values = {}
        coaches = athlete.coach_ids
        values.update({
            'athlete': athlete,
            'coaches': coaches
        })
        response = request.render(
            "organisation.portal_athlete_coach_dashboard", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/athlete-<int:athlete_id>/parent',
            '/athlete-<int:athlete_id>/parent'], type='http',
           auth='user',
           website=True)
    def dashboard_parent(self, athlete_id=None, access_token=None):
        athlete = request.env['organisation.athletes'].sudo().search(
            [('id', '=', athlete_id)])
        partner = request.env.user.partner_id
        if partner.org_group_selection == 'athletes':
            if athlete.partner_id != partner:
                return Forbidden()
            values = self._athlete_parent_get_page_view_values(
                athlete, access_token)
        else:
            values = {}
        parents = athlete.parent_ids
        values.update({
            'athlete': athlete,
            'parents': parents,
        })
        response = request.render(
            "organisation.portal_athlete_parent_dashboard", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/my_timesheet'], type='http',
           auth='user',
           website=True)
    def dashboard_coach_timesheet(self, access_token=None):
        partner = request.env.user.partner_id
        coach = request.env['organisation.coaches'].sudo().search(
            [('partner_id', '=', partner.id)])
        values = self._coach_timesheet_get_page_view_values(coach, access_token)
        tasks = coach.task_ids
        values.update({
            'coach': coach,
            'tasks': tasks,
        })
        response = request.render(
            "organisation.portal_coach_timesheet_dashboard", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/task_id=<int:task_id>'], type='http',
           auth='user',
           website=True)
    def dashboard_coach_task(self, task_id=None):
        partner = request.env.user.partner_id
        task = request.env['project.task'].sudo().search(
            [('id', '=', task_id)])
        coach = request.env['organisation.coaches'].sudo().search(
            [('partner_id', '=', partner.id)])
        checklists = task.checklist_ids
        values = {}
        values.update({
            'coach': coach,
            'task': task,
            'checklists': checklists,
        })
        response = request.render(
            "organisation.portal_coach_task_dashboard", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/start_task'], type='json', auth='user', website=True)
    def start_task(self, **post):
        task = request.env['project.task'].sudo().search(
            [('id', '=', post['task_id'])])
        coach = request.env['organisation.coaches'].sudo().search(
            [('partner_id', '=', request.env.user.partner_id.id)])
        if request.env.user.task_id:
            raise UserError("You can not start 2 tasks at same time !")

        task.sudo().start_time = datetime.now()
        # add entry in line

        vals = {'name': '/', 'date': datetime.now()}

        if task:
            vals.update({'start_date': datetime.now()})
            vals.update({'task_id': task.id})

            if task.project_id:
                vals.update({'project_id': task.project_id.id})
                act_id = request.env['project.project'].sudo().browse(
                    task.project_id.id).analytic_account_id

                if act_id:
                    vals.update({'account_id': act_id.id})

        if coach:
            emp_search = coach.employee_id

            if emp_search:
                vals.update({'employee_id': emp_search.id})

        timesheet = request.env['account.analytic.line'].sudo().create(vals)
        request.env.user.write({'task_id': task.id, 'start_time': datetime.now()})
        task.write({
            'task_running': True,
            'task_runner': request.env.user.name,
            'task_runner_ids': [(4, request.env.user.id)]
        })
        task.sudo()._cr.commit()

    @route(['/end_task'], type='json', auth='user', website=True)
    def end_task(self, **post):
        task = request.env['project.task'].sudo().search(
            [('id', '=', post['task_id'])])
        coach = request.env['organisation.coaches'].sudo().search(
            [('partner_id', '=', request.env.user.partner_id.id)])
        usr_id = request.env.user
        if usr_id and usr_id.task_id:
            task.sudo().end_time = datetime.now()
            task.sudo().start_time = request.env.user.start_time
            if task.id != request.env.user.task_id.id:
                raise UserError("You cannot End this task !")

            tot_sec = (task.end_time - request.env.user.start_time).total_seconds()
            tot_hours = round((tot_sec / 3600.0), 2)

            task.sudo().total_time = tot_hours

            vals = {
                'name': task.name,
                'unit_amount': task.total_time,
                'amount': task.total_time,
                'date': datetime.now()
            }

            if task and request.env.user and request.env.user.task_id:
                task_search = request.env['project.task'].sudo().search(
                    [('id', '=', task.id)], limit=1)

                if task_search:
                    vals.update({'start_date': request.env.user.start_time})
                    vals.update({'end_date': datetime.now()})
                    vals.update({'task_id': task_search.id})

                    if task_search.project_id:
                        vals.update({'project_id': task_search.project_id.id})
                        act_id = request.env['project.project'].sudo().browse(
                            task_search.project_id.id).analytic_account_id

                        if act_id:
                            vals.update({'account_id': act_id.id})

                    task_search.sudo().write({
                        'start_time':
                            None,
                        'task_running':
                            False,
                        'task_runner_ids': [(3, request.env.user.id)]
                    })

                    timesheet_line = request.env['account.analytic.line'].sudo().search(
                        [('task_id', '=', task_search.id),
                         ('employee_id', '=', coach.employee_id.id),
                         ('end_date', '=', False)],
                        limit=1)
                    if timesheet_line:
                        timesheet_line.write(vals)
                    task.sudo()._cr.commit()
                    request.env.user.write({'task_id': False, 'start_time': None})

    @route(['/my/edit_athlete'], type='http', auth='user', website=True)
    def edit_athlete(self, **post):
        values = {}
        athlete = request.env['organisation.athletes'].sudo().search(
            [('id', '=', post['athlete_id'])])
        partner = athlete.partner_id
        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        values.update({
            'error': {},
            'error_message': [],
        })
        values.update({
            'partner': partner,
            'athlete': athlete,
            'countries': countries,
            'states': states,
            'date': fields.Date.today()
        })
        response = request.render(
            "organisation.athlete_edit_form_template", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/edit_parent'], type='http', auth='user', website=True)
    def edit_parent(self, **post):
        values = {}
        parent = request.env['organisation.parents'].sudo().search(
            [('id', '=', post['parent_id'])])
        partner = parent.partner_id
        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        values.update({
            'partner': partner,
            'parent': parent,
            'countries': countries,
            'states': states,
            'date': fields.Date.today()
        })
        response = request.render(
            "organisation.parent_edit_form_template", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/edit_coach'], type='http', auth='user', website=True)
    def edit_coach(self, **post):
        values = {}
        coach = request.env['organisation.coaches'].sudo().search(
            [('id', '=', post['coach_id'])])
        partner = coach.partner_id
        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        values.update({
            'partner': partner,
            'coach': coach,
            'countries': countries,
            'states': states,
            'date': fields.Date.today()
        })
        response = request.render(
            "organisation.coach_edit_form_template", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/edit_fan'], type='http', auth='user', website=True)
    def edit_fan(self, **post):
        values = {}
        fan = request.env['organisation.fans'].sudo().search(
            [('id', '=', post['fan_id'])])
        partner = fan.partner_id
        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        values.update({
            'partner': partner,
            'fan': fan,
            'countries': countries,
            'states': states,
            'date': fields.Date.today()
        })
        response = request.render(
            "organisation.fan_edit_form_template", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/submit_details'], type='http', auth='user', website=True)
    def submit_details(self, **post):
        post.get('photo')
        athlete = request.env['organisation.athletes'].sudo().search(
            [('id', '=', post['athlete_id'])])
        partner = athlete.partner_id
        employee = athlete.employee_id
        partner.write({
            'name': post['name'],
            'email': post['email'],
            'phone': post['phone'],
            'member_id': post['member_id'],
            'street': post['street'],
            'city': post['city'],
            'zip': post['zipcode'],
            'athlete_id': athlete.id,
            'dob': post['dob']
        })
        employee.write({
            'member_id': post['member_id'],
        })
        athlete.write({
            'member_id': post['member_id'],
        })
        if post['photo']:
            partner.write({
                'image_1920': base64.b64encode(post.get('photo').read()),
            })
            employee.write({
                'image_1920': base64.b64encode(post.get('photo').read()),
            })
        if post['country_id']:
            partner.write({
                'country_id': int(post['country_id']),
            })
        if post['state_id']:
            partner.write({
                'state_id': int(post['state_id']),
            })
        athlete.write({
            'dob': post['dob']
        })
        if partner.org_group_selection == 'athletes':
            return request.redirect("/my/athlete-%s/profile" % athlete.id)
        elif partner.org_group_selection == 'ex_coaches':
            return request.redirect("/my/athlete-%s/profile" % athlete.id)
        elif partner.org_group_selection == 'parents':
            return request.redirect("/my/athlete-%s/profile" % athlete.id)
        else:
            return request.redirect("/my")

    @route(['/my/submit_parent'], type='http', auth='user', website=True)
    def submit_parent(self, **post):
        parent = request.env['organisation.parents'].sudo().search(
            [('id', '=', post['parent_id'])])
        partner = parent.partner_id
        partner.write({
            'name': post['name'],
            'email': post['email'],
            'phone': post['phone'],
            'street': post['street'],
            'city': post['city'],
            'zip': post['zipcode'],
            # 'country_id': int(post['country_id']),
            # 'state_id': int(post['state_id']),
        })
        if 'country_id' in post:
            if post['country_id']:
                partner.write({
                    'country_id': int(post['country_id']),
                })
            else:
                partner.write({
                    'country_id': False,
                })
        if 'state_id' in post:
            if post['state_id']:
                partner.write({
                    'state_id': int(post['state_id']),
                })
            else:
                partner.write({
                    'state_id': False,
                })
        return request.redirect("/my/parent_profile/%s" % parent.id)

    @route(['/my/submit_coach'], type='http', auth='user', website=True)
    def submit_coach(self, **post):
        coach = request.env['organisation.coaches'].sudo().search(
            [('id', '=', post['coach_id'])])
        partner = coach.partner_id
        partner.write({
            'name': post['name'],
            'email': post['email'],
            'phone': post['phone'],
            'street': post['street'],
            'city': post['city'],
            'zip': post['zipcode'],
            # 'country_id': int(post['country_id']),
            # 'state_id': int(post['state_id']),
        })
        if post['country_id']:
            partner.write({
                'country_id': int(post['country_id']),
                # 'state_id': int(post['state_id']),
            })
        if post['state_id']:
            partner.write({
                # 'country_id': int(post['country_id']),
                'state_id': int(post['state_id']),
            })
        return request.redirect("/my/profile-%s" % coach.id)

    @route(['/my/submit_fan'], type='http', auth='user', website=True)
    def submit_fan(self, **post):
        fan = request.env['organisation.fans'].sudo().search(
            [('id', '=', post['fan_id'])])
        partner = fan.partner_id
        partner.write({
            'name': post['name'],
            'email': post['email'],
            'phone': post['phone'],
            'street': post['street'],
            'city': post['city'],
            'zip': post['zipcode'],
            # 'country_id': int(post['country_id']),
            # 'state_id': int(post['state_id']),
        })
        if post['country_id']:
            partner.write({
                'country_id': int(post['country_id']),
                # 'state_id': int(post['state_id']),
            })
        if post['state_id']:
            partner.write({
                # 'country_id': int(post['country_id']),
                'state_id': int(post['state_id']),
            })
        return request.redirect("/my/fan_profile/%s" % fan.id)

    @route(['/athlete/task/manage'], type='http',
           auth='user',
           website=True)
    def dashboard_athlete_task(self, **post):
        partner = request.env.user.partner_id
        task = request.env['project.task'].sudo().search(
            [('id', '=', post['task_id'])])
        athlete = request.env['organisation.coaches'].sudo().search(
            [('partner_id', '=', partner.id)])
        values = {}
        values.update({
            'athlete': athlete,
            'task': task,
        })
        response = request.render(
            "organisation.portal_athlete_task_dashboard", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/start_athlete_task'], type='json', auth='user', website=True)
    def start_athlete_task(self, **post):
        task = request.env['project.task'].sudo().search(
            [('id', '=', post['task_id'])])
        athlete = request.env['organisation.athletes'].sudo().search(
            [('partner_id', '=', request.env.user.partner_id.id)])
        if request.env.user.task_id:
            raise UserError("You can not start 2 tasks at same time !")

        task.sudo().start_time = datetime.now()
        # add entry in line

        vals = {'name': '/', 'date': datetime.now()}

        if task:
            vals.update({'start_date': datetime.now()})
            vals.update({'task_id': task.id})

            if task.project_id:
                vals.update({'project_id': task.project_id.id})
                act_id = request.env['project.project'].sudo().browse(
                    task.project_id.id).analytic_account_id

                if act_id:
                    vals.update({'account_id': act_id.id})

        if athlete:
            emp_search = athlete.employee_id

            if emp_search:
                vals.update({'employee_id': emp_search.id})

        timesheet = request.env['account.analytic.line'].sudo().create(vals)
        request.env.user.write({'task_id': task.id, 'start_time': datetime.now()})
        task.write({
            'task_running': True,
            'task_runner': request.env.user.name,
            'task_runner_ids': [(4, request.env.user.id)]
        })
        task.sudo()._cr.commit()

    @route(['/end_athlete_task'], type='json', auth='user', website=True)
    def end_athlete_task(self, **post):
        task = request.env['project.task'].sudo().search(
            [('id', '=', post['task_id'])])
        athlete = request.env['organisation.athletes'].sudo().search(
            [('partner_id', '=', request.env.user.partner_id.id)])
        usr_id = request.env.user
        if usr_id and usr_id.task_id:
            task.sudo().end_time = datetime.now()
            task.sudo().start_time = request.env.user.start_time
            if task.id != request.env.user.task_id.id:
                raise UserError("You cannot End this task !")

            tot_sec = (task.end_time - request.env.user.start_time).total_seconds()
            tot_hours = round((tot_sec / 3600.0), 2)

            task.sudo().total_time = tot_hours

            vals = {
                'name': task.name,
                'unit_amount': task.total_time,
                'amount': task.total_time,
                'date': datetime.now()
            }

            if task and request.env.user and request.env.user.task_id:
                task_search = request.env['project.task'].sudo().search(
                    [('id', '=', task.id)], limit=1)

                if task_search:
                    vals.update({'start_date': request.env.user.start_time})
                    vals.update({'end_date': datetime.now()})
                    vals.update({'task_id': task_search.id})

                    if task_search.project_id:
                        vals.update({'project_id': task_search.project_id.id})
                        act_id = request.env['project.project'].sudo().browse(
                            task_search.project_id.id).analytic_account_id

                        if act_id:
                            vals.update({'account_id': act_id.id})

                    task_search.sudo().write({
                        'start_time':
                            None,
                        'task_running':
                            False,
                        'task_runner_ids': [(3, request.env.user.id)]
                    })

                    timesheet_line = request.env['account.analytic.line'].sudo().search(
                        [('task_id', '=', task_search.id),
                         ('employee_id', '=', athlete.employee_id.id),
                         ('end_date', '=', False)],
                        limit=1)
                    if timesheet_line:
                        timesheet_line.write(vals)
                    task.sudo()._cr.commit()
                    request.env.user.write({'task_id': False, 'start_time': None})

    @route(['/my/athlete-<int:athlete_id>/invoices',
            '/athlete/athlete-=<int:athlete_id>/invoices'],
           type='http', auth='user', website=True)
    def portal_athlete_invoices(self, athlete_id=None, page=1, date_begin=None,
                                date_end=None, sortby=None, filterby=None):
        athlete = request.env['organisation.athletes'].sudo().search([
            ('id', '=', athlete_id)
        ])
        partner = athlete.partner_id
        domain = [('move_type', 'in',
                  ('out_invoice', 'out_refund', 'in_invoice', 'in_refund',
                   'out_receipt', 'in_receipt')),
                  ('partner_id', '=', partner.id)]
        values = self._prepare_portal_layout_values()

        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'invoice_date desc'},
            'duedate': {'label': _('Due Date'),
                        'order': 'invoice_date_due desc'},
            'name': {'label': _('Reference'), 'order': 'name desc'},
            'state': {'label': _('Status'), 'order': 'state'},
        }
        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']


        if date_begin and date_end:
            domain += [('create_date', '>', date_begin),
                       ('create_date', '<=', date_end)]

        # count for pager
        invoice_count = request.env['account.move'].sudo().search_count(domain)
        # invoice_count = len(athlete.invoice_ids)
        # pager
        pager = portal_pager(
            url="/my/invoices",
            url_args={'date_begin': date_begin, 'date_end': date_end,
                      'sortby': sortby},
            total=invoice_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        invoices = request.env['account.move'].sudo().search(domain, order=order,
                                         limit=self._items_per_page,
                                         offset=pager['offset'])
        # obj_invoices = athlete.invoice_ids
        # invoices = obj_invoices.search([], order=order, limit=self._items_per_page, offset=pager['offset'])

        request.session['my_invoices_history'] = invoices.ids[:100]

        values.update({
            'date': date_begin,
            'invoices': invoices,
            'page_name': 'invoice',
            'pager': pager,
            'default_url': '/my/invoices',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            # 'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("account.portal_my_invoices", values)


    @route(['/my/my_invoices', '/my_invoices', '/my/athlete/my_invoices',
            '/athlete/my_invoices'],
           type='http', auth='user', website=True)
    def portal_invoices(self, page=1, date_begin=None, date_end=None,
                        sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        AccountInvoice = request.env['account.move']
        domain = self._get_invoices_domain()
        partner = request.env.user.partner_id

        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'invoice_date desc'},
            'duedate': {'label': _('Due Date'), 'order': 'invoice_date_due desc'},
            'name': {'label': _('Reference'), 'order': 'name desc'},
            'state': {'label': _('Status'), 'order': 'state'},
        }
        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'invoices': {'label': _('Invoices'), 'domain': [('move_type', '=', ('out_invoice', 'out_refund'))]},
            'bills': {'label': _('Bills'), 'domain': [('move_type', '=', ('in_invoice', 'in_refund'))]},
        }
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        invoice_count = AccountInvoice.search_count(domain)
        # invoice_count = len(athlete.invoice_ids)
        # pager
        pager = portal_pager(
            url="/my/invoices",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=invoice_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        invoices = AccountInvoice.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        # obj_invoices = athlete.invoice_ids
        # invoices = obj_invoices.search([], order=order, limit=self._items_per_page, offset=pager['offset'])

        request.session['my_invoices_history'] = invoices.ids[:100]

        values.update({
            'date': date_begin,
            'invoices': invoices,
            'page_name': 'invoice',
            'pager': pager,
            'default_url': '/my/invoices',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        if partner.org_group_selection == 'parents':
            values.update({
                'parents': True
            })
        return request.render("account.portal_my_invoices", values)

    @route(['/my/parent/invoices'],
           type='http', auth='user', website=True)
    def portal_parent_invoices(self, page=1, date_begin=None, date_end=None,
                        sortby=None, filterby=None, groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        parent = request.env['organisation.parents'].sudo().search(
            [('partner_id', '=', partner.id)])
        if not parent:
            request.redirect('/my/home')
        athletes = parent.athlete_ids
        athlete_partners = athletes.partner_id
        partner_ids = []
        partner_ids.append(partner.id)
        for athlete_partner in athlete_partners:
            partner_ids.append(athlete_partner.id)
        domain = [('move_type', 'in', (
            'out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt',
            'in_receipt')), ('partner_id', 'in', partner_ids)]

        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'invoice_date desc'},
            'duedate': {'label': _('Due Date'),
                        'order': 'invoice_date_due desc'},
            'name': {'label': _('Reference'), 'order': 'name desc'},
            'state': {'label': _('Status'), 'order': 'state'},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'partner_id': {'input': 'partner_id', 'label': _('Athlete')},
            'state': {'input': 'state', 'label': _('Stage')},
        }
        # default sort by order
        if not sortby:
            sortby = 'date'
        if not groupby:
            groupby = 'partner_id'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'invoices': {'label': _('Invoices'), 'domain': [
                ('move_type', '=', ('out_invoice', 'out_refund'))]},
            'bills': {'label': _('Bills'), 'domain': [
                ('move_type', '=', ('in_invoice', 'in_refund'))]},
        }
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin),
                       ('create_date', '<=', date_end)]

        # count for pager
        invoice_count = request.env['account.move'].sudo().search_count(domain)
        # invoice_count = len(athlete.invoice_ids)
        # pager
        pager = portal_pager(
            url="/my/invoices",
            url_args={'date_begin': date_begin, 'date_end': date_end,
                      'sortby': sortby, 'groupby': groupby},
            total=invoice_count,
            page=page,
            step=self._items_per_page
        )
        if groupby == 'partner_id':
            order = "partner_id, %s" % order
        elif groupby == 'state':
            order = "state, %s" % order
        # content according to pager and archive selected
        invoices = request.env['account.move'].sudo().search(
            domain, order=order, limit=self._items_per_page,
            offset=pager['offset'])
        # obj_invoices = athlete.invoice_ids
        # invoices = obj_invoices.search([], order=order, limit=self._items_per_page, offset=pager['offset'])

        request.session['my_invoices_history'] = invoices.ids[:100]

        if groupby == 'partner_id':
            grouped_inv = [request.env['account.move'].sudo().concat(*g)
                           for k, g in
                           groupbyelem(invoices, itemgetter('partner_id'))]
        elif groupby == 'state':
            grouped_inv = [request.env['account.move'].sudo().concat(*g)
                           for k, g in groupbyelem(invoices, itemgetter('state'))]
        else:
            grouped_inv = [invoices]

        values.update({
            'date': date_begin,
            'grouped_invoices': grouped_inv,
            'invoices': invoices,
            'page_name': 'invoice',
            'pager': pager,
            'default_url': '/my/parent/invoices',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'groupby': groupby,
            'filterby': filterby,
        })
        if partner.org_group_selection == 'parents':
            values.update({
                'parents': True
            })
        return request.render("organisation.portal_parent_invoices", values)

    @route(['/checklist/complete'], type='http',
           auth='user',
           website=True)
    def checklist_complete(self, **post):
        checklist = request.env['task.checklist'].sudo().search(
            [('id', '=', post['checklist_id'])])
        task = request.env['project.task'].sudo().search(
            [('id', '=', post['task_id'])])
        coach = request.env['organisation.coaches'].sudo().search(
            [('id', '=', post['coach_id'])])
        checklists = task.checklist_ids
        values = {}
        checklist.write({'state': 'completed'})
        values.update({
            'coach': coach,
            'task': task,
            'checklists': checklists,
        })
        response = request.render(
            "organisation.portal_coach_task_dashboard", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/dashboard'], type='http', auth='user', website=True)
    def my_dashboard(self, **post):
        partner = request.env.user.partner_id
        coach = request.env['organisation.coaches'].sudo().search([
            ('partner_id', '=', partner.id)])
        links = request.env['coach.dashboard.link'].sudo().search([])
        values = {}
        values.update({
            'coach': coach,
            'links': links,
            'page_name': 'coach_dashboard'
        })
        params = request.env['ir.config_parameter'].sudo()
        coach_profile = params.get_param('organisation.coach_profile')
        coach_booking = params.get_param('organisation.coach_booking')
        coach_calendar = params.get_param('organisation.coach_calendar')
        coach_assignments = params.get_param(
            'organisation.coach_assignments')
        coach_forms = params.get_param('organisation.coach_forms')
        coach_chat_hub = params.get_param('organisation.coach_chat_hub')
        coach_timesheet = params.get_param('organisation.coach_timesheet')
        coach_invoice = params.get_param('organisation.coach_invoice')
        coach_attendance = params.get_param('organisation.coach_attendance')
        mobile = params.get_param('organisation.mobile')
        tablet = params.get_param('organisation.tablet')
        desktop = params.get_param('organisation.desktop')
        values.update({
            'coach_profile': coach_profile,
            'coach_booking': coach_booking,
            'coach_calendar': coach_calendar,
            'coach_assignments': coach_assignments,
            'coach_forms': coach_forms,
            'coach_chat_hub': coach_chat_hub,
            'coach_timesheet': coach_timesheet,
            'coach_invoice': coach_invoice,
            'coach_attendance': coach_attendance,
            'mobile': mobile,
            'tablet': tablet,
            'desktop': desktop,
        })
        response = request.render(
            "organisation.portal_coach_dashboard", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/my_chat_hub'], type='http',
           auth='user',
           website=True)
    def dashboard_chat_hub(self, access_token=None):
        partner = request.env.user.partner_id
        if partner.org_group_selection == 'ex_coaches':
            coach = request.env['organisation.coaches'].sudo().search(
             [('partner_id', '=', partner.id)])
            values = self._coach_chat_hub_get_page_view_values(
                coach, access_token)
        elif partner.org_group_selection == 'parents':
            parent = request.env['organisation.parents'].sudo().search(
             [('partner_id', '=', partner.id)])
            values = self._parent_chat_hub_get_page_view_values(
                parent, access_token)
        else:
            values = {}
        channels = request.env['chat.hub'].sudo().search(
            [('partner_ids', 'in', partner.id)])
        values.update({
            'channels': channels,
            'is_account': True,
            'total': len(channels)
        })
        response = request.render(
            "organisation.portal_athlete_chat_hub", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/channel_id=<int:channel_id>'], type='http',
           auth='user',
           website=True)
    def chat_hub_channel(self, channel_id=None):
        channel = request.env['chat.hub'].sudo().search(
            [('id', '=', channel_id)])
        values = {}
        values.update({
            'channel': channel,
            'is_account': True,
        })
        response = request.render(
            "organisation.portal_chat_hub_channel", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/booking-<int:coach_id>'], type='http', auth='user',
           website=True)
    def coach_booking(self, coach_id=None):
        return

    @route(['/my/profile-<int:coach_id>'], type='http', auth='user',
           website=True)
    def coach_dashboard_profile(self, coach_id=None, access_token=None):
        coach = request.env['organisation.coaches'].sudo().search(
            [('id', '=', coach_id)])
        partner = request.env.user.partner_id
        partner_coach = request.env['organisation.coaches'].sudo().search(
            [('partner_id', '=', partner.id)])
        if partner_coach.id not in coach.mapped('id'):
            return Forbidden()
        values = self._coach_profile_get_page_view_values(coach, access_token)
        response = request.render(
            "organisation.portal_coach_profile_dashboard", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/documents-<int:coach_id>'], type='http', auth='user',
           website=True)
    def coach_documents(self, coach_id=None, access_token=None):
        partner = request.env.user.partner_id
        coach = request.env['organisation.coaches'].sudo().search(
            [('id', '=', coach_id)])
        partner = request.env.user.partner_id
        partner_coach = request.env['organisation.coaches'].sudo().search(
            [('partner_id', '=', partner.id)])
        if partner_coach.id not in coach.mapped('id'):
            return Forbidden()
        # values = self._coach_profile_get_page_view_values(coach, access_token)
        documents = coach.document_ids
        values = self._coach_documents_get_page_view_values(coach, access_token)
        values.update({
            'coach': coach,
            'partner': partner,
            'documents': documents
        })
        response = request.render(
            "organisation.portal_coach_document_dashboard", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/calendar-<int:coach_id>'], type='http',
           auth='user',
           website=True)
    def coach_calendar(self, coach_id=None, access_token=None):
        coach = request.env['organisation.coaches'].sudo().search(
            [('id', '=', coach_id)])
        # print(coach)
        # print(coach_id)
        partner = request.env.user.partner_id
        # print(partner)
        partner_coach = request.env['organisation.coaches'].sudo().search(
            [('partner_id', '=', partner.id)])

        # print(request.env.user.partner_id.id)
        if request.env.user.partner_id.id != coach_id:
            return Forbidden()
        values = self._coach_calendar_get_page_view_values(coach, access_token)
        # print('values', values)
        events = request.env['calendar.event'].search(
                [('partner_ids', 'in', partner.ids)])
        # print("events", events)
        length = len(events)
        # print("length", length)
        today = str(fields.Date.today())
        values.update({
            'coach': coach,
            'events': events,
            'length': length,
            'today': today
        })
        events_info = []
        for ev in events:
            title = ev.event_description.splitlines()[0].split(
                ': ')[1].replace('/', ' ')
            print(title)
            tz = pytz.timezone(
                (ev.event_tz or ev.env.context.get('tz') or 'UTC'))
            start = pytz.utc.localize(ev.start).astimezone(tz).strftime(
                "%Y-%m-%d %H:%M:%S")
            stop = pytz.utc.localize(ev.stop).astimezone(tz).strftime(
                "%Y-%m-%d %H:%M:%S")
            events_info.append({'title': title,
                                'start': start,
                                'end': stop})
        values.update({
            'events_info': events_info,
            'is_account': True,
        })
        # print('vaaals', values)
        response = request.render(
            "organisation.portal_coach_calendar_dashboard", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/discipline-<int:coach_id>'], type='http',
           auth='user',
           website=True)
    def coach_discipline(self, coach_id=None):
        coach = request.env['organisation.coaches'].sudo().search(
            [('id', '=', coach_id)])
        disciplines = coach.discipline_ids
        values = {}
        values.update({
            'coach': coach,
            'disciplines': disciplines
        })
        response = request.render(
            "organisation.portal_coach_discipline_dashboard", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/parent_dashboard'], type='http',
           auth='user',
           website=True)
    def parent_dashboard(self):
        print("haiiii")
        partner = request.env.user.partner_id
        parent = request.env['organisation.parents'].sudo().search(
            [('partner_id', '=', partner.id)])
        print('parent', parent)
        links = request.env['parent.dashboard.link'].sudo().search([])
        print('links', links)
        if parent:
            values = {}
            values.update({
                'links': links,
                'parent': parent,
                'page_name': 'parent_dashboard'
            })
            params = request.env['ir.config_parameter'].sudo()
            parent_profile = params.get_param('organisation.parent_profile')
            parent_invoices = params.get_param('organisation.parent_invoices')
            parent_chat_hub = params.get_param('organisation.parent_chat_hub')
            parent_attendance = params.get_param(
                'organisation.parent_attendance')
            mobile = params.get_param('organisation.mobile')
            tablet = params.get_param('organisation.tablet')
            desktop = params.get_param('organisation.desktop')
            values.update({
                'parent_profile': parent_profile,
                'parent_invoices': parent_invoices,
                'parent_chat_hub': parent_chat_hub,
                'parent_attendance': parent_attendance,
                'mobile': mobile,
                'tablet': tablet,
                'desktop': desktop,
            })
            response = request.render(
                "organisation.portal_parent_dashboard", values)
        else:
            response = request.render("organisation.no_access_template")
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/parent_profile/<int:parent_id>'], type='http', auth='user',
           website=True)
    def parent_dashboard_profile(self, parent_id=None, access_token=None):
        parent = request.env['organisation.parents'].sudo().search(
            [('id', '=', parent_id)])
        if not parent:
            request.redirect('/my/home')
        partner = request.env.user.partner_id
        partner_parent = request.env['organisation.parents'].sudo().search(
            [('partner_id', '=', partner.id)])
        if partner_parent.id not in parent.mapped('id'):
            return Forbidden()
        values = self._parent_profile_get_page_view_values(parent, access_token)
        response = request.render(
            "organisation.portal_parent_profile_dashboard", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    # def _get_portal_form(self, uuid, mode):
    #     return request.env['formio.form']._get_portal_form(uuid, mode)

    @http.route('/my/athlete/form', type='http', auth='user',
                website=True)
    def portal_athlete_form(self, **post):
        form = request.env['formio.form'].sudo().search(
            [('id', '=', post['form_id'])])
        if not form:
            # TODO website page with message?
            return request.redirect("/")
        values = {}
        values.update({
            'form': form
        })

        # values = self._formio_form_get_page_view_values(form, **post)
        return request.render("organisation.portal_my_form_edit", values)

    @http.route('/formio/form/<string:uuid>', type='http', auth='user',
                website=True)
    def form_root(self, uuid, **kwargs):
        form = self._get_form(uuid, 'read')
        if not form:
            msg = 'Form UUID %s' % uuid
            return request.not_found(msg)

        # TODO REMOVE (still needed or obsolete legacy?)
        # Needed to update language
        context = request.env.context.copy()
        context.update({'lang': request.env.user.lang})
        request.env.context = context

        languages = form.builder_id.languages
        lang_en = request.env.ref('base.lang_en')

        if lang_en.active and form.builder_id.language_en_enable and 'en_US' not in languages.mapped(
                'code'):
            languages |= request.env.ref('base.lang_en')

        values = {
            'languages': languages.sorted('name'),
            'form': form,
            'formio_css_assets': form.builder_id.formio_css_assets,
            'formio_js_assets': form.builder_id.formio_js_assets,
        }
        return request.render('formio.formio_form_embed', values)

    @http.route('/survey_start', type='http', auth='user',
                website=True)
    def survey_start(self, **post):
        survey = request.env['survey.survey'].sudo().search(
            [('id', '=', post['survey_id'])])
        url = survey.start_url
        return request.redirect(url)

    @route(['/my/athlete_invoices'],
           type='http', auth='user', website=True)
    def my_athlete_invoices(self, page=1, date_begin=None, groupby=None,
                                date_end=None, sortby=None, filterby=None):
        parent = request.env['organisation.parents'].sudo().search([
            ('partner_id', '=', request.env.user.partner_id.id)
        ])
        athletes = parent.athlete_ids
        partners = athletes.partner_id
        domain = [('move_type', 'in',
                   ('out_invoice', 'out_refund', 'in_invoice', 'in_refund',
                    'out_receipt', 'in_receipt')),
                  ('partner_id', 'in', partners.ids)]
        values = self._prepare_portal_layout_values()

        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'invoice_date desc'},
            'duedate': {'label': _('Due Date'),
                        'order': 'invoice_date_due desc'},
            'name': {'label': _('Reference'), 'order': 'name desc'},
            'state': {'label': _('Status'), 'order': 'state'},
            'partner_id': {'label': _('Athlete'), 'order': 'partner_id desc'},
        }

        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin),
                       ('create_date', '<=', date_end)]

        # count for pager
        invoice_count = request.env['account.move'].sudo().search_count(domain)
        # invoice_count = len(athlete.invoice_ids)
        # pager
        pager = portal_pager(
            url="/my/invoices",
            url_args={'date_begin': date_begin, 'date_end': date_end,
                      'sortby': sortby},
            total=invoice_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        invoices = request.env['account.move'].sudo().search(domain,
                                                             order=order,
                                                             limit=self._items_per_page,
                                                             offset=pager[
                                                                 'offset'])
        # obj_invoices = athlete.invoice_ids
        # invoices = obj_invoices.search([], order=order, limit=self._items_per_page, offset=pager['offset'])

        request.session['my_invoices_history'] = invoices.ids[:100]

        values.update({
            'date': date_begin,
            'invoices': invoices,
            'page_name': 'invoice',
            'pager': pager,
            'default_url': '/my/invoices',
            'searchbar_sortings': searchbar_sortings,
            # 'searchbar_groupby': searchbar_groupby,
            'sortby': sortby,
            # 'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'show_athlete': True,
        })
        return request.render("account.portal_my_invoices", values)

    @route(['/upload_document'], type='http', auth='user', website=True)
    def upload_document(self, **post):
        athlete = request.env['organisation.athletes'].sudo().search(
            [('id', '=', post['athlete_id'])])
        values = {}
        values.update({
            'athlete': athlete,
        })
        return request.render("organisation.upload_document_form", values)

    @route(['/submit_document'], type='http', auth='user', website=True)
    def submit_document(self, **post):
        if 'athlete_id' in post:
            partner = request.env.user.partner_id
            document = request.env['athletes.documents'].sudo().create({
                'name': post['name'],
                'description': post['description'],
                'athlete_id': post['athlete_id'],
                'document': base64.b64encode(post.get('attachment1').read()),
            })
            if partner.org_group_selection == 'athletes':
                return request.redirect(
                    "/my/athlete-%s/documents" % post['athlete_id'])
            elif partner.org_group_selection == 'ex_coaches':
                return request.redirect(
                    "/my/athlete-%s/documents" % post['athlete_id'])
            elif partner.org_group_selection == 'parents':
                return request.redirect(
                    "/my/athlete-%s/documents" % post['athlete_id'])
            else:
                return request.redirect("/my")
        elif 'coach_id' in post:
            document = request.env['athletes.documents'].sudo().create({
                'name': post['name'],
                'description': post['description'],
                'coach_id': post['coach_id'],
                'document': base64.b64encode(post.get('attachment1').read()),
            })
            return request.redirect('/my/documents-%s' % post['coach_id'])
        else:
            return request.redirect('/my/home')

    @route(['/submit_multi_athlete_document'],
           type='http', auth='user', website=True)
    def submit_multi_athlete_document(self, **post):
        data_document = base64.b64encode(post.get('attachment1').read())
        if post['type'] == 'group':
            document = request.env['athletes.documents'].sudo().create({
                'name': post['name'],
                'description': post['description'],
                'group_id': post['group_id'],
                'document': data_document,
            })
            group = request.env['athlete.groups'].sudo().search(
                [('id', '=', post['group_id'])])
            athletes = group.athlete_ids
            for athlete in athletes:
                document = request.env['athletes.documents'].sudo().create({
                    'name': post['name'],
                    'description': post['description'],
                    'athlete_id': athlete.id,
                    'document': data_document
                })
        if post['type'] == 'athlete':
            athlete_count = post['athlete_count']
            athlete_ids = []
            for i in range(0, int(athlete_count)):
                str_athlete = "athlete" + str(i)
                if post[str_athlete] in athlete_ids:
                    athlete = request.env['organisation.athletes'].sudo(
                    ).search([('id', '=', post[str_athlete])])
                    raise ValidationError(_(
                        "Sorry..! You have selected the same "
                        "athlete '%s' more than once!",
                        athlete.name))
                athlete_ids.append(post[str_athlete])
            for i in range(0, int(athlete_count)):
                athlete = "athlete" + str(i)
                document = request.env['athletes.documents'].sudo().create({
                    'name': post['name'],
                    'description': post['description'],
                    'athlete_id': post[athlete],
                    'document': data_document,
                })
        return request.redirect('/athletes/documents/upload')

    @route(['/my/documents/upload'], type='http', auth='user', website=True)
    def coach_document_upload(self, **post):
        coach = request.env['organisation.coaches'].sudo().search(
            [('id', '=', post['coach_id'])])
        values = {}
        values.update({
            'coach': coach,
        })
        return request.render("organisation.upload_coach_document_form", values)

    @route(['/athletes/documents/upload'], type='http', auth='user', website=True)
    def coach_multiple_athlete_document_upload(self, **post):
        coach = request.env['organisation.coaches'].sudo().search(
            [('partner_id', '=', request.env.user.partner_id.id)])
        athletes = coach.athlete_ids
        groups = request.env['athlete.groups'].sudo().search([])
        group = request.env['athlete.groups'].sudo().search([], limit=1)
        grp_athletes = group.athlete_ids
        values = {}
        values.update({
            'coach': coach,
            'athletes': athletes,
            'groups': groups,
            'grp_athletes': grp_athletes,
        })
        athletes_info = []
        for athlete in athletes:
            athletes_info.append({'id': athlete.id,
                                  'name': athlete.name})
            values.update({
                'athletes_info': athletes_info,
            })
        return request.render(
            "organisation.coach_multiple_athlete_document_upload_form", values)

    @route(['/check_in'], type='http', auth='user',
           website=True)
    def check_in(self, **post):
        athlete = request.env['organisation.coaches'].sudo().search(
            [('partner_id', '=', request.env.user.partner_id.id)])
        employee = athlete.employee_id
        values = {}
        values.update({
            'employee': employee,
            'company': employee.company_id
        })
        return request.render(
            "organisation.enter_kiosk_mode_template", values)

    @route(['/my/fan_profile/<int:fan_id>', '/fan_profile/<int:fan_id>'],
           type='http', auth='user', website=True)
    def fan_dashboard_profile(self, fan_id=None, access_token=None):
        fan = request.env['organisation.fans'].sudo().search(
            [('id', '=', fan_id)])
        if not fan:
            request.redirect('/my/home')
        partner = request.env.user.partner_id
        partner_fan = request.env['organisation.fans'].sudo().search(
            [('partner_id', '=', partner.id)])
        if partner_fan.id not in fan.mapped('id'):
            return Forbidden()
        # values = self._parent_profile_get_page_view_values(parent, access_token)
        values = {}
        values.update({
            'fan': fan,
            'page_name': 'fan_dashboard',
            'fan_profile': True
        })
        response = request.render(
            "organisation.portal_fan_profile_dashboard", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/fan_booking/<int:fan_id>', '/fan_booking/<int:fan_id>'],
           type='http', auth='user', website=True)
    def fan_dashboard_booking(self, fan_id=None, access_token=None):
        return

    @route(['/my/fan_calendar/<int:fan_id>', '/fan_calendar/<int:fan_id>'],
           type='http', auth='user', website=True)
    def fan_dashboard_calendar(self, fan_id=None, access_token=None):
        fan = request.env['organisation.fans'].sudo().search(
            [('id', '=', fan_id)])
        if not fan:
            request.redirect('/my/home')
        partner = request.env.user.partner_id
        partner_fan = request.env['organisation.fans'].sudo().search(
            [('partner_id', '=', partner.id)])
        if partner_fan.id not in fan.mapped('id'):
            return Forbidden()
        # values = self._parent_profile_get_page_view_values(parent, access_token)
        values = {}
        events = fan.event_ids
        length = len(events)
        today = str(fields.Date.today())
        values.update({
            'fan': fan,
            'events': events,
            'length': length,
            'today': today,
            'page_name': 'fan_dashboard',
            'fan_calendar': True
        })
        events_info = []
        for ev in events:
            tz = pytz.timezone(
                (ev.event_tz or ev.env.context.get('tz') or 'UTC'))
            start = pytz.utc.localize(ev.start).astimezone(tz).strftime(
                "%Y-%m-%d %H:%M:%S")
            stop = pytz.utc.localize(ev.stop).astimezone(tz).strftime(
                "%Y-%m-%d %H:%M:%S")
            events_info.append({'title': ev.event_description,
                                'start': start,
                                'end': stop})
        values.update({
            'events_info': events_info,
        })
        response = request.render(
            "organisation.portal_fan_calendar_dashboard", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/get_athletes_list'], type='json', auth='user', website=True)
    def get_athletes_list(self, **post):
        group = request.env['athlete.groups'].sudo().search(
            [('id', '=', str(post['group_id']))])
        athletes = group.athlete_ids
        vals = []
        for athlete in athletes:
            vals.append({
                'name': athlete.name,
                'email': athlete.email,
                'phone': athlete.phone,
            })
        return {'vals': vals}

    @route(['/get_employee_kiosk_values'], type='json', auth='user', website=True)
    def get_employee_kiosk_values(self, **post):
        employee = request.env['hr.employee'].sudo().search([(
            'member_id', '=', post['member_id']
        )])
        if employee:
            return {
                'employee_id': employee.id,
                'employee_name': employee.name,
                'employee_state': employee.attendance_state,
                'employee_hours_today': employee.hours_today,
            }
        else:
            return {'warning': _(
                "No employee corresponding to Badge ID '%(barcode)s.'") % {
                                   'barcode': post['member_id']}}

    @route(['/get_employee_vehicles'], type='json', auth='user',
           website=True)
    def get_employee_vehicles(self, **post):
        veh_info = []
        if 'employee_id' in post:
            employee = request.env['hr.employee'].sudo().search([(
                'id', '=', post['employee_id']
            )])
            if employee:
                athlete = request.env['organisation.athletes'].sudo().search([(
                    'employee_id', '=', employee.id)])
                if athlete:
                    vehicles = athlete.vehicle_ids
                    for veh in vehicles:
                        veh_info.append({'id': veh.id, 'name': veh.name})
        return veh_info
