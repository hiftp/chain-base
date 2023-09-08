# -*- coding: utf-8 -*-
"""Vehicle Registration"""


from odoo import fields, models, api, _
from random import randint


class Vehicles(models.Model):
    """model for managing vehicle registration"""
    _name = "vehicle.registration"
    _description = "Vehicle Registration"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Vehicle Registration", store=True, required=True)
    athlete_ids = fields.Many2many('organisation.athletes', string="Athletes",
                                   store=True, readonly=False,
                                   compute='_compute_athlete_ids')

    @api.depends('name')
    def _compute_athlete_ids(self):
        for vehicle in self:
            athletes = self.env['organisation.athletes'].search(
                [('vehicle_ids', 'in', vehicle.id)])
            vehicle.athlete_ids = athletes
