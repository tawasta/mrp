from odoo import api, models
import logging

_logger = logging.getLogger(__name__)


class MultiLevelMrp(models.TransientModel):

    _inherit = "mrp.multi.level"

    @api.model
    def _prepare_mrp_move_data_from_stock_move(self, product_mrp_area, move, direction="in"):
        move_data = super()._prepare_mrp_move_data_from_stock_move(
            product_mrp_area=product_mrp_area,
            move=move,
            direction=direction
        )

        ignore_production = product_mrp_area.mrp_area_id.ignore_production_orders
        production = move_data.get("production_id", False)

        if production and ignore_production:
            _logger.info("Ignoring production orders in MRP multi level computations")
            return {}

        ignore_purchase = product_mrp_area.mrp_area_id.ignore_purchase_orders
        purchase = move_data.get("purchase_order_id", False)

        if purchase and ignore_purchase:
            _logger.info("Ignoring PURCHASE ORDERS in MRP multi level computations!!")
            return {}

        move_id = move_data.get("stock_move_id", False)
        stock_move = self.env["stock.move"].browse(move_id)

        picking_id = stock_move.picking_id if stock_move else False
        sale_order = picking_id.sale_id if picking_id else False

        ignore_sale = product_mrp_area.mrp_area_id.ignore_sale_orders

        if sale_order and ignore_sale:
            _logger.info("Ignoring SALE ORDERS in MRP multi level computations!!")
            return {}

        return move_data
