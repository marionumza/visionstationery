# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"
    
    comment = fields.Char("Comment")


 