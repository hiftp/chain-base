
from collections import deque
import json
import logging

from odoo import http, fields
from odoo.http import request

# from ..models.formio_builder import \
#     STATE_CURRENT as BUILDER_STATE_CURRENT, STATE_OBSOLETE as BUILDER_STATE_OBSOLETE
#
# from ..models.formio_form import \
#     STATE_PENDING as FORM_STATE_PENDING, STATE_DRAFT as FORM_STATE_DRAFT, \
#     STATE_COMPLETE as FORM_STATE_COMPLETE, STATE_CANCEL as FORM_STATE_CANCEL

_logger = logging.getLogger(__name__)


class FormController(http.Controller):

    @http.route('/form/form/<string:form_id>', type='http', auth='user',
                website=True)
    def form_root(self, form_id, **kwargs):
        form = request.env['formio.form'].sudo().search(
            [('id', '=', form_id)])
        if not form:
            msg = 'Form Not Found!!'
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