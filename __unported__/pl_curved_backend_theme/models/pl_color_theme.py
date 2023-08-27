# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class PlColorTheme(models.Model):
    _name = 'pl.color.theme'
    _description = 'Arc Color Theme'

    pl_body_background = fields.Char(string='Body')
    pl_side_bar = fields.Char(string='Side Bar')
    pl_menu = fields.Char(string='Menu')
    pl_menu_hover = fields.Char(string='Menu Hover')
    pl_button = fields.Char(string='Button')
    pl_border = fields.Char(string='Border')
    pl_heading = fields.Char(string='Heading')
    pl_link = fields.Char(string='Link')
    pl_primary_color = fields.Char(string='Primary Color')
    pl_tooltip = fields.Char(string='Tooltip')

    pl_user = fields.Many2one(string="User", comodel_name="res.users")
    pl_company = fields.Many2one(string="Company", comodel_name="res.company")
    pl_global = fields.Boolean(string="Global")
    pl_active = fields.Boolean(string="Theme selected")
    pl_default = fields.Boolean(string="Default theme")
    pl_template = fields.Boolean(string="Template theme")
    pl_template_id = fields.Many2one(comodel_name='pl.color.theme', string="Connected template")
    pl_sub_theme = fields.Many2one(comodel_name='pl.color.theme', string="Related theme")
    name = fields.Char(string="Name")

    @api.model
    def get_theme(self, scope, origin):
        pl_color_theme_info = {}
        pl_color_theme = []
        pl_domain = []
        if scope == 'User':
            pl_domain = ('pl_user', '=', origin.id)
        if scope == 'Company':
            pl_domain = ('pl_company', '=', origin.id)
        if scope == 'Global':
            pl_domain = ('pl_global', '=', True)

        # Get custom themes
        pl_color_theme_info['custom'] = self.env(su=True)['pl.color.theme'].search_read(
            [('pl_template_id', '=', False), pl_domain], fields=[])

        # check if user/company has active theme if not then make default theme as active.
        pl_active_theme = self.env(su=True)['pl.color.theme'].search([pl_domain, ('pl_active', '=', True)])
        if not pl_active_theme:
            pl_default_theme = self.env(su=True)['pl.color.theme'].search([pl_domain, ('pl_default', '=', True)])
            pl_default_theme.write({'pl_active': True})

        # Get pre-defined theme.
        pl_template_theme = self.env(su=True)['pl.color.theme'].search_read([('pl_template', '=', True)], fields=[])
        for temp_theme in pl_template_theme:
            pl_user_theme_temp = self.env(su=True)['pl.color.theme'].search_read(
                [('pl_template_id', '=', temp_theme['id']), pl_domain], fields=[])
            if not pl_user_theme_temp:
                vals = {
                    'pl_body_background': temp_theme['pl_body_background'],
                    'pl_menu': temp_theme['pl_menu'],
                    'pl_menu_hover': temp_theme['pl_menu_hover'],
                    'pl_button': temp_theme['pl_button'],
                    'pl_border': temp_theme['pl_border'],
                    'pl_heading': temp_theme['pl_heading'],
                    'pl_link': temp_theme['pl_link'],
                    'pl_primary_color': temp_theme['pl_primary_color'],
                    'pl_tooltip': temp_theme['pl_tooltip'],
                    'pl_template_id': temp_theme['id'],
                    'name': temp_theme['name'],
                    'pl_active': True if temp_theme['pl_default'] else False,
                    'pl_default': True if temp_theme['pl_default'] else False,
                }
                if scope == 'User':
                    vals['pl_user'] = origin.id
                if scope == 'Company':
                    vals['pl_company'] = origin.id
                if scope == 'Global':
                    vals['pl_global'] = True

                res = self.env(su=True)['pl.color.theme'].create(vals)
                pl_color_theme += self.env(su=True)['pl.color.theme'].search_read([('id', '=', res.id)])
            else:
                pl_user_theme_temp = self.plCheckThemeInfo(temp_theme, pl_user_theme_temp)
                pl_color_theme += pl_user_theme_temp
        pl_color_theme_info['predefined'] = pl_color_theme

        # Return theme for user and company settings.
        if scope in ['User', 'Company']:

            pl_themes = self.env(su=True)['pl.color.theme'].search_read(
                [('pl_template_id', '=', False), ('pl_global', '=', True)], fields=[])
            pl_theme_returned = pl_color_theme_info['predefined']

            # Global custom themes
            for themes in pl_themes:
                if scope == 'User':
                    pl_domain = [('pl_user', '=', origin.id), ('pl_sub_theme', '=', themes['id'])]
                    vals = {
                        'pl_user': origin.id,
                        'pl_sub_theme': themes['id']
                    }
                if scope == 'Company':
                    pl_domain = [('pl_company', '=', origin.id), ('pl_sub_theme', '=', themes['id'])]
                    vals = {
                        'pl_company': origin.id,
                        'pl_sub_theme': themes['id']
                    }
                pl_theme_obj = self.env(su=True)['pl.color.theme'].search_read(pl_domain)
                if not pl_theme_obj:
                    vals.update({
                        'pl_body_background': themes['pl_body_background'],
                        'pl_menu': themes['pl_menu'],
                        'pl_menu_hover': themes['pl_menu_hover'],
                        'pl_button': themes['pl_button'],
                        'pl_border': themes['pl_border'],
                        'pl_heading': themes['pl_heading'],
                        'pl_link': themes['pl_link'],
                        'pl_primary_color': themes['pl_primary_color'],
                        'pl_tooltip': themes['pl_tooltip'],
                        'pl_template_id': themes['id'],
                        'name': themes['name'],
                        'pl_active': True if themes['pl_default'] else False,
                        'pl_default': True if themes['pl_default'] else False,
                    })
                    self.env(su=True)['pl.color.theme'].create(vals)
                    if not pl_theme_returned:
                        pl_theme_returned = self.env(su=True)['pl.color.theme'].search_read(pl_domain)
                    else:
                        pl_theme_returned.append(self.env(su=True)['pl.color.theme'].search_read(pl_domain)[0])
                else:
                    if not pl_theme_returned:
                        pl_theme_returned = pl_theme_obj
                    else:
                        pl_theme_returned.append(pl_theme_obj[0])
            return pl_theme_returned

        return pl_color_theme_info

    def plCheckThemeInfo(self, temp_theme, pl_user_theme_temp):
        """
        Function to check updated theme colors.
        :param temp_theme:
        :param pl_user_theme_temp:
        :return:
        """
        pl_field_check = ['pl_body_background', 'pl_menu', 'pl_menu_hover', 'pl_button', 'pl_border',
                          'pl_heading', 'pl_link', 'pl_primary_color', 'pl_tooltip', 'name'
                          ]
        pl_update_field = dict()
        for rec in pl_field_check:
            if temp_theme[rec] != pl_user_theme_temp[0][rec]:
                pl_update_field.update({rec: temp_theme[rec]})

        if len(pl_update_field):
            self.env['pl.color.theme'].sudo().search([('id', '=', pl_user_theme_temp[0]['id'])]).write(pl_update_field)
            pl_user_theme_temp = self.env['pl.color.theme'].sudo().search_read(
                [('id', '=', pl_user_theme_temp[0]['id'])])
        return pl_user_theme_temp

    def unlink(self):
        pl_shadow_theme = self.sudo().search([('pl_sub_theme', '=', self.id)])
        for rec in pl_shadow_theme:
            rec.unlink()
        return super(PlColorTheme, self).unlink()

    def write(self, vals):
        res = super(PlColorTheme, self).write(vals)
        pl_shadow_theme = self.env(su=True)['pl.color.theme'].search([('pl_sub_theme', '=', self.id)])
        for rec in pl_shadow_theme:
            rec.write(vals)
        return res
