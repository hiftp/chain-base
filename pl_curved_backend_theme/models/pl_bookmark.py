# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class PlBookmark(models.Model):
    _name = 'pl.bookmark'
    _description = 'User Bookmarpl'

    pl_bookmark_name = fields.Char(string="Bookmark Name", help="Name for displaying alphabet")
    pl_bookmark_url = fields.Char(string="Bookmark Url", help="Url of Bookmark")
    pl_bookmark_position = fields.Integer(string="Bookmark Position", default=1, help="Position of bookmark")
    pl_user_id = fields.Many2one(string="User", comodel_name="res.users", required=True, help="Connected User")