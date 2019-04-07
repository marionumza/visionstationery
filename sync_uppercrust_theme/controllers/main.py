# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import datetime
import werkzeug
import functools
from odoo import tools
from odoo import http
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug
from odoo.osv.orm import browse_record
from odoo.tools.translate import _
from odoo import SUPERUSER_ID
from odoo.tools import html2plaintext
from odoo.modules import get_module_resource
import odoo.modules.registry
# from cStringIO import StringIO
from io import StringIO

class Binary(http.Controller):
    @http.route([
        '/default_logo.png'
    ], type='http', auth="none", cors="*")
    def company_logo(self, dbname=None, **kw):
        imgname = 'default_logo.png'
        placeholder = functools.partial(get_module_resource, 'web', 'static', 'src', 'img')
        uid = None
        if request.session.db:
            dbname = request.session.db
            uid = request.session.uid
        elif dbname is None:
            dbname = db_monodb()

        if not uid:
            uid = odoo.SUPERUSER_ID

        if not dbname:
            response = http.send_file(placeholder(imgname))
        else:
            try:
                registry = odoo.modules.registry.Registry(dbname)
                with registry.cursor() as cr:
                    cr.execute("""SELECT c.web_company_logo, c.write_date
                                    FROM res_users u
                               LEFT JOIN res_company c
                                      ON c.id = u.company_id
                                   WHERE u.id = %s
                               """, (uid,))
                    row = cr.fetchone()
                    if row and row[0]:
                        image_data = StringIO(str(row[0]).decode('base64'))
                        response = http.send_file(image_data, filename=imgname, mtime=row[1])
                    else:
                        response = http.send_file(placeholder('nologo.png'))
            except Exception:
                response = http.send_file(placeholder(imgname))
        return response


    # @http.route(['/page/about_us'], 
    #     type='http', auth="public", website=True)
    # def about_us(self, **kwargs):
    #     values = {}        
    #     values.update(kwargs=kwargs.items())
    #     return request.render("sync_uppercrust_theme.about_us", values)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: