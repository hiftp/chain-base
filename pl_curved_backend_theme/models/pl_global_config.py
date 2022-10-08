# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
from odoo.http import request
import logging
import base64
import io
from PIL import Image
from odoo.tools.mimetypes import guess_mimetype

_logger = logging.getLogger(__name__)


class PlThemeGlobalConfig(models.Model):
    _name = "pl.global.config"
    _rec_name = 'pl_recname'
    _description = "Global Settings"
    # FixMe : Change the default values

    pl_recname = fields.Char(default="Global Settings")
    pl_pwa_icon = fields.Binary(string="Icon", default=False)
    pl_pwa_icon_type = fields.Char(string="Icon Type")
    pl_click_edit = fields.Boolean(string="Double-click Edit", default=False)
    pl_menu_bar = fields.Selection(string="Menu Bar Position",
                                   selection=[('Horizontal', 'Horizontal'), ('Vertical', 'Vertical')],
                                   default='Horizontal')
    pl_chatter = fields.Selection(string="Chatter Position",
                                  selection=[('pl_chatter_bottom', 'Bottom'), ('pl_chatter_right', 'Right')],
                                  default='pl_chatter_bottom')
    # pl_website_title = fields.Char(string="Website Backend Title", default='odoo')
    pl_website_title = fields.Char(string="Website Backend Title", default='Saltfun')
    pl_click_edit = fields.Boolean(string="Double-click Edit", default=False)
    # pl_website_title_enable = fields.Boolean(string="Enable Website Backend Title")
    pl_website_title_enable = fields.Boolean(string="Enable Website Backend Title", default=True)
    pl_favicon = fields.Binary(string="Favicon")
    pl_company_logo_enable = fields.Boolean(string="Enable Company Logo")
    pl_small_company_logo = fields.Binary(string="Small Logo")
    pl_company_logo = fields.Binary(string="Company Logo")
    # pl_enterprise_apps = fields.Boolean(string="Hide Enterprise Apps", default=False)
    pl_enterprise_apps = fields.Boolean(string="Hide Enterprise Apps", default=True)
    pl_odoo_referral = fields.Boolean(string="Show Odoo Referral", default=False)
    pl_theme_style = fields.Selection(string="Theme Style", selection=[('curved_theme_style', 'Curved'),
                                                                       ('boxed_theme_style', 'Boxed')],
                                      default='curved_theme_style')
    pl_colors_theme = fields.Many2one(comodel_name='pl.color.theme')
    pl_breadcrumb_style = fields.Selection(string="Breadcrumb style", selection=[('pl_breadcrumb_style_1', 'Style 1'),
                                                                             ('pl_breadcrumb_style_2', 'Style 2'),
                                                                             ('pl_breadcrumb_style_3', 'Style 3'),
                                                                             ('pl_breadcrumb_style_4', 'Style 4'),
                                                                             ('pl_breadcrumb_style_5', 'Style 5'),
                                                                             ('pl_breadcrumb_style_6', 'Style 6'),
                                                                             ('pl_breadcrumb_style_7', 'Style 7'),
                                                                             ], default='pl_breadcrumb_style_1')
    pl_button_style = fields.Selection(string="Button style", selection=[('pl_button_style_1', 'Style 1'),
                                                                         ('pl_button_style_2', 'Style 2'),
                                                                         ('pl_button_style_3', 'Style 3'),
                                                                         ('pl_button_style_4', 'Style 4'),
                                                                         ('pl_button_style_5', 'Style 5'),
                                                                         ], default='pl_button_style_1')
    pl_body_background_type = fields.Selection(string="Body Background Image",
                                               selection=[('Image', 'Image'), ('Color', 'Color')], default='Image')
    pl_body_background_color = fields.Selection(selection=[('body_back_color_1', 'Body Background Color 1'),
                                                           ('body_back_color_2', 'Body Background Color 2'),
                                                           ('body_back_color_3', 'Body Background Color 3'),
                                                           ('body_back_color_4', 'Body Background Color 4'),
                                                           ('body_back_color_5', 'Body Background Color 5'),
                                                           ('body_back_color_6', 'Body Background Color 6'),
                                                           ('body_back_color_7', 'Body Background Color 7'),
                                                           ('body_back_color_8', 'Body Background Color 8')],
                                                default='body_back_color_1',
                                                string="Body Background Color")
    pl_body_background_image = fields.Binary(string="Body background Image")
    pl_tab_style = fields.Selection(string="Tab style", selection=[('pl_tab_style1', 'Style 1'),
                                                                   ('pl_tab_style2', 'Style 2'),
                                                                   ('pl_tab_style3', 'Style 3'),
                                                                   ('pl_tab_style4', 'Style 4'),
                                                                   ('pl_tab_style5', 'Style 5'),
                                                                   ], default='pl_tab_style1')
    pl_checkbox_style = fields.Selection(string="Checkbox style",
                                         selection=[('pl_checkbox_1', 'Style 1'), ('pl_checkbox_2', 'Style 2'),
                                                    ('pl_checkbox_3', 'Style 3'),
                                                    ('pl_checkbox_4', 'Style 4'), ('pl_checkbox_5', 'Style 5')],
                                         default='pl_checkbox_1')
    pl_icon_design = fields.Char(string="Icon Design")
    pl_login_page_style = fields.Selection(string="Login Page Style",
                                           selection=[('default', 'Default'), ('Style1', 'Style1'), ('Style2', 'Style2'), ('Style3', 'Style3'),
                                                      ('Style4', 'Style4'), ('Style5', 'Style5')], default='default')
    pl_login_page_logo = fields.Binary(string="Login background logo")
    pl_login_page_logo_enable = fields.Boolean(string="Enable login background logo", default=False)
    pl_login_background_image = fields.Binary(string="Login background Image")
    pl_login_background_image_enable = fields.Boolean(string="Enable Login Background Image", default=False)
    pl_header = fields.Boolean(string="Show Header", default=False)
    pl_footer = fields.Boolean(string="Show Footer", default=False)
    pl_login_back_image_opacity = fields.Integer(string="Login Background Image Opacity")
    pl_header_content = fields.Char(string="Header Content", default="Any Message you want to display on top.")
    pl_footer_content = fields.Char(string="Footer Content", default="Any Message you want to display on bottom.")

    pl_font_style = fields.Selection(string="Font Style", selection=[('pl_font_poppins', 'Poppins'),
                                                                     ('pl_font_lato', 'Lato'),
                                                                     ('pl_font_raleway', 'Raleway'),
                                                                     ('pl_font_arial', 'Arial'),
                                                                     ('pl_font_times_new', 'Times new'),
                                                                     ('pl_font_open_san', 'Open San'),
                                                                     ('pl_font_roboto', 'Roboto'),
                                                                     ('pl_font_ubuntu', 'Ubuntu'),
                                                                     ], default='pl_font_poppins')

    pl_font_size = fields.Selection(string="Font Size", selection=[('pl_font_size_small', 'Small'),
                                                                   ('pl_font_size_medium', 'Medium'),
                                                                   ('pl_font_size_large', 'Larger'),
                                                                   ('pl_font_size_extra_large', 'Extra Large')
                                                                   ], default='pl_font_size_medium')

    pl_body_background = fields.Char(string="Body background")
    pl_body_background_opacity = fields.Float(string="Body Background Image Opacity", default=0.5)
    pl_app_drawer_background = fields.Char(string="App Drawer background", default=False)
    pl_app_drawer_background_opacity = fields.Float(string="App Drawer Background Opacity", default=0.5)

    pl_separator_style = fields.Selection(string="Separator style", selection=[('pl_separator_1', 'Separator 1'),
                                                                               ('pl_separator_2', 'Separator 2'),
                                                                               ('pl_separator_3', 'Separator 3'),
                                                                               ('pl_separator_4', 'Separator 4'),
                                                                               ('pl_separator_5', 'Separator 5')],
                                          default='pl_separator_1')

    pl_radio_button_style = fields.Selection(string="Radio Button Style",
                                             selection=[('pl_radio_button_1', 'Style 1'),
                                                        ('pl_radio_button_2', 'Style 2'),
                                                        ('pl_radio_button_3', 'Style 3'),
                                                        ('pl_radio_button_4', 'Style 4'),
                                                        ('pl_radio_button_5', 'Style 5')], default='pl_radio_button_1')

    pl_popup_animation_style = fields.Selection(string="Popup Animation style",
                                                selection=[('pl_popup_style1', 'Style 1'),
                                                           ('pl_popup_style2', 'Style 2'),
                                                           ('pl_popup_style3', 'Style 3'),
                                                           ('pl_popup_style4', 'Style 4'),
                                                           ('pl_popup_style5', 'Style 5'),
                                                           ('pl_popup_style6', 'Style 6'),
                                                           ('pl_popup_style7', 'Style 7'),
                                                           ('pl_popup_style8', 'Style 8'),
                                                           ('pl_popup_style9', 'Style 9'),
                                                           ('pl_popup_style10', 'Style 10'),
                                                           ], default='pl_popup_style1')

    pl_loaders = fields.Selection(string="Loading Bar", selection=[('pl_loader_1', 'Loader 1'),
                                                                   ('pl_loader_2', 'Loader 2'),
                                                                   ('pl_loader_3', 'Loader 3'),
                                                                   ('pl_loader_4', 'Loader 4'),
                                                                   ('pl_loader_5', 'Loader 5'),
                                                                   ('pl_loader_6', 'Loader 6'),
                                                                   ('pl_loader_7', 'Loader 7'),
                                                                   ('pl_loader_default', 'Default Loader'),
                                                                   ], default='pl_loader_default')

    pl_theme_color = fields.Many2one(comodel_name='pl.color.theme', string='Current color theme')

    # ---- Scope ---- #
    # FixMe: Single scope fields can be displayed as dummy for now only on  HTML

    scope_pl_auto_dark_mode = fields.Selection(
        selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')], default='User')
    scope_pl_list_density = fields.Selection(selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                             default='User')
    scope_pl_click_edit = fields.Selection(selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                           default='User')
    scope_pl_menu_bar = fields.Selection(selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                         default='User')
    scope_pl_favorite_bar = fields.Selection(selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                             default='User')
    scope_pl_chatter = fields.Selection(selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                        default='User')
    scope_pl_website_title = fields.Selection(string="Scope of Website Backend Title",
                                              selection=[('User', 'User'), ('Company', 'Company'),
                                                         ('Global', 'Global')], default='Global')
    scope_pl_favicon = fields.Selection(string="Scope of Favicon",
                                        selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                        default='User')
    scope_pl_company_logo = fields.Selection(string="Scope of company logo",
                                             selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                             default='Global')
    scope_pl_small_company_logo = fields.Selection(string="Scope of small company logo",
                                                   selection=[('User', 'User'), ('Company', 'Company'),
                                                              ('Global', 'Global')], default='Global')
    scope_pl_enterprise_apps = fields.Selection(string="Scope of Enterprise Apps",
                                                selection=[('User', 'User'), ('Company', 'Company'),
                                                           ('Global', 'Global')],
                                                default='User')
    scope_pl_odoo_referral = fields.Selection(string="Scope of Odoo referral",
                                              selection=[('User', 'User'), ('Company', 'Company'),
                                                         ('Global', 'Global')],
                                              default='User')
    scope_pl_theme_style = fields.Selection(string="Scope of Theme Style",
                                            selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                            default='User')
    scope_pl_colors_theme = fields.Selection(string="Scope of Colors Theme",
                                             selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                             default='User')
    scope_pl_font_style = fields.Selection(string="Scope of Font Style",
                                           selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                           default='User')
    scope_pl_button_style = fields.Selection(string="Scope of Button style",
                                             selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                             default='User')
    scope_pl_body_background = fields.Selection(string="Scope of Body background",
                                                selection=[('User', 'User'), ('Company', 'Company'),
                                                           ('Global', 'Global')],
                                                default='User')

    scope_pl_app_drawer_background = fields.Selection(string="Scope of App Drawer background",
                                                      selection=[('User', 'User'), ('Company', 'Company'),
                                                                 ('Global', 'Global')],
                                                      default='User')

    scope_pl_separator_style = fields.Selection(string="Scope of Seperator Style",
                                                selection=[('User', 'User'), ('Company', 'Company'),
                                                           ('Global', 'Global')],
                                                default='User')
    scope_pl_tab_style = fields.Selection(string="Scope of Tab Style",
                                          selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                          default='User')
    scope_pl_checkbox_style = fields.Selection(string="Scope of Checkbox Style",
                                               selection=[('User', 'User'), ('Company', 'Company'),
                                                          ('Global', 'Global')],
                                               default='User')
    scope_pl_popup_animation_style = fields.Selection(string="Scope of Animation Style",
                                                      selection=[('User', 'User'), ('Company', 'Company'),
                                                                 ('Global', 'Global')],
                                                      default='User')
    scope_pl_loaders = fields.Selection(string="Scope of Loaders",
                                        selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                        default='User')
    scope_pl_icon_design = fields.Selection(string="Scope of Icon Design",
                                            selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                            default='User')
    scope_pl_login_page_style = fields.Selection(string="Scope of Login Style",
                                                 selection=[('User', 'User'), ('Company', 'Company'),
                                                            ('Global', 'Global')],
                                                 default='User')
    scope_pl_login_background_image = fields.Selection(string="Scope of Login Background",
                                                       selection=[('User', 'User'), ('Company', 'Company'),
                                                                  ('Global', 'Global')],
                                                       default='User')
    scope_pl_header = fields.Selection(string="Scope of Header",
                                       selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                       default='User')
    scope_pl_footer = fields.Selection(string="Scope of Footer",
                                       selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                       default='User')

    scope_pl_font_size = fields.Selection(string="Scope of Font Size",
                                          selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                          default='User')
    scope_pl_radio_button_style = fields.Selection(string="Scope of Radio Button Style",
                                                   selection=[('User', 'User'), ('Company', 'Company'),
                                                              ('Global', 'Global')],
                                                   default='User')

    # Note: these fields are created only for user scopes.
    scope_pl_favtbar_autohide = fields.Selection(string="Scope of Favorite bar auto hide",
                                                 selection=[('User', 'User')],
                                                 default='User')
    scope_pl_favtbar_position = fields.Selection(string="Scope of Favorite bar position",
                                                 selection=[('User', 'User')],
                                                 default='User')
    scope_pl_show_app_name = fields.Selection(string="Scope of Apps name show",
                                              selection=[('User', 'User')],
                                              default='User')
    scope_pl_user_menu_placement = fields.Selection(string="Scope of Apps menu placement",
                                                    selection=[('User', 'User')],
                                                    default='User')
    scope_pl_menubar_autohide = fields.Selection(string="Scope of Apps menubar auto hide",
                                                 selection=[('User', 'User')],
                                                 default='User')

    pl_body_background_image_enable = fields.Boolean(string="Enable body background images", default=False)

    @api.constrains('scope_pl_company_logo')
    def pl_onchange(self):
        self.scope_pl_small_company_logo = self.scope_pl_company_logo

    def pl_get_config_value(self, pl_fields):
        """
        FixMe: Handle for multiple fields
        Todo: Create same for setting values and test for all cases
        Retrieve the value for a given field.
            :param string pl_fields: The field of the parameter value to retrieve.
            :return: The value of the parameter, or ``default`` if it does not exist.
            :rtype: Dictionary or Value depending on size of pl_fields list
        """
        pl_models = {
            'User': 'res.users',
            'Company': 'res.company',
            'Global': 'pl.global.config',
        }
        pl_scopes = self.pl_get_field_scope(['scope_' + i for i in pl_fields])
        # pl_scopes = 'Company'
        if pl_scopes and len(pl_fields) == 1:
            pl_field_value = self.env(su=True)[pl_models.get(pl_scopes)].search_read([], fields=pl_fields or [],
                                                                                     limit=1)
            return pl_field_value[0].get(str(pl_fields[0]))
        return False

    def pl_get_field_scope(self, pl_fields):
        """
        Retrive the selected model/scope for the fields
            :param pl_fields: List of fields
            :return: Dictionary or Value depending on size of pl_fields list
        """
        pl_scope_values = self.env(su=True)['pl.global.config'].search_read([], fields=pl_fields or [], limit=1)
        # if pl_fields and len(pl_scope_values) > 0 and len(pl_fields) == 1:
        #     pl_scope_values = pl_scope_values[0].get(str(pl_fields[0]))
        return pl_scope_values

    @api.model
    def pl_get_config_values(self):
        """
        Function to return scope fields values.
        :return:
        """
        pl_global_config_id = self.env.ref('pl_curved_backend_theme.pl_global_config_single_rec').id
        pl_global_data = self.sudo().search([('id', '=', pl_global_config_id)], limit=1)
        values = False
        if pl_global_data:
            values = {
                # 'scope_pl_auto_dark_mode': pl_global_data.scope_pl_auto_dark_mode,
                'scope_pl_list_density': pl_global_data.scope_pl_list_density,
                'scope_pl_click_edit': pl_global_data.scope_pl_click_edit,
                'scope_pl_menu_bar': pl_global_data.scope_pl_menu_bar,
                'scope_pl_favorite_bar': pl_global_data.scope_pl_favorite_bar,
                'scope_pl_chatter': pl_global_data.scope_pl_chatter,
                'scope_pl_website_title': pl_global_data.scope_pl_website_title,
                'scope_pl_company_logo': pl_global_data.scope_pl_company_logo,
                'scope_pl_theme_style': pl_global_data.scope_pl_theme_style,
                'scope_pl_font_style': pl_global_data.scope_pl_font_style,
                'scope_pl_button_style': pl_global_data.scope_pl_button_style,
                'scope_pl_body_background': pl_global_data.scope_pl_body_background,
                'scope_pl_separator_style': pl_global_data.scope_pl_separator_style,
                'scope_pl_tab_style': pl_global_data.scope_pl_tab_style,
                'scope_pl_checkbox_style': pl_global_data.scope_pl_checkbox_style,
                'scope_pl_popup_animation_style': pl_global_data.scope_pl_popup_animation_style,
                'scope_pl_loaders': pl_global_data.scope_pl_loaders,
                'scope_pl_font_size': pl_global_data.scope_pl_font_size,
                'scope_pl_radio_button_style': pl_global_data.scope_pl_radio_button_style,
                'scope_pl_app_drawer_background': pl_global_data.scope_pl_app_drawer_background,
                'scope_pl_colors_theme': pl_global_data.scope_pl_colors_theme,
            }
        return values

    @api.model
    def pl_save_apply_scope(self, unsaved_data):
        """
        Function to save changed scope for settings.
        :return:
        """
        pl_global_config_id = self.env.ref('pl_curved_backend_theme.pl_global_config_single_rec').id
        pl_global_data = self.sudo().search([('id', '=', pl_global_config_id)], limit=1)
        if pl_global_data:
            pl_global_data.write(unsaved_data)
            _logger.info(_("Theme setting scope is changed successfully."))

    @api.model
    def pl_get_global_setting(self):
        """
        Function to return list of dictionary for global theme setting data.
        :return:
        """
        pl_global_config_id = self.env.ref('pl_curved_backend_theme.pl_global_config_single_rec').id
        pl_global_data = self.sudo().search([('id', '=', pl_global_config_id)], limit=1)
        values = {
            'pl_menu_bar': pl_global_data.pl_menu_bar,
            'pl_theme_style': pl_global_data.pl_theme_style,
            'pl_font_style': pl_global_data.pl_font_style,
            'pl_font_size': pl_global_data.pl_font_size,
            'pl_button_style': pl_global_data.pl_button_style,
            'pl_breadcrumb_style': pl_global_data.pl_breadcrumb_style,
            'pl_body_background': pl_global_data.pl_body_background,
            'pl_separator_style': pl_global_data.pl_separator_style,
            'pl_tab_style': pl_global_data.pl_tab_style,
            'pl_checkbox_style': pl_global_data.pl_checkbox_style,
            'pl_radio_button_style': pl_global_data.pl_radio_button_style,
            'pl_popup_animation_style': pl_global_data.pl_popup_animation_style,
            'pl_loaders': pl_global_data.pl_loaders,
        }
        return values

    @api.model
    def get_body_background(self, pl_fields):
        """
        function to return body background and opacity based on its scope and currently active background.
        :return:
        """
        pl_global_config_id = self.env.ref('pl_curved_backend_theme.pl_global_config_single_rec')
        pl_image_model = {
            'pl_body_background': 'pl.body.background',
            'pl_app_drawer_background': 'pl.drawer.background'
        }
        pl_result = {}

        for rec in pl_fields:
            # First check for scope
            scope = pl_global_config_id.sudo()['scope_' + rec]
            pl_origin_data = False
            if scope == 'Global':
                pl_origin_data = pl_global_config_id
                pl_domain = [('pl_global', '=', True), ('pl_active', '=', True)]

            if scope == 'Company':
                pl_origin_data = self.env.user.company_id
                pl_domain = [('pl_company', '=', pl_origin_data.id), ('pl_active', '=', True)]

            if scope == 'User':
                pl_origin_data = self.env.user
                pl_domain = [('pl_user', '=', pl_origin_data.id), ('pl_active', '=', True)]

            if not pl_origin_data:
                return False

            if pl_origin_data[rec]:
                pl_result[rec] = {
                    'type': 'color',
                    'value': pl_origin_data[rec][:pl_origin_data[rec].rfind(',')] + ', ' + str(
                        pl_origin_data[rec + '_opacity']) + ')',
                }
                if rec == 'pl_app_drawer_background':
                    pl_drawer_font_style = self.env['pl.drawer.colors'].search(
                        [('pl_colors', '=', pl_origin_data[rec])])
                    if pl_drawer_font_style:
                        pl_result['pl_drawer_font_style'] = pl_drawer_font_style.pl_font_style
            if not pl_origin_data[rec]:
                pl_back = self.env[pl_image_model[rec]].sudo().search(pl_domain, limit=1)
                pl_result[rec] = {
                    'type': 'image',
                    'value': self.pl_get_image_url(pl_back.pl_image),
                    'opacity': pl_origin_data[rec + '_opacity']
                }
                if rec == 'pl_body_background':
                    pl_body_background_image_enable = True
                    if scope == 'User':
                        pl_body_background_image_enable = self.sudo().env.user.pl_body_background_image_enable
                    if scope == 'Company':
                        pl_body_background_image_enable = self.sudo().env.user.company_id.pl_body_background_image_enable
                    if scope == 'Global':
                        pl_body_background_image_enable = pl_global_config_id.pl_body_background_image_enable

                    if not pl_body_background_image_enable:
                        pl_result[rec]['value'] = False

        return pl_result

    @api.model
    def pl_get_image_url(self, data):
        file_type_magic_word = {
            '/': 'jpg',
            'R': 'gif',
            'i': 'png',
            'P': 'svg+xml',
        }
        if not data:
            return False
        return 'data:image/' + (file_type_magic_word.get(data[0]) or 'png') + ';base64,' + data.decode("utf-8")

    @api.model
    def pl_get_value_from_scope(self, pl_field_list):
        pl_global_origin = self.env.ref('pl_curved_backend_theme.pl_global_config_single_rec')
        pl_user = self.env.user
        pl_company = self.env.user.company_id
        pl_result = {}

        # Get fields scope
        pl_scopes = pl_global_origin.pl_get_field_scope(['scope_' + i for i in pl_field_list])

        # compute fields value based on the scope.
        if len(pl_scopes):
            for key, value in pl_scopes[0].items():
                if value == 'User':
                    self.pl_get_field_value(pl_user, key.split('scope_')[1], pl_result)
                if value == 'Company':
                    self.pl_get_field_value(pl_company, key.split('scope_')[1], pl_result)
                if value == 'Global':
                    self.pl_get_field_value(pl_global_origin, key.split('scope_')[1], pl_result)
        return pl_result

    def pl_get_field_value(self, origin_data, key, pl_result):
        # check for special fields
        pl_special_fields = self.pl_get_special_fields()
        if key in pl_special_fields.keys():
            # special fields will check it will only returns the data if its enabler field is checked.
            if origin_data[pl_special_fields[key]]:
                pl_result[key] = origin_data[key]
            else:
                pl_result[key] = False
        else:
            pl_result[key] = origin_data[key]

    def pl_get_special_fields(self):
        return {'pl_company_logo': 'pl_company_logo_enable',
                'pl_small_company_logo': 'pl_company_logo_enable'}

    def write(self, vals):
        if ('pl_pwa_icon' in vals) and not vals.get('pl_pwa_icon'):
            pl_prev_icons = self.env["ir.attachment"].sudo().search(
                [('url', 'like', '/pl_curved_backend_theme/logo')])
            if pl_prev_icons:
                pl_prev_icons.unlink()
        if vals.get('pl_pwa_icon'):
            # Check for icon extension and size.
            pl_pwa_icon_decode = base64.b64decode(vals.get('pl_pwa_icon'))
            pl_pwa_mimetype = guess_mimetype(pl_pwa_icon_decode)
            vals['pl_pwa_icon_type'] = pl_pwa_mimetype
            if pl_pwa_mimetype.startswith('image/png'):
                pl_icon_size = self.pl_get_icon_size(pl_pwa_icon_decode)
                if pl_icon_size.size < (512, 512):
                    raise exceptions.UserError(_("Please upload icon 512x512 resolution or bigger."))

                # First delete the previous icons.
                pl_prev_icons = self.env["ir.attachment"].sudo().search(
                    [('url', 'like', '/pl_curved_backend_theme/logo')])
                if pl_prev_icons:
                    pl_prev_icons.unlink()

                # Create different icons for pwa.
                for size in [(72, 72), (96, 96), (128, 128), (144, 144), (152, 152), (192, 192), (256, 256), (384, 384),
                             (512, 512)]:
                    self.pl_create_icons_size(pl_pwa_icon_decode, size, pl_pwa_mimetype, extension='.png')
            else:
                raise exceptions.UserError(
                    _("Please upload PNG file.")
                )

        return super(PlThemeGlobalConfig, self).write(vals)

    def pl_get_icon_size(self, icon):
        icon_bytes = io.BytesIO(icon)
        return Image.open(icon_bytes)

    def pl_create_icons_size(self, pl_icon, size, pl_pwa_mimetype, extension):
        url = '/pl_curved_backend_theme/logo/icon_' + str(size[0]) + '_' + request.db + extension

        pl_image = self.pl_get_icon_size(pl_icon)
        pl_img_resize = pl_image.resize(size)
        pl_io = io.BytesIO()
        pl_img_resize.save(pl_io, format="PNG")
        pl_icon = base64.b64encode(pl_io.getvalue())

        values = {
            "datas": pl_icon,
            "db_datas": pl_icon,
            "url": url,
            "name": url,
            "type": "binary",
            "mimetype": pl_pwa_mimetype
        }
        self.env["ir.attachment"].sudo().create(values)
