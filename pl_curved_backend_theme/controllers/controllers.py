# -*- coding: utf-8 -*-
from odoo.http import request, route, _logger
import requests
from datetime import datetime
import base64
from odoo.addons.web.controllers.main import Home
from odoo.addons.auth_signup.controllers.main import AuthSignupHome

from odoo import http, _


class PlCurvedBackendTheme(http.Controller):

    @route(['/pl_curved_backend_theme/save/form_width'], type='json', auth='user')
    def pl_save_form_page_width(self, val):
        request.env.user.write({
            'pl_form_page_width': val
        })

    @route(['/pl_curved_backend_theme/save/pl_splitted_form_width'], type='json', auth='user')
    def pl_save_split_form_page_width(self, data):
        request.env.user.write(data)

    @route(['/update/bookmarpl'], type='json', auth='user')
    def update_bookmarpl(self, **post):
        """
        Update the Bookmarpl
        :param post: dict of functionality(create_new, rename, reposition, delete) and corresponding bookmark details
        :return: Updated XML template of bookmark
        """
        user_id = request.env.user.id
        if post.get('create_new', False):
            bookmark_name = post['bookmark_name']
            bookmark_url = post['bookmark_url']
            bookmark_position = post['bookmark_position']
            request._cr.execute(
                'insert into pl_bookmark (pl_bookmark_name,pl_bookmark_url,pl_bookmark_position,pl_user_id) values (%s,%s,%s,%s)',
                (bookmark_name, bookmark_url, bookmark_position, user_id))
        elif post.get('rename', False):
            bookmark_name = post['bookmark_name']
            bookmark_id = post['bookmark_id']
            request._cr.execute('update pl_bookmark set pl_bookmark_name=%s where id = %s and pl_user_id = %s ',
                                (bookmark_name, bookmark_id, user_id))
        elif post.get('reposition', False):
            bookmark_id = post['bookmark_id']
            bookmark_position = int(post['bookmark_position'])
            reposition = post['reposition']
            new_position = False
            if reposition == 'move_up':
                new_position = bookmark_position - 1
            elif reposition == 'move_down':
                new_position = bookmark_position + 1
            else:
                _logger.info("Unable to change position of Bookmark.")
            if new_position:
                request._cr.execute('update pl_bookmark set pl_bookmark_position=%s where id = %s and pl_user_id = %s ',
                                    (new_position, bookmark_id, user_id))
                request._cr.execute(
                    'update pl_bookmark set pl_bookmark_position=%s where pl_bookmark_position = %s and pl_user_id = %s and id!=%s ',
                    (bookmark_position, new_position, user_id, bookmark_id))
        elif post.get('delete', False):
            bookmark_id = post['bookmark_id']
            request._cr.execute('Delete from pl_bookmark where id =%s and pl_user_id = %s',
                                (bookmark_id, user_id))
        pl_bookmarpl = request.env['pl.bookmark'].search([('pl_user_id', '=', user_id)], order='pl_bookmark_position')
        values = {
            'bookmarpl': pl_bookmarpl,
        }
        return request.env['ir.ui.view']._render_template("pl_curved_backend_theme.pl_bookmark_", values)

    @route(['/render/bookmarpl'], type='json', auth='user')
    def render_bookmark_template(self):
        """
        Render the HTML of User's bookmarpl
        :return: XML Template of Bookmark
        """
        user_id = request.env.user.id
        pl_bookmarpl = request.env['pl.bookmark'].search([('pl_user_id', '=', user_id)], order='pl_bookmark_position')
        values = {
            'bookmarpl': pl_bookmarpl,
        }
        return request.env['ir.ui.view']._render_template("pl_curved_backend_theme.pl_bookmark_", values)

    @route(['/get/installed/languages'], type='json', auth='public')
    def get_languages(self):
        """
        Render the list of installed languages
        :return: list of tuples of short code & languages
        """
        languages = request.env['res.lang'].get_installed()
        return languages

    @route(['/selected/language'], type='json', auth='public')
    def user_selected_language(self, selected_language):
        """
        To switch the user language
        :param selected_language: string of language short code
        """
        request.env.user.lang = selected_language

    @route(['/render/theme/view/data'], type='json', auth='user')
    def render_theme_view_settings(self, pl_setting_scope, pl_rec_id=None):
        """
        Function to return theme setting data for company/global to visible current company/global setting on the form
        view.
        :param pl_setting_scope:
        :return:
        """
        pl_origin_data = False
        pl_domain = []
        values = {}
        pl_all_setting_scope = request.env['pl.global.config'].pl_get_config_values()
        if pl_setting_scope == 'User':
            user = request.env.user
            obj_list = {
                'global': request.env.ref('pl_curved_backend_theme.pl_global_config_single_rec'),
                'company': user.company_id,
                'user': request.env.user
            }
            values = self.pl_get_values(pl_all_setting_scope, user, pl_setting_scope)
            pl_domain = [('pl_user', '=', user.id)]

            pl_color_theme = False
            if pl_all_setting_scope['scope_pl_colors_theme'] == 'User':
                pl_color_theme = request.env(su=True)['pl.color.theme'].get_theme(scope=pl_setting_scope, origin=user)
            values.update({
                'pl_sun_time_info': self.pl_get_suntime_info(),
                'pl_dark_mode': user.pl_dark_mode,
                'pl_auto_dark_mode': self.pl_get_dark_mode(),
                'pl_menubar_autohide': user.pl_menubar_autohide,
                'pl_favtbar_autohide': user.pl_favtbar_autohide,
                'pl_favtbar_position': user.pl_favtbar_position,
                'pl_show_app_name': user.pl_show_app_name,
                'pl_user_menu_placement': user.pl_user_menu_placement,
                'pl_manager_role': user.has_group('pl_curved_backend_theme.pl_curved_theme_settings'),
                'pl_global_config_id': request.env.ref('pl_curved_backend_theme.pl_global_config_single_rec').id,
                'pl_body_background_img': self.pl_get_background_data(pl_domain, 'pl.body.background'),
                'pl_app_drawer_background_img': self.pl_get_background_data(pl_domain, 'pl.drawer.background'),
                'pl_body_background_opacity': obj_list[
                    pl_all_setting_scope.get('scope_pl_body_background').lower()].pl_body_background_opacity,
                'pl_app_drawer_background_opacity': user.pl_app_drawer_background_opacity,
                'pl_body_background_image_enable': obj_list[
                    pl_all_setting_scope.get('scope_pl_body_background').lower()].pl_body_background_image_enable,
                'pl_color_theme': pl_color_theme,
            })

            # Update currently active menu bar
            pl_current_menu_bar_scope = pl_all_setting_scope['scope_pl_menu_bar']
            if pl_current_menu_bar_scope == 'Global':
                pl_origin_data = request.env.ref('pl_curved_backend_theme.pl_global_config_single_rec')
                pl_new_values = self.pl_get_values({'scope_pl_menu_bar': pl_current_menu_bar_scope}, pl_origin_data,
                                                   pl_current_menu_bar_scope)
                values.update({'pl_current_menu_bar': pl_new_values.get('pl_menu_bar')})
            elif pl_current_menu_bar_scope == 'Company':
                pl_origin_data = request.env.user.company_id
                pl_new_values = self.pl_get_values({'scope_pl_menu_bar': pl_current_menu_bar_scope}, pl_origin_data,
                                                   pl_current_menu_bar_scope)
                values.update({'pl_current_menu_bar': pl_new_values.get('pl_menu_bar')})
            elif pl_current_menu_bar_scope == 'User':
                values.update({'pl_current_menu_bar': values.get('pl_menu_bar')})

        if pl_setting_scope == 'Company':
            pl_origin_data = request.env['res.company'].browse(pl_rec_id)
            pl_domain = [('pl_company', '=', pl_origin_data.id)]
            values = self.pl_get_values(pl_all_setting_scope, pl_origin_data, pl_setting_scope)
        if pl_setting_scope == 'Global':
            pl_origin_data = request.env.ref('pl_curved_backend_theme.pl_global_config_single_rec')
            pl_domain = [('pl_global', '=', True)]
            values = self.pl_get_values(pl_all_setting_scope, pl_origin_data, pl_setting_scope)

        # Only for company and global since user have different value of dictionary.
        # User needs to have different dictionary since it needs to manage hide and show tabs for settings based on
        # the scope.
        if pl_setting_scope in ['Company', 'Global']:
            pl_color_theme = False
            if (pl_all_setting_scope['scope_pl_colors_theme'] == 'Company' and pl_setting_scope == 'Company') or (
                    pl_setting_scope == 'Global'):
                pl_color_theme = request.env(su=True)['pl.color.theme'].get_theme(scope=pl_setting_scope,
                                                                                  origin=pl_origin_data)
            values.update({
                'pl_body_background_opacity': pl_origin_data.pl_body_background_opacity,
                'pl_app_drawer_background_opacity': pl_origin_data.pl_app_drawer_background_opacity,
                'pl_website_title_enable': pl_origin_data.pl_website_title_enable,
                'pl_company_logo_enable': pl_origin_data.pl_company_logo_enable,
                'pl_small_company_logo': self.pl_get_image_url(pl_origin_data.pl_small_company_logo),
                'pl_body_background_img': self.pl_get_background_data(pl_domain, 'pl.body.background'),
                'pl_app_drawer_background_img': self.pl_get_background_data(pl_domain, 'pl.drawer.background'),
                'pl_color_theme': pl_color_theme,
                'pl_body_background_image_enable': pl_origin_data.pl_body_background_image_enable,
            })
            if 'pl_company_logo' in values:
                values.update({
                    'pl_company_logo': self.pl_get_image_url(pl_origin_data.pl_company_logo)
                })

        if pl_setting_scope == 'Global':
            values['pl_enterprise_apps'] = pl_origin_data.pl_enterprise_apps
            values['pl_breadcrumb_style'] = pl_origin_data.pl_breadcrumb_style
            values['pl_login_page_logo_enable'] = pl_origin_data.pl_login_page_logo_enable
            values['pl_login_page_logo_image'] = self.pl_get_image_url(pl_origin_data.pl_login_page_logo)
            values['pl_color_theme_scope'] = pl_all_setting_scope['scope_pl_colors_theme']
            values['pl_login_page_style'] = pl_origin_data.pl_login_page_style
            values['pl_login_background_color'] = request.env['pl.login.background.color'].search_read([])
            values['pl_login_background_image'] = self.pl_get_login_background_img()
        return values

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

    def pl_get_login_background_img(self):
        result = []
        for rec in request.env['pl.login.background.image'].search([]):
            result.append(
                {
                    'id': rec.id,
                    'pl_image': self.pl_get_image_url(rec.pl_image),
                    'pl_active': rec.pl_active
                }
            )
        return result

    def pl_get_values(self, pl_all_setting_scope, pl_origin, pl_current_scope):
        """
        Function to get values to render on the page.
        :param pl_all_setting_scope: all setting scopes.
        :param pl_origin: origin of the data.
        :param pl_current_scope: current scope.
        :return: values to render on the page.
        """
        values = dict()
        for key, value in pl_all_setting_scope.items():
            if value == pl_current_scope and key.split('scope_')[1] in pl_origin:
                values[key.split('scope_')[1]] = pl_origin[key.split('scope_')[1]] if pl_origin[
                    key.split('scope_')[1]] else True

                # Handle boolean field
                if key == 'scope_pl_favorite_bar':
                    values[key.split('scope_')[1]] = pl_origin[key.split('scope_')[1]]
                if key == 'scope_pl_click_edit':
                    values[key.split('scope_')[1]] = pl_origin[key.split('scope_')[1]]
        return values

    def pl_get_background_data(self, pl_domain, pl_model):
        """
        Function to return the body background data based on the scope for global, companies, and users.
        :param pl_domain:
        :return:
        """
        pl_body_background_img = []
        for pl_background in request.env[pl_model].search(
                pl_domain):
            pl_body_background_img.append({
                'id': str(pl_background.id),
                'pl_active': pl_background.pl_active,
                'value': self.pl_get_image_url(pl_background.pl_image)
            })
        return pl_body_background_img

    @route(['/pl_curved_backend_theme/save/split_data'], type='json', auth='user')
    def pl_save_split_data(self, val):
        request.env.user.write({
            'pl_split_view': val
        })
        return True

    @route(['/pl_curved_backend_theme/add/images'], type='json', auth='user')
    def pl_add_background_images(self, image_info=False, scope=False, company_id=False):
        # Save data.
        if image_info.get('key') and image_info.get('value'):
            pl_image_model = {
                'pl_body_background_img': 'pl.body.background',
                'pl_app_drawer_background_img': 'pl.drawer.background'
            }
            vals = {'pl_image': image_info['value']}
            if scope == 'user':
                vals['pl_user'] = request.env.user.id
            if scope == 'company':
                vals['pl_company'] = company_id
            if scope == 'global':
                vals['pl_global'] = True
            request.env[pl_image_model[image_info['key']]].create(vals)

        # Get background image data
        pl_domain = []
        pl_template_data = dict()
        if scope == 'user':
            pl_domain = [('pl_user', '=', request.env.user.id)]
        if scope == 'company':
            pl_domain = [('pl_company', '=', company_id)]
            if image_info.get('key') == 'pl_body_background_img':
                pl_template_data['pl_image_for'] = 'pl_body_background_company'
                pl_template_data['pl_image_save'] = 'pl_body_background_img'
                pl_template_data['pl_image_del'] = 'pl_body_background_del_company'
            if image_info.get('key') == 'pl_app_drawer_background_img':
                pl_template_data['pl_image_for'] = 'pl_app_drawer_background_company'
                pl_template_data['pl_image_save'] = 'pl_app_drawer_background_img'
                pl_template_data['pl_image_del'] = 'pl_drawer_background_company_del'
        if scope == 'global':
            pl_domain = [('pl_global', '=', True)]
            if image_info.get('key') == 'pl_body_background_img':
                pl_template_data['pl_image_for'] = 'pl_body_background_global'
                pl_template_data['pl_image_save'] = 'pl_body_background_img'
                pl_template_data['pl_image_del'] = 'pl_body_background_del_global'
            if image_info.get('key') == 'pl_app_drawer_background_img':
                pl_template_data['pl_image_for'] = 'pl_app_drawer_background_global'
                pl_template_data['pl_image_save'] = 'pl_app_drawer_background_img'
                pl_template_data['pl_image_del'] = 'pl_drawer_background_global_del'
        return self.pl_get_background_data(pl_domain, pl_image_model[image_info['key']])

    @route(['/pl_curved_backend_theme/add/login/images'], type='json', auth='user')
    def pl_add_login_background_images(self, image_info=False):
        # Save data.
        if image_info.get('key') and image_info.get('value'):
            request.env['pl.login.background.image'].create({'pl_image': image_info['value']})
        return self.pl_get_login_background_img()

    @route(['/pl_curved_backend_theme/add/login/color'], type='json', auth='user')
    def pl_add_login_background_colors(self, data=False):
        # Save data.
        if data.get('value'):
            request.env['pl.login.background.color'].create({'pl_color': data['value']})
        return request.env['pl.login.background.color'].search_read([])

    @route(['/save/theme/settings'], type='json', auth='user')
    def save_theme_settings(self, **post):
        """
        Save the settings of Theme
        :param post: dict of field and its value
        """

        # pl_no_check_field have special functionality to write/create data in other models.
        pl_no_check_field = ['pl_body_background_img', 'pl_app_drawer_background_img']
        pl_login_page_fields = ["pl_login_background_image_save", "pl_login_background_setting"]
        pl_theme_fields = ["pl_body_background",
                           "pl_menu",
                           "pl_menu_hover",
                           "pl_button",
                           "pl_border",
                           "pl_heading",
                           "pl_link",
                           "pl_primary_color",
                           "pl_tooltip"]
        pl_image_model = {
            'pl_body_background_img': 'pl.body.background',
            'pl_app_drawer_background_img': 'pl.drawer.background'
        }
        pl_background_data = {}
        pl_background_domain = []
        pl_splitter = ''

        pl_origin_obj = False
        if post.get('pl_origin_scope') == 'user':
            # if setting is changed then active and de-active the templates.
            pl_origin_obj = request.env.user
            pl_background_data['pl_user'] = pl_origin_obj.id
            pl_background_domain = [('pl_user', '=', pl_origin_obj.id)]
            pl_color_theme_domain = [('pl_user', '=', pl_origin_obj.id), ('pl_active', '=', True)]

        if post.get('pl_origin_scope') == 'company':
            pl_origin_obj = request.env['res.company'].browse(post['record_id'])
            pl_splitter = '_company'
            pl_background_data['pl_company'] = pl_origin_obj.id
            pl_background_domain = [('pl_company', '=', pl_origin_obj.id)]
            pl_color_theme_domain = [('pl_company', '=', pl_origin_obj.id), ('pl_active', '=', True)]

        if post.get('pl_origin_scope') == 'global':
            pl_origin_obj = request.env.ref('pl_curved_backend_theme.pl_global_config_single_rec')
            pl_splitter = '_global'
            pl_background_data['pl_global'] = True
            pl_background_domain = [('pl_global', '=', True)]
            pl_color_theme_domain = [('pl_global', '=', True), ('pl_active', '=', True)]

        for key, value in post.get('pl_unsaved_setting').items():
            # check for special field data need to update or create new data on its model.
            if key in pl_no_check_field:
                if type(value) is int:
                    # Need to de-active other background and active selected image.
                    for pl_background in request.env[pl_image_model[key]].search(pl_background_domain):
                        if pl_background.id == value:
                            pl_background.write({'pl_active': True})
                        else:
                            pl_background.write({'pl_active': False})
                else:
                    pl_background_data['pl_image'] = value
                    request.env[pl_image_model[key]].create(pl_background_data)
            elif key in pl_login_page_fields:
                # De-active all image and color first.
                request.env['pl.login.background.image'].search([]).write({'pl_active': False})
                request.env['pl.login.background.color'].search([]).write({'pl_active': False})
                # Active login page background based on image or color.
                if key == "pl_login_background_image_save":
                    pl_rec = request.env['pl.login.background.image'].search([('id', '=', value)])
                    if pl_rec:
                        pl_rec.pl_active = True

                # Active login page background based on color.
                if key == "pl_login_background_setting" and value:
                    pl_rec = request.env['pl.login.background.color'].search([('id', '=', value)])
                    if pl_rec:
                        pl_rec.pl_active = True

            elif pl_splitter and pl_splitter in key:
                if key.rsplit(pl_splitter, 1)[0] not in pl_theme_fields:
                    pl_origin_obj[key.rsplit(pl_splitter, 1)[0]] = value
            elif key:
                pl_origin_obj[key] = value

            # Manage theme colors active.
            if key == 'pl_theme_color':
                # de-active current theme
                pl_current_theme = request.env['pl.color.theme'].sudo().search(pl_color_theme_domain)
                for rec in pl_current_theme:
                    rec.write({'pl_active': False})
                # active new theme
                pl_new_theme = request.env['pl.color.theme'].sudo().search([('id', '=', value)], limit=1)
                if pl_new_theme:
                    pl_new_theme.write({'pl_active': True})

        # Hide or show enterprise apps.
        if 'pl_enterprise_apps' in post['pl_unsaved_setting']:
            request.env.ref('pl_curved_backend_theme.pl_curved_theme_hide_enterprise_apps').write({
                'active': post['pl_unsaved_setting'].get('pl_enterprise_apps')
            })

    @route(['/pl_list_renderer/attachments'], type='json', auth='user')
    def pl_list_render(self, **kw):
        """
        Fetches the details of attachments of all renderd records in List View.
        :param kw: {res_ids, model}
        :return: values {rec_id:[{att_id, att_name, att_mime}]}
        """
        tree_view_ids = kw.get('res_ids')
        tree_view_model = kw.get('model')

        # Handle do action from js
        tree_view_domain = kw.get('domain')
        pl_domain = []
        for view_domain in tree_view_domain:
            if type(view_domain) is list:
                pl_domain.append(tuple(view_domain))
            else:
                pl_domain.append(view_domain)
        if not tree_view_ids:
            tree_view_ids = request.env[tree_view_model].sudo().search(pl_domain).ids

        values = {}
        for tree_view_rec_id in tree_view_ids:
            attachment_ids = False
            # Check if tree_view_rec_id is integer.
            if type(tree_view_rec_id) is int:
                attachment_ids = request.env['ir.attachment'].search(
                    [('res_model', '=', tree_view_model), ('res_id', '=', tree_view_rec_id)]).ids
            if attachment_ids:
                values.update({tree_view_rec_id: ''})
                for attachment_id in attachment_ids:
                    data = request.env['ir.attachment'].browse(attachment_id)
                    if data:
                        if len(values.get(tree_view_rec_id)):
                            values[tree_view_rec_id].append({
                                'att_id': data.id,
                                'att_name': data.display_name,
                                'att_mime': data.mimetype
                            })
                        else:
                            values[tree_view_rec_id] = [{
                                'att_id': data.id,
                                'att_name': data.display_name,
                                'att_mime': data.mimetype
                            }]
        data = [values]
        list_density = {'pl_list_density': request.env.user.pl_list_density}
        data.append(list_density)

        # Append checkbox style for tree view.
        data.append({'pl_checkbox_style': self.pl_get_checkbox_style()})
        return data

    @route(['/pl_app_frequency/update'], type='json', auth='user')
    def pl_app_frequency_update(self, **kw):
        """
        To update the frequency of apps as per users
        :param kw: dict containing Primary Menu id
        """
        menu_id = kw['menu_id']
        user_id = request.env.user
        if menu_id in user_id.pl_frequency_menu.pl_menu_id.ids:
            menu = user_id.pl_frequency_menu.search([('pl_menu_id', '=', menu_id), ('pl_user_id', '=', user_id.id)], limit=1)
            menu.pl_frequency = menu.pl_frequency + 1
        else:
            vals = {
                'pl_frequency': 1,
                'pl_user_id': user_id.id,
                'pl_menu_id': menu_id,
            }
            user_id.pl_frequency_menu.create(vals)

    @route(['/pl_app_frequency/render'], type='json', auth='user')
    def pl_app_frequency_render(self):
        """
        Render the list of frequently used menus
        :return: dict of top12 frequently used app by user
        """
        user_id = request.env.user
        menu_ids = user_id.pl_frequency_menu.search_read([('pl_user_id', '=', user_id.id)], ['pl_menu_id'], limit=12,
                                                         order='pl_frequency desc')
        return [menu['pl_menu_id'][0] for menu in menu_ids]

    # Todo: If no use then remove this function.
    @route(['/pl_curved_theme/checkbox/get'], type='json', auth='user')
    def pl_get_checkbox_style(self):
        """
        Controller to return list of selected checkbox style.
        :return:
        """

        user = request.env.user
        return user.pl_checkbox_style

    def pl_get_suntime_info(self):
        """
        Function to return sun-time info.
        :return: sun-time info
        """
        pl_current_user = request.env.user
        pl_sunrise_hour = pl_current_user.pl_sunrise_hour
        pl_sunrise_min = pl_current_user.pl_sunrise_min
        pl_sunset_hour = pl_current_user.pl_sunset_hour
        pl_sunset_min = pl_current_user.pl_sunset_min
        if pl_sunset_hour or pl_sunset_min:
            return {
                'sunrise': str(pl_sunrise_hour) + ":" + str(pl_sunrise_min) + ":00",
                'sunset': str(pl_sunset_hour) + ":" + str(pl_sunset_min) + ":00"
            }
        return False

    @route(['/pl_curved_theme/get_fav_icons'], type='json', auth='user')
    def pl_get_fav_icons(self, pl_app_icons):
        for rec in pl_app_icons:
            pl_domain = [
                ('pl_ir_ui_menu', '=', rec.get('id')),
                ('pl_fav_app', '=', True),
                ('pl_users', '=', request.env.user.id)
            ]
            pl_is_fav_app = request.env['pl.fav.menu'].search(pl_domain)
            rec['pl_fav_app'] = False
            if pl_is_fav_app:
                rec['pl_fav_app'] = True
        return pl_app_icons

    @route(['/pl_curved_theme/set_fav_icons'], type='json', auth='user')
    def pl_set_fav_icons(self, pl_app_id):
        pl_app_id = int(pl_app_id)
        pl_domain = [
            ('pl_ir_ui_menu', '=', pl_app_id),
            ('pl_fav_app', '=', False),
            ('pl_users', '=', request.env.user.id)
        ]
        pl_is_fav_app = request.env['pl.fav.menu'].search(pl_domain)

        if pl_is_fav_app:
            pl_is_fav_app.write({'pl_fav_app': True})
            return True
        else:
            res = pl_is_fav_app.create(
                {
                    'pl_fav_app': True,
                    'pl_ir_ui_menu': pl_app_id,
                    'pl_users': request.env.user.id
                }
            )
            return True

    @route(['/pl_curved_theme/rmv_fav_icons'], type='json', auth='user')
    def pl_rmv_fav_icons(self, pl_app_id):
        pl_app_id = int(pl_app_id)
        pl_domain = [
            ('pl_ir_ui_menu', '=', pl_app_id),
            ('pl_fav_app', '=', True),
            ('pl_users', '=', request.env.user.id)
        ]
        pl_is_fav_app = request.env['pl.fav.menu'].search(pl_domain)

        if pl_is_fav_app:
            pl_is_fav_app.write({'pl_fav_app': False})
            return True
        else:
            pl_is_fav_app.create(
                {
                    'pl_fav_app': False,
                    'pl_ir_ui_menu': pl_app_id,
                    'pl_users': request.env.user.id
                }
            )
            return True

    @route(['/pl_curved_theme/pl_get_website_title'], type='json', auth='public')
    def pl_get_website_title(self, **post):
        pl_origin = request.env.ref('pl_curved_backend_theme.pl_global_config_single_rec')
        pl_scope_value = pl_origin.scope_pl_website_title
        if pl_scope_value == 'Company':
            pl_origin = request.env.user.company_id
        # check if website title is enabled
        if pl_origin.pl_website_title_enable:
            return pl_origin.pl_website_title
        return 'Odoo'

    @route(['/pltheme/background/default'], type='json', auth='user')
    def set_background_default(self, pl_setting_scope, pl_rec_id=None, pl_default_info=None):
        if pl_setting_scope == 'Global' and pl_default_info:
            pl_global_obj = request.env.ref('pl_curved_backend_theme.pl_global_config_single_rec')
            # uncheck background color.
            pl_global_obj[pl_default_info['field']] = False
            pl_global_obj[pl_default_info['field'] + '_opacity'] = 1
            # pl_global_obj.pl_body_background = False

            # de-active background image.
            pl_sel_background = request.env[pl_default_info['model']].search(
                [('pl_global', '=', True), ('pl_active', '=', True)], limit=1)
            if pl_sel_background:
                pl_sel_background.pl_active = False

        if pl_setting_scope == 'User' and pl_default_info:
            pl_user_obj = request.env.user
            pl_user_obj[pl_default_info['field']] = False
            pl_user_obj[pl_default_info['field'] + '_opacity'] = 1

            # de-active background image.
            pl_sel_background = request.env[pl_default_info['model']].search(
                [('pl_user', '=', pl_user_obj.id), ('pl_active', '=', True)], limit=1)
            if pl_sel_background:
                pl_sel_background.pl_active = False

        if pl_setting_scope == 'Company' and pl_rec_id and pl_default_info:
            pl_company_obj = request.env['res.company'].browse(pl_rec_id)
            # uncheck background color.
            pl_company_obj[pl_default_info['field']] = False
            pl_company_obj[pl_default_info['field'] + '_opacity'] = 1

            # de-active background image.
            pl_sel_background = request.env[pl_default_info['model']].search(
                [('pl_company', '=', pl_company_obj.id), ('pl_active', '=', True)], limit=1)
            if pl_sel_background:
                pl_sel_background.pl_active = False

    def pl_get_dark_mode(self):
        pl_current_user = request.env.user
        pl_sunset_hour = pl_current_user.pl_sunset_hour
        pl_sunset_min = pl_current_user.pl_sunset_min
        if pl_sunset_hour or pl_sunset_min:
            return pl_current_user.pl_auto_dark_mode
        return False

    @http.route('/pl_curved_backend_theme/getTheme', type='json', auth="user")
    def pl_get_theme(self):
        pl_color_theme_scope = request.env['pl.global.config'].pl_get_field_scope(['scope_pl_colors_theme'])
        pl_scope = pl_color_theme_scope[0].get('scope_pl_colors_theme')
        if pl_scope == 'User':
            pl_origin_obj = request.env.user
            pl_color_theme_domain = [('pl_user', '=', pl_origin_obj.id), ('pl_active', '=', True)]
        if pl_scope == 'Company':
            pl_origin_obj = request.env.user.sudo().company_id
            pl_color_theme_domain = [('pl_company', '=', pl_origin_obj.id), ('pl_active', '=', True)]
        if pl_scope == 'Global':
            pl_origin_obj = request.env.ref('pl_curved_backend_theme.pl_global_config_single_rec')
            pl_color_theme_domain = [('pl_global', '=', True), ('pl_active', '=', True)]

        pl_current_theme_data = request.env['pl.color.theme'].sudo().search(pl_color_theme_domain, limit=1)
        if pl_current_theme_data:
            return {
                'primary': pl_current_theme_data.pl_primary_color,
                'body-background': pl_current_theme_data.pl_body_background,
                'nav-link-color': pl_current_theme_data.pl_menu,
                'pl-over-link': pl_current_theme_data.pl_menu_hover,
                'tab-bg': pl_current_theme_data.pl_border,
                'primary-btn': pl_current_theme_data.pl_button,
                'heading-color': pl_current_theme_data.pl_heading,
                'link-color': pl_current_theme_data.pl_link,
                'tooltip-heading-bg': pl_current_theme_data.pl_tooltip,
                'default_theme': pl_current_theme_data.pl_default
            }
        return {
            'primary': '#141CBA',
            'body-background': '#ffffff',
            'nav-link-color': '#454546',
            'pl-over-link': '#f5f5f5',
            'tab-bg': '#ffffff',
            'primary-btn': '#141CBA',
            'heading-color': '#141CBA',
            'link-color': '#141CBA',
            'tooltip-heading-bg': '#dee2e6',
            'default_theme': True
        }


class PlHome(Home):
    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, *args, **kw):
        request.params['pl_login_background'] = self.pl_get_login_page_image()
        request.params['pl_login_layout'] = self.pl_get_login_page_layout()
        if not request.session.uid:
            request.uid = request.env.ref('base.public_user').id
        pl_login_logo = self.pl_get_login_page_logo()
        if pl_login_logo:
            request.params['pl_login_logo'] = pl_login_logo
        res = super(PlHome, self).web_login(redirect=redirect, *args, **kw)
        # login_status = request.params['login_success']
        # if login_status:
        #     request.env.user.partner_id.pl_set_sunrise_sunset_time()
        return res

    def pl_get_login_page_image(self):
        """
        Function to return login page background image and color.
        :return:
        """

        pl_global_obj = request.env.ref('pl_curved_backend_theme.pl_global_config_single_rec')
        # pl_back_img = pl_global_obj.sudo().pl_login_background_image

        # check for active login page image.
        pl_check_active_image = request.env['pl.login.background.image'].search([('pl_active', '=', True)], limit=1)
        if pl_check_active_image:
            return {
                'type': 'image',
                'background-img': self.pl_get_image_url(pl_check_active_image.pl_image)
            }

        # check for active login page color.
        pl_check_active_color = request.env['pl.login.background.color'].search([('pl_active', '=', True)], limit=1)
        if pl_check_active_color:
            return {
                'type': 'color',
                'background-color': pl_check_active_color.pl_color
            }
        # if pl_global_obj.sudo().pl_login_background_image_enable and pl_back_img:
        #     return {
        #         'background-img': self.pl_get_image_url(pl_back_img),
        #         'background-opacity': pl_global_obj.sudo().pl_login_back_image_opacity
        #     }
        return False

    def pl_get_login_page_layout(self):
        pl_global_obj = request.env.ref('pl_curved_backend_theme.pl_global_config_single_rec')
        return pl_global_obj.sudo().pl_login_page_style

    def pl_get_login_page_logo(self):
        pl_global_obj = request.env.ref('pl_curved_backend_theme.pl_global_config_single_rec').sudo()
        if pl_global_obj.pl_login_page_logo_enable:
            return self.pl_get_image_url(pl_global_obj.pl_login_page_logo)
        return False

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


