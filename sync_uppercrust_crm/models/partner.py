# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, tools, _

class ResPartner(models.Model):

    _inherit = "res.partner"

    def geo_query_address(self, street=None, zip=None, city=None, state=None, country=None):
        if country and ',' in country and (country.endswith(' of') or country.endswith(' of the')):
            country = '{1} {0}'.format(*country.split(',', 1))
        return tools.ustr(', '.join(
            field for field in [street, ("%s %s" % (zip or '', city or '')).strip(), state, country]
            if field
        ))

    def get_geo_localize(self):
        return self.geo_query_address(street=self.street,
                                    zip=self.zip,
                                    city=self.city,
                                    state=self.state_id and self.state_id.name,
                                    country=self.country_id and self.country_id.name)


class ResCompany(models.Model):

    _inherit = "res.company"

    def get_geo_localize(self):
        return self.partner_id.get_geo_localize()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: