# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, _

class BlogPost(models.Model):
    _inherit = "blog.post"
    _description = "Blog Post"
    
    background_image = fields.Binary(string='Background Image', oldname='content_image')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: