# -*- coding: utf-8 -*-

from odoo import api, fields, models
import string
from datetime import datetime

import sys, getopt, os, struct
from Crypto.Cipher import AES
from Crypto.Hash import MD5, SHA256
from Crypto import Random
import  Crypto.Util.Counter
import base64
import hashlib

mode = {
    'ecb': AES.MODE_ECB,
    'cfb': AES.MODE_CFB,
    'ofb': AES.MODE_OFB,
    'cbc': AES.MODE_CBC,
}

class EncryptDecrypt(models.Model):

    _name = 'encrypt.decrypt'

    name = fields.Char("Name", required=True)
    action = fields.Selection(
        string="Action",
        selection=[
            ('encrypt', 'Encrypt'),
            ('decrypt', 'Decrypt'),
        ],
        required=True,
        default='encrypt'
    )
    mode = fields.Selection(
        string="Mode",
        selection=[
            ('ecb', 'ECB'),
            ('cfb', 'CFB'),
            ('ofb', 'OFB'),
            ('cbc', 'CBC'),
        ]
    )
    bs = fields.Integer("BS", default=32)
    key = fields.Char("Key", required=True)
    input_text = fields.Text("Text Input")
    output_text = fields.Text("Text Output")

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]


    def encrypt_text(self):
        if not self.input_text:
            return None
        key = hashlib.sha256(self.key.encode()).digest()

        raw = self._pad(self.input_text)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, mode[self.mode], iv)
        self.output_text = base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt_text(self):
        if not self.input_text:
            return
        key = hashlib.sha256(self.key.encode()).digest()
        enc = base64.b64decode(self.input_text)
        iv = enc[:AES.block_size]
        cipher = AES.new(key, mode[self.mode], iv)
        self.output_text = self._unpad(self, cipher.decrypt(enc[AES.block_size:])).decode('utf-8')
