# -*- coding: utf-8 -*-

import json
import pytz

from odoo import http
from odoo.addons.http_routing.models.ir_http import url_for
from odoo.http import request
from odoo.tools import ustr
from odoo.modules.module import get_module_resource


class PlPwaController(http.Controller):

    @http.route('/pl_curved_backend_theme/get_manifest', type='json', auth='public', sitemap=False)
    def pl_get_pwa_manifest(self):
        pl_enable_pwa_app = request.env['ir.config_parameter'].sudo().get_param(
            'pl_curved_backend_theme.pl_enable_pwa_app')
        if not pl_enable_pwa_app:
            return False
        pl_pwa_name = request.env['ir.config_parameter'].sudo().get_param('pl_curved_backend_theme.pl_pwa_name')
        pl_pwa_background_color = request.env['ir.config_parameter'].sudo().get_param(
            'pl_curved_backend_theme.pl_pwa_background_color')
        pl_pwa_theme_color = request.env['ir.config_parameter'].sudo().get_param(
            'pl_curved_backend_theme.pl_pwa_theme_color')
        port = request.httprequest.host_url.split('://')[1]

        manifest = {'name': pl_pwa_name, 'short_name': pl_pwa_name, 'description': pl_pwa_name,
                    # 'start_url': request.httprequest.host_url + 'web/', 'display': 'standalone',
                    'start_url': 'https://' + port + 'web/', 'display': 'standalone',
                    'background_color': pl_pwa_background_color,
                    'id': "/?db=" + request.db,
                    'theme_color': pl_pwa_theme_color, 'icons': self.pl_get_image_url()}
        return manifest

    @http.route('/pl_curved_backend_theme/get/sw.js', type='http', auth='public', methods=['GET'], sitemap=False)
    def pl_get_service_worker(self):
        sw_file = get_module_resource('pl_curved_backend_theme', 'static/src/js/sw.js')
        with open(sw_file, 'r') as fp:
            body = fp.read()
        response = request.make_response(body, [
            ('Content-Type', 'text/javascript'),
            ('Service-Worker-Allowed', url_for('/web/')),
        ])
        return response

    def pl_get_image_url(self):
        pl_icons = []
        for size in [(72, 72), (96, 96), (128, 128), (144, 144), (152, 152), (192, 192), (256, 256), (384, 384),
                     (512, 512)]:
            pl_url = '/pl_curved_backend_theme/logo/icon_' + str(size[0]) + '_' + request.db
            pl_pwa_icons = request.env["ir.attachment"].sudo().search(
                [('url', 'like', pl_url)], limit=1)

            # Condition to solve the problem for pwa already have the icon with old url.
            if not pl_pwa_icons:
                pl_url = '/pl_curved_backend_theme/logo/icon_' + str(size[0])
                pl_pwa_icons = request.env["ir.attachment"].sudo().search(
                    [('url', 'like', pl_url)], limit=1)

            if pl_pwa_icons:
                pl_icons.append({
                    "src": 'data:image/png;base64,'+pl_pwa_icons.datas.decode("utf-8"),
                    "sizes": str(size[0]) + 'x' + str(size[1]),
                    "type": "image/png"
                })
        return pl_icons
