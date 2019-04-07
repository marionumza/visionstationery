# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
import logging
from odoo import fields, models, api, _
from odoo import SUPERUSER_ID
from odoo.exceptions import Warning, ValidationError
_logger = logging.getLogger(__name__)

LoyaltyProcess = [
    ('addition', 'Points Added'),
    ('deduction', 'Point Deducted')
]

LoyalityBase = [
    ('purchase', 'Purchase Amount'),
    ('category', 'Product Category')
]
Policy = [
    ('one_time_redeem', 'One Time Redemption'),
    ('partial_redeem', 'Partial Redemption')
]
ProductDomain = [
    ('type', '=', 'service'),
]
RedeemStage = [
    ('draft', 'On Order Completion'),
    ('confirm', 'On Order Confirmation')
]

HelpReddemPolicy = _(
    """* The The One time redeem policy  is set when user have only one
    time redeem options,after the redemption reward points will reduced to zero!\n
    * The Partial Redeem  policy  allow user the redeem
    some specific amount of money multiple time with the appropriate point reduction. """
)


class WebsiteLoyaltyManagement(models.Model):
    _name = "website.loyalty.management"
    _description = "Website Loyalty Management"

    name = fields.Char(
        string="Name",
        help=" The mention name will represented as the loyalty product name in the cart !",
        required=True,
        default='Loyalty Program 2016-17',
        copy=False
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        copy=False
    )
    loyalty_product_description = fields.Text(
        string="Loyalty Product Description",
        help=" These Text will be visible to user in there cart with awarded amount of loyalty benefits",
        default='This loyalty product represent loyalty benefits awarded for you !',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        domain=ProductDomain,
        string="Loyalty Product",
        required=True
    )
    image = fields.Binary(
        related='product_id.image'
    )
    start_date = fields.Date(
        string='Start Date'
    )
    end_date = fields.Date(
        string='End Date'
    )
    min_purchase = fields.Float(
        string="Minimum  Purchase",
        required=True,
        default=1
    )
    purchase = fields.Float(
        string="Purchase Amount",
        required=True,
        default=1
    )
    points = fields.Float(
        required=True,
        default=1
    )
    signup_points = fields.Float(
        string='Sign Up Points'
    )
    loyalty_redeem_stage = fields.Selection(
        selection=RedeemStage,
        string="Benefits Awarded ",
        required=True,
        default='draft'
    )
    loyalty_base = fields.Selection(
        selection=LoyalityBase,
        string="Loyalty Awarded On Basis Of",
        readonly=True,
        default="purchase"
    )
    max_redeem_amount = fields.Float(
        string="Maximum Redeem Amount Per Sale Order",
        required=True,
        default=1000.0
    )
    redeem_rule_list = fields.One2many(
        comodel_name="reward.redeem.rule",
        inverse_name='loyalty_fk',
        string="Redeem Rule"
    )
    redeem_policy = fields.Selection(
        selection=Policy,
        string="Loyalty Policy",
        help=HelpReddemPolicy,
        required=True,
        default='one_time_redeem'
    )
    _sql_constraints = [
        (
            'unique_name',
            'unique(name)',
            _('A Loyalty Program with the same name already exists!')
        ),
    ]


    @api.one
    @api.constrains('max_redeem_amount')
    def _check_max_redeem_amount(self):
        if self.max_redeem_amount <= 0:
            raise ValidationError(_(
                "Max redeem amount should be positive."))
    @api.one
    @api.constrains('signup_points')
    def _check_signup_points(self):
        if self.signup_points and self.signup_points <0:
            raise ValidationError(_(
                "Signu Points should be positive."))

    @api.model
    def get_active_obj(self,domain=None):
        domain = domain or []
        return self.search(domain, limit=1)

    @api.model
    def _fetch_signup_loyalty_points(self):
        return self.signup_points or 0

    @api.model
    def _get_redeem_rule_id(self,partner_id=None):
        partner_id = partner_id or self.env.user.partner_id
        points = partner_id.wk_website_loyalty_points
        redeem_rule_id = self.redeem_rule_list.filtered(
            lambda rule: rule.point_start <= points
            and rule.point_end >= points)
        return redeem_rule_id and redeem_rule_id[0]

    @api.model
    def _get_loyalty_sale_line_info(self):
        line_info=self.sudo().read(['name','loyalty_product_description'])[0]
        return {
            'name': line_info.get('name','')+'\n'+line_info.get('loyalty_product_description',''),
            'description': line_info.get('loyalty_product_description'),
            'product_id': self.sudo().product_id
        }


    @api.model
    def get_loyalty_points(self, amount):
        if self.purchase > 0 and amount >= self.min_purchase:
            offer_ratio = self.points / self.purchase
            return amount * offer_ratio
        return 0

    @api.model
    def _get_loyalty_amount(self,  sale_order_amount,partner_id=None):
        result={'reward_amount': 0, 'remain_points': 0,'redeem_point': None}
        partner_id = partner_id or self.env.user.partner_id
        wk_website_loyalty_points = partner_id.wk_website_loyalty_points
        if sale_order_amount > 1:
            max_redeem_amount=self.max_redeem_amount
            redeem_rule = self.redeem_rule_list
            redeem_rule_list=redeem_rule.filtered(
            lambda rule:rule.point_start<=wk_website_loyalty_points and
            rule.point_end>=wk_website_loyalty_points)
            if len(redeem_rule_list):
                redeem_rule_list = redeem_rule_list[0]


            computed_redeem_amount=wk_website_loyalty_points*redeem_rule_list.reward
            reduction_amount = computed_redeem_amount if computed_redeem_amount<max_redeem_amount else max_redeem_amount

            if self.redeem_policy == 'one_time_redeem':
                if sale_order_amount <= reduction_amount:
                    result['reward_amount'] = sale_order_amount
                else:
                    result['reward_amount'] = reduction_amount
                result['remain_points']=0
                result['redeem_point'] = wk_website_loyalty_points#
            elif self.redeem_policy == 'partial_redeem' and redeem_rule_list.reward :
                if sale_order_amount <=    reduction_amount:
                    result['reward_amount'] = sale_order_amount
                    result['remain_points'] = abs((computed_redeem_amount-sale_order_amount)/redeem_rule_list.reward)
                    result['redeem_point'] = sale_order_amount/redeem_rule_list.reward#
                else:
                    result['reward_amount'] = reduction_amount
                    result['remain_points'] = abs((computed_redeem_amount-reduction_amount)/redeem_rule_list.reward)
                    result['redeem_point'] = reduction_amount/redeem_rule_list.reward#
        return result

    @api.model
    def update_partner_loyalty(self, order_obj, order_state):
        order_data = order_obj.read(['state','wk_loyalty_state','partner_id','wk_website_loyalty_points'])[0]
        if ( order_data.get('state') not in ['cancel']
        and (self.loyalty_redeem_stage == order_state)
        and (order_data.get('wk_loyalty_state') != 'done')
        and (order_data.get('wk_website_loyalty_points') > 0)):
            order_obj.partner_id.wk_website_loyalty_points+=order_data.get('wk_website_loyalty_points')
            order_obj.wk_loyalty_state = 'done'
            return self._save_gain_history(order_data)
        return True

    @staticmethod
    def get_history_point(history_ids):
        point_added, point_deducted = 0, 0
        for history_id in history_ids:
            if history_id.loyalty_process == 'addition':
                point_added += history_id.points_processed
            elif history_id.loyalty_process == 'deduction':
                point_deducted += history_id.points_processed
        return point_added, point_deducted

    @api.model
    def cancel_redeem_history(self, order_obj):
        if order_obj.wk_loyalty_state != 'cancel':
            domain = [('sale_order_ref', '=', order_obj.id)]
            history_ids = self.env['website.loyalty.history'].search(domain)
            if history_ids:
                point_added, point_deducted = self.get_history_point(history_ids)
                points = point_deducted if order_obj.wk_loyalty_state == 'draft' else (
                    point_deducted - point_added)
                order_obj.partner_id.wk_website_loyalty_points += points
                history_ids.unlink()
            order_obj.wk_loyalty_state = 'cancel'

    @api.one
    def _save_redeem_history(self, sale_order, state='save'):
        History = self.env['website.loyalty.history']
        sale_order_line = sale_order.website_order_line.filtered(
        lambda line:line.product_id == self.product_id
        )
        if len(sale_order_line):
            sale_order_line = sale_order_line[0]
            domain = [
                ('sale_order_ref', '=', sale_order.id),
                ('loyalty_process', '=', 'deduction')
            ]
            already_deducted = History.search_count(domain)
            if state == 'save' and (not already_deducted):
                line_data = sale_order_line.read(['order_partner_id','redeem_points','price_unit'])[0]
                vals = {
                    'loyalty_id': self.id,
                    'partner_id': line_data.get('order_partner_id')[0],
                    'points_processed': line_data.get('redeem_points'),
                    'sale_order_ref': sale_order.id,
                    'redeem_amount': line_data.get('price_unit'),
                    'loyalty_process': 'deduction',
                    'process_reference': 'Sale Order',
                }
                return History.create(vals)
        return

    @api.model
    def _save_gain_history(self, order_data):
        History =self.env['website.loyalty.history']
        domain = [
            ('sale_order_ref', '=', order_data.get('id')),
            ('loyalty_process', '=', 'addition')
        ]
        already_deducted = History.search_count(domain)
        if not already_deducted:
            vals = {
                'partner_id':  order_data.get('partner_id')[0],
                'loyalty_id': self.id,
                'points_processed': order_data.get('wk_website_loyalty_points'),
                'sale_order_ref': order_data.get('id'),
                'loyalty_process': 'addition',
                'process_reference': 'Sale Order',
            }
            history_obj= History.create(vals)
            return history_obj
        return


class RewardRedeemRule(models.Model):
    _name = "reward.redeem.rule"
    _description = "Reward Redeem Rule Class"

    name = fields.Char(
        string='Rule Name',
        default="Default Redeem Rule "
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )
    point_start = fields.Float(
        string='Point Start',
        required=True,
        default=1
    )
    point_end = fields.Float(
        string='Point End',
        required=True,
        default=100)
    reward = fields.Float(
        string='Reward of 1 point',
        required=True
    )
    loyalty_fk = fields.Many2one(
        comodel_name='website.loyalty.management',
        ondelete="cascade"
    )

    @api.one
    @api.constrains('reward')
    def _check_reward(self):
        if self.reward <= 0:
            raise ValidationError(_(
                "Reward amount should be positive."))

    @api.one
    @api.constrains('point_start', 'point_end')
    def _check_point_range(self):
        """	validate the point_start and point_end !"""
        if self.point_start <= 0.0:
            raise ValidationError(
                _("Point Start should be positive."))
        if self.point_start == self.point_end:
            raise ValidationError(
                _("Point Start and Point End must be different."))
        elif self.point_start > self.point_end:
            raise ValidationError(_(
                "Point Start must be smaller  than  Point End."))
        else:
            redeem_rule_ids = self.search(
                [('loyalty_fk', '=', self.loyalty_fk.id)])
            if len(redeem_rule_ids) != 0:
                for redeem_rule_id in redeem_rule_ids:
                    if self.id != redeem_rule_id.id:
                        if (self.point_start <= redeem_rule_id.point_start and self.point_end >= redeem_rule_id.point_end) or \
                                (self.point_start >= redeem_rule_id.point_start and self.point_end <= redeem_rule_id.point_end) or\
                                (self.point_start >= redeem_rule_id.point_start and self.point_start <= redeem_rule_id.point_end):
                            raise ValidationError(
                                _("This Redeem Points range is already assign to another redeem Rule !"))


class WkLoyaltyRedeemHistory(models.Model):
    _name = "website.loyalty.history"

    _description = "Loyalty Redeem History Class"
    _rec_name = 'sale_order_ref'
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Customer"
    )
    loyalty_id = fields.Many2one(
        comodel_name='website.loyalty.management',
        string=" Loyalty Program"
    )
    redeem_policy = fields.Selection(
        related='loyalty_id.redeem_policy'
    )
    date = fields.Date(
        string='Redeemed Date',
        default=fields.Datetime().now()
    )
    loyalty_process = fields.Selection(
        selection=LoyaltyProcess,
        string="Process"
    )
    points_processed = fields.Float(
        string="Points"
    )
    process_reference = fields.Char(
        string="Reference"
    )
    sale_order_ref = fields.Many2one(
        string="Sale Order No.",
        comodel_name="sale.order",
        ondelete="cascade"
    )
    redeem_amount = fields.Float(
        string="Discount Offered"
    )
