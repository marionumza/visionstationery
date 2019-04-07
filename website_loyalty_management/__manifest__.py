# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Website Loyalty Program",
  "summary"              :  "The module helps to  win your customer loyalty .",
  "category"             :  "Website",
  "version"              :  "0.1",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "maintainer"           :  "Prakash Kumar",
  "website"              :  "https://store.webkul.com/Odoo-Website-Loyalty-Management.html",
  "description"          :  """http://webkul.com/blog/odoo-website-loyalty
    Odoo Website Loyalty Management For Website""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=website_loyalty_management&version=11.0",
  "depends"              :  [
                             'website_virtual_product',
                             'wk_wizard_messages',
                             'portal',
                             'website_sale_management'
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'views/res_config_view.xml',
                             'views/template.xml',
                             'views/website_loyalty_management.xml',
                             'data/data.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  69,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}