class PlAuthSignupHome(AuthSignupHome):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        request.params['pl_login_background'] = self.pl_get_login_page_image()
        request.params['pl_login_layout'] = self.pl_get_login_page_layout()
        request.params['pl_login_logo'] = self.pl_get_login_page_logo()
        return super(PlAuthSignupHome, self).web_auth_signup(*args, **kw)

    @http.route('/web/reset_password', type='http', auth='public', website=True, sitemap=False)
    def web_auth_reset_password(self, *args, **kw):
        request.params['pl_login_background'] = self.pl_get_login_page_image()
        request.params['pl_login_layout'] = self.pl_get_login_page_layout()
        request.params['pl_login_logo'] = self.pl_get_login_page_logo()
        return super(PlAuthSignupHome, self).web_auth_reset_password(*args, **kw)

    def pl_get_login_page_image(self):
        """
        Function to return login page background image and color.
        :return:
        """

        pl_global_obj = request.env.ref('pl_curved_backend_theme.pl_global_config_single_rec')
        # pl_back_img = pl_global_obj.sudo().pl_login_background_image

        # check for active login page image.
        pl_check_active_image = request.env['pl.login.background.image'].search([('pl_active', '=', True)], limit=1)
        if pl_check_active_image:
            return {
                'type': 'image',
                'background-img': self.pl_get_image_url(pl_check_active_image.pl_image)
            }

        # check for active login page color.
        pl_check_active_color = request.env['pl.login.background.color'].search([('pl_active', '=', True)], limit=1)
        if pl_check_active_color:
            return {
                'type': 'color',
                'background-color': pl_check_active_color.pl_color
            }
        # if pl_global_obj.sudo().pl_login_background_image_enable and pl_back_img:
        #     return {
        #         'background-img': self.pl_get_image_url(pl_back_img),
        #         'background-opacity': pl_global_obj.sudo().pl_login_back_image_opacity
        #     }
        return False

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

    def pl_get_login_page_layout(self):
        pl_global_obj = request.env.ref('pl_curved_backend_theme.pl_global_config_single_rec')
        return pl_global_obj.sudo().pl_login_page_style

    def pl_get_login_page_logo(self):
        pl_global_obj = request.env.ref('pl_curved_backend_theme.pl_global_config_single_rec').sudo()
        if pl_global_obj.pl_login_page_logo_enable:
            return self.pl_get_image_url(pl_global_obj.pl_login_page_logo)
        return False
