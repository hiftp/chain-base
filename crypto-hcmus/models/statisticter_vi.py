# -*- coding: utf-8 -*-

from odoo import api, fields, models
import string
from datetime import datetime

class StatisticterVi(models.Model):

    _name = 'statisticter.vi'

    name = fields.Char("Name", required=True)
    description = fields.Text("List file")
    table = fields.Html("Result")

    def compute_result(self):
        objs = self.env['statisticter.vi'].search([('id', '=', id)])
        attch_env = self.env['ir.attachment']
        for rec in objs:
            table = '''
            <table style="width:100%">
                <tr>
                    <th>Letter</th>
                    <th>Percent (%)</th> 
                </tr>
            '''
            # Init result
            file_name = ''
            result = {}
            for i in string.ascii_lowercase:
                result[i] = 0
            datas = attch_env.search(
                [('res_model', '=', 'statisticter.vi'),
                 ('res_id', '=', rec.id)])
            if not datas:
                continue
            for char in datas.index_content:
                if char in result.keys():
                    result[char] = result[char] + 1
                file_name = file_name + char.name
            # Compute total
            total = 0
            for k in result.keys():
                total = total + result[k]
            # Compute 
            for k in result.keys():
                result[k] = round(100.0 * result[k] / total, 2)
                row = '''
                <tr>
                    <td>%s</td>
                    <td>%s</td> 
                </tr>
                ''' % (k, result[k])
                table = table + row
            table = table + '</table>'
            rec.table = table
            rec.description = file_name
