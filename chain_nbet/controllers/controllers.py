# -*- coding: utf-8 -*-
from odoo import http

# class NbetProcess(http.Controller):
#     @http.route('/nbet__process/nbet__process/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/nbet__process/nbet__process/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('nbet__process.listing', {
#             'root': '/nbet__process/nbet__process',
#             'objects': http.request.env['nbet__process.nbet__process'].search([]),
#         })

#     @http.route('/nbet__process/nbet__process/objects/<model("nbet__process.nbet__process"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nbet__process.object', {
#             'object': obj
#         })