from odoo import fields, models


class ProductionMessageWizard(models.TransientModel):
    _name = "mrp.production.message.wizard"
    _description = "Production produce with message"

    production_ids = fields.Many2many(
        "mrp.production",
    )

    def produce_all(self):
        self.ensure_one()

        return self.production_ids.button_mark_done()
