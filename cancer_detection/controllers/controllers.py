# -*- coding: utf-8 -*-
from odoo import http
import json

class CancerDetection(http.Controller):
    @http.route('/cancer_types', auth='public', methods=['POST','GET'], csrf=False)
    def types(self, **post):
        partner_scan_model = http.request.env['ir.model'].sudo().search([('model', '=', 'partner.scan')]).id
        cancer_types = http.request.env['ir.model.fields'].sudo().search([('model_id','=',partner_scan_model), ('name', '=', 'cancer_type')]).selection_ids.mapped('value')
        return json.dumps(cancer_types)


    @http.route('/file_types', auth='public', methods=['POST','GET'], csrf=False)
    def file_types(self, **post):
        partner_scan_model = http.request.env['ir.model'].sudo().search([('model', '=', 'partner.scan')]).id
        file_types = http.request.env['ir.model.fields'].sudo().search([('model_id','=',partner_scan_model), ('name', '=', 'file_type')]).selection_ids.mapped('value')
        return json.dumps(file_types)

    @http.route('/create_scan', auth='public', methods=['POST'], csrf=False)
    def create_scan(self, **post):
        login = post.get("login")
        password = post.get("password")
        actual_user = http.request.env['res.users'].sudo().search([('login', '=', login)])
        if not actual_user:
            return json.dumps({'error': 'User not found'})
        if actual_user.x_portal_password != password:
            return json.dumps({'error': 'Wrong password'})
        cancer_type = post.get("cancer_type")
        file_type = post.get("file_type")
        patient_name = post.get("patient_name")
        scan_file = post.get("scan_file")
        patient_id = http.request.env['res.partner'].sudo().search([('name', '=', patient_name), ('create_uid', '=', actual_user.id)]).id
        if patient_id:
            scan = http.request.env['partner.scan'].sudo().create({
                'cancer_type': cancer_type,
                'file_type': file_type,
                'partner_id': patient_id,
                'scan_file': scan_file,
            })
            query = f"""UPDATE partner_scan SET create_uid = {actual_user.id} WHERE id = {scan.id}"""
            http.request.env.cr.execute(query)
            return json.dumps({'success': scan.classification})
        else:
            return json.dumps({'error': 'Patient not found'})