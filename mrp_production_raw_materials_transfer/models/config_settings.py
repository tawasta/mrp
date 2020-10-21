from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    raw_materials_picking_type_id = fields.Many2one(
        related="company_id.raw_materials_picking_type_id",
        string="Raw Materials Transfer Picking Type",
        readonly=False,
    )

    raw_materials_src_location_id = fields.Many2one(
        related="company_id.raw_materials_src_location_id",
        string="Raw Materials Default Source Location",
        readonly=False,
    )
