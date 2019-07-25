from odoo import models, fields, api, SUPERUSER_ID,_
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError


class StockPackingWizard(models.TransientModel):
    
    _name = 'stock.packing.wizard'
    
    line_ids = fields.One2many('stock.packing.line.wizard','packing_wizard_id',string="Lines")

    @api.multi
    def create_packing(self):
        FLAG = False
        for test_line in self.line_ids:
            if test_line.packing_qty > 0:
                FLAG = True
            if test_line.packing_qty > test_line.remain_pack:
                raise UserError(_('Packing Qty Should not be more then actual need to pack qty!'))
        if not FLAG:
            raise UserError(_('No Packing QTY value entered!'))
        operations = self.line_ids.filtered(lambda o: o.packing_qty > 0.00)
        operation_ids = self.env['stock.move.line']
        if operations:
            package = self.env['stock.quant.package'].create({})
            for operation in operations:
                if not (len(operation.move_id.move_line_ids) > 1) and float_compare(operation.packing_qty, operation.move_id.move_line_ids.product_uom_qty, precision_rounding=operation.move_id.move_line_ids.product_uom_id.rounding) >= 0:
                    operation.move_id.move_line_ids.write({'qty_done': operation.packing_qty})
                    operation_ids |= operation.move_id.move_line_ids
#                     operation_ids.write({'qty_done': operation.packing_qty})
                else:
                    op_move_line_ids = operation.move_id.move_line_ids.sorted(key=lambda r: r.id)
                    total_uom_qty = sum(operation.move_id.move_line_ids.mapped('product_uom_qty'))
                    total_uom_qty_done = sum(operation.move_id.move_line_ids.mapped('qty_done'))
                    actual_qty_need = total_uom_qty - total_uom_qty_done
                    quantity_left_todo = float_round(
                        actual_qty_need - operation.packing_qty,
                        precision_rounding=op_move_line_ids[0].product_uom_id.rounding,
                        rounding_method='UP')
                    done_to_keep = operation.packing_qty
                    new_operation_move = op_move_line_ids[0].copy(
                        default={'product_uom_qty': 0, 'qty_done':operation.packing_qty})
                    op_move_line_ids[0].write({'product_uom_qty': quantity_left_todo, 'qty_done': 0.00})
                    new_operation_move.write({'product_uom_qty': done_to_keep, 'qty_done': operation.packing_qty})
                    operation_ids |= new_operation_move
                operation_ids.write({'result_package_id': package.id})
        return True
    
    
    

class StockPackingLineWizard(models.TransientModel):
    _name = 'stock.packing.line.wizard'
    
    @api.multi
    def _get_remain_qty(self):
        for rec in self:
            rec.remain_pack = rec.reserved_qty - rec.done_qty
    
    packing_wizard_id = fields.Many2one('stock.packing.wizard','wizard')
    move_id = fields.Many2one('stock.move','Move')
    product_id = fields.Many2one('product.product',string="Product")
    reserved_qty = fields.Float("Reserved Qty")
    done_qty = fields.Float('Done Qty')
    packing_qty = fields.Float("Packing Qty")
    remain_pack = fields.Float(compute='_get_remain_qty',string='Need to Pack')
    