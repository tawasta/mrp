from odoo import api
from odoo import models
from odoo import _
from odoo.addons.queue_job.job import job


class MultiLevelMrp(models.TransientModel):
    _inherit = "mrp.multi.level"

    @api.model
    @job()
    def _mrp_cleanup_queued(self, mrp_areas):
        res = super(MultiLevelMrp, self)._mrp_cleanup(mrp_areas)

        job_desc = _(
            "MRP Multi-level: MRP Applicable for areas {}".format(mrp_areas.ids)
        )
        self.with_delay(description=job_desc)._calculate_mrp_applicable_queued(
            mrp_areas
        )

        return res

    @api.model
    @job()
    def _calculate_mrp_applicable_queued(self, mrp_areas):
        res = super(MultiLevelMrp, self)._calculate_mrp_applicable(mrp_areas)

        job_desc = _(
            "MRP Multi-level: MRP Initialisation for areas {}".format(mrp_areas.ids)
        )
        self.with_delay(description=job_desc)._mrp_initialisation_queued(mrp_areas)

        return res

    @api.model
    @job()
    def _mrp_initialisation_queued(self, mrp_areas):
        res = super(MultiLevelMrp, self)._mrp_initialisation(mrp_areas)

        job_desc = _(
            "MRP Multi-level: MRP Calculation for areas {}".format(mrp_areas.ids)
        )
        self.with_delay(description=job_desc)._mrp_calculation_queued(mrp_areas)

        return res

    @api.model
    @job()
    def _mrp_calculation_queued(self, mrp_areas):
        mrp_lowest_llc = self._low_level_code_calculation()
        res = super(MultiLevelMrp, self)._mrp_calculation(mrp_lowest_llc, mrp_areas)

        job_desc = _(
            "MRP Multi-level: MRP Final Process for areas {}".format(mrp_areas.ids)
        )
        self.with_delay(description=job_desc)._mrp_final_process_queued(mrp_areas)

        return res

    @api.model
    @job()
    def _mrp_final_process_queued(self, mrp_areas):
        return super(MultiLevelMrp, self)._mrp_final_process(mrp_areas)

    @api.multi
    @job()
    def run_mrp_multi_level_queued(self):
        for area in self.env["mrp.area"].search([]):
            job_desc = _("MRP Multi-level: MRP Cleanup for '{}'".format(area.name))
            self.with_delay(description=job_desc)._mrp_cleanup_queued(area)
