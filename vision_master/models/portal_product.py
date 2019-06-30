from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from operator import itemgetter
import logging
_logger = logging.getLogger(__name__)


class PortalProductMap(models.Model):
    _name = 'portal.product.map'
    _description = 'Mapping product name per portal'

    name = fields.Char('Portal Code')
    description = fields.Char('Product description in portal')
    product_id = fields.Many2one('product.product', 'Product')

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            name = rec.name and rec.product_id and ' - '.join(
                [rec.name, rec.product_id.name]) or rec.name or rec.product_id and rec.product_id.name or False
            res.append((rec.id, name))
        return res
