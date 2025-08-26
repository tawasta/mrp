
from odoo import models


class MrpMove(models.Model):

    _inherit = 'mrp.move'
    _order = "product_mrp_area_id, mrp_date, current_date, mrp_type desc, id"
