from odoo import models, fields, api
from odoo.addons.queue_job.job import job


class BomArchivedProductWizard(models.TransientModel):

    _name = "mrp_bom_archived_product_list.wizard"

    @api.multi
    @job(default_channel="root.ir_cron")
    def compute(self):
        bom_model = self.env["mrp.bom"]
        # Do a search_read first so that the whole mass of BOMs do not get
        # browsed at the same time
        all_boms = bom_model.search_read([], ["id"])
        for bom in all_boms:
            bom_model.browse(bom["id"]).refresh_archive_info()

    @api.model
    def cron_compute(self):
        # Different decorator so that it's callable also from ir.cron
        bom_model = self.env["mrp.bom"]
        all_boms = bom_model.search_read([], ["id"])
        for bom in all_boms:
            job_desc = "Compute archived products for {}".format(bom.name)
            bom_model.browse(bom["id"]).with_delay(description=job_desc).refresh_archive_info()

    name = fields.Char("Name")
