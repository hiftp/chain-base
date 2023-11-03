# -*- coding: utf-8 -*-

import qrcode
import io
import base64
from werkzeug.wrappers import Request, Response
import os

from odoo import http, tools, modules, _
from odoo.http import Controller, request, route


class DocumentationController(http.Controller):

    @http.route([
        '/documentation/<string:version>/<path:file_name>',
    ], methods=['GET'], type='http', auth='public')
    def redirect_to_doc(self, file_name, version='16.0'):
        # todo: 当前不处理多语言，因为会将 path 和 lang 混。后续 取所有语言，然后再判断
        module_path = modules.get_module_path('app_odoo_doc', display_warning=False)
            
        if module_path:
            base_url_doc = request.httprequest.full_path
            if base_url_doc.endswith('?'):
                base_url_doc = base_url_doc[:-1]
            # 当前只处理 英文
            user_lang = False
            if request.session.uid:
                user_lang = request.env['res.users'].sudo().browse(request.session.uid).partner_id.lang
            if user_lang and file_name.startswith(user_lang):
                base_url_doc = base_url_doc.replace(('/%s' % user_lang), '')
                return request.redirect(base_url_doc, 303)
        #     todo: 当前直接303转资源
        return request.redirect('/app_odoo_doc/static%s' % base_url_doc, 303)
    
    # @http.route('/app/get_url_qrcode', type='http', auth="public")
    # def get_url_qrcode(self, url, **kw):
    #     qr = qrcode.QRCode(version=1,
    #                        error_correction=qrcode.constants.ERROR_CORRECT_L,
    #                        box_size=10,
    #                        border=1)
    #     qr.add_data(url)
    #     qr.make(fit=True)
    #
    #     image = qr.make_image(fill_color="black", back_color="white")
    #     # 将图片数据转换为 base64 编码
    #     buffered = io.BytesIO()
    #     image.save(buffered, format="PNG")
    #     image_data = base64.b64encode(buffered.getvalue()).decode()
    #
    #     return image_data
