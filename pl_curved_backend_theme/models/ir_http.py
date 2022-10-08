from odoo import models
from odoo.http import request


class PlIrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super(PlIrHttp, self).session_info()
        if request.env.user.has_group('base.group_user'):
            result['pl_breadcrumb_style'] = request.env.ref('pl_curved_backend_theme.pl_global_config_single_rec').pl_breadcrumb_style
            result['pl_splitted_vertical_width'] = request.env.user.pl_split_vertical_list_width
            result['pl_splitted_horizontal_height'] = request.env.user.pl_split_horizontal_list_height
            result['pl_split_view'] = request.env.user.pl_split_view
            result['show_effect'] = request.env['ir.config_parameter'].sudo().get_param('base_setup.show_effect')
            result['pl_form_view_width'] = request.env.user.pl_form_page_width if request.env.user.pl_form_page_width else False
            result['pl_lang_direction'] = request.env['res.lang']._lang_get(request.env.user.lang).direction
            pl_all_setting_scope = request.env['pl.global.config'].sudo().pl_get_config_values()
            if pl_all_setting_scope.get('scope_pl_loaders', '').lower() == 'global':
                result['pl_current_loader'] = self.sudo().env.ref('pl_curved_backend_theme.pl_global_config_single_rec')['pl_loaders']
            elif pl_all_setting_scope.get('scope_pl_loaders', '').lower() == 'company':
                result['pl_current_loader'] = self.sudo().env.user.company_id.pl_loaders
            else:
                result['pl_current_loader'] = self.sudo().env.user.pl_loaders
        return result
