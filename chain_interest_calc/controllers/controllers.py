# -*- coding: utf-8 -*-
from odoo import http

class InterestCalc(http.Controller):
    @http.route('/interest_calc/interest_calc/', auth='public')
    def index(self, **kw):
        return "Hello, world"

    @http.route('/interest_calc/interest_calc/objects/', auth='public')
    def list(self, **kw):
        return http.request.render('chain_interest_calc.listing', {
            'root': '/interest_calc/interest_calc',
            'objects': http.request.env['chain_interest_calc.interest_calc'].search([]),
        })

    @http.route('/interest_calc/interest_calc/objects/<model("interest_calc.interest_calc"):obj>/', auth='public')
    def object(self, obj, **kw):
        return http.request.render('chain_interest_calc.object', {
            'object': obj
        })