import logging
from datetime import date

from odoo import api
from odoo import models
from odoo import _
from odoo.addons.queue_job.job import job

_logger = logging.getLogger(__name__)


class MultiLevelMrp(models.TransientModel):
    _inherit = "mrp.multi.level"

    @api.model
    @job()
    def _mrp_cleanup_queued(self, mrp_areas):
        res = super(MultiLevelMrp, self)._mrp_cleanup(mrp_areas)
        area_names = ','.join([str(a.name) for a in mrp_areas]).lstrip(",")

        job_desc = _(
            "MRP Multi-level: MRP Applicable for {}".format(area_names)
        )
        self.with_delay(description=job_desc)._calculate_mrp_applicable_queued(
            mrp_areas
        )

        if res:
            msg = _("MRP Cleanup done")
        else:
            msg = _("MRP Cleanup failed!")

        return msg

    @api.model
    @job()
    def _calculate_mrp_applicable_queued(self, mrp_areas):
        res = super(MultiLevelMrp, self)._calculate_mrp_applicable(mrp_areas)
        area_names = ','.join([str(a.name) for a in mrp_areas]).lstrip(",")

        job_desc = _(
            "MRP Multi-level: MRP Initialisation for {}".format(area_names)
        )
        self.with_delay(description=job_desc)._mrp_initialisation_queued(mrp_areas)

        if res:
            msg = _("MRP Applicable calculation done")
        else:
            msg = _("MRP Applicable calculation failed!")

        return msg

    @api.model
    @job()
    def _mrp_initialisation_queued(self, mrp_areas):
        res = super(MultiLevelMrp, self)._mrp_initialisation(mrp_areas)
        area_names = ','.join([str(a.name) for a in mrp_areas]).lstrip(",")

        job_desc = _(
            "MRP Multi-level: MRP Calculation for {}".format(area_names)
        )
        self.with_delay(description=job_desc)._mrp_calculation_queued(mrp_areas)

        # res is empty on success, so no check here
        msg = _("MRP Initialisation done")

        return msg

    @api.model
    @job()
    def _mrp_calculation_queued(self, mrp_areas):
        mrp_lowest_llc = self._low_level_code_calculation()
        # Use _mrp_calculation from this module to allow splitting LLC:s into standalone jobs
        res = self._mrp_calculation(mrp_lowest_llc, mrp_areas)

        if res:
            msg = _("MRP LLC Calculation queued")
        else:
            msg = _("MRP LLC Calculation queue failed!")

        return msg

    @api.model
    @job()
    def _mrp_final_process_queued(self, mrp_areas):
        res = super(MultiLevelMrp, self)._mrp_final_process(mrp_areas)

        # res is empty on success, so no check here
        msg = _("MRP Final process done")

        return msg

    @api.multi
    @job()
    def run_mrp_multi_level_queued(self):
        for area in self.env["mrp.area"].search([]):
            job_desc = _("MRP Multi-level: MRP Cleanup for '{}'".format(area.name))
            self.with_delay(description=job_desc)._mrp_cleanup_queued(area)

    @api.model
    def _mrp_calculation(self, mrp_lowest_llc, mrp_areas):
        _logger.info('Start MRP calculation')
        if not mrp_areas:
            mrp_areas = self.env['mrp.area'].search([])
        for mrp_area in mrp_areas:
            llc = 0
            job_desc = _("MRP Multi-level: MRP Calculation LLC {} for {}".format(llc, mrp_area.name))
            self.with_delay(description=job_desc)._mrp_calculation_llc(mrp_area, mrp_lowest_llc, llc)

        log_msg = 'MRP Calculation queued'
        _logger.info(log_msg)

        return True

    @api.model
    @job(default_channel="root.ir_cron")
    def _mrp_calculation_llc(self, mrp_area, mrp_lowest_llc, llc):
        _logger.info('Starting MRP calculation for LLC %s' % llc)
        end_msg = 'End MRP calculation for LLC %s' % llc
        product_mrp_area_obj = self.env['product.mrp.area']

        product_mrp_areas = product_mrp_area_obj.search(
            [('product_id.llc', '=', llc),
             ('mrp_area_id', '=', mrp_area.id)])
        llc += 1

        area_count = len(product_mrp_areas)
        area_number = 0
        _logger.info("Area count: {}".format(area_count))
        for product_mrp_area in product_mrp_areas:
            area_number += 1
            _logger.info("Area {}/{}: {}".format(area_number, area_count, product_mrp_area.product_id.display_name))
            nbr_create = 0
            onhand = product_mrp_area.qty_available
            if product_mrp_area.mrp_nbr_days == 0:
                for move in product_mrp_area.mrp_move_ids:
                    if self._exclude_move(move):
                        continue
                    qtytoorder = product_mrp_area.mrp_minimum_stock - \
                                 onhand - move.mrp_qty
                    if qtytoorder > 0.0:
                        cm = self.create_action(
                            product_mrp_area_id=product_mrp_area,
                            mrp_date=move.mrp_date,
                            mrp_qty=qtytoorder, name=move.name)
                        qty_ordered = cm['qty_ordered']
                        onhand += move.mrp_qty + qty_ordered
                        nbr_create += 1
                    else:
                        onhand += move.mrp_qty
            else:
                nbr_create = self._init_mrp_move_grouped_demand(
                    nbr_create, product_mrp_area)

            if onhand < product_mrp_area.mrp_minimum_stock and \
                    nbr_create == 0:
                qtytoorder = \
                    product_mrp_area.mrp_minimum_stock - onhand
                cm = self.create_action(
                    product_mrp_area_id=product_mrp_area,
                    mrp_date=date.today(),
                    mrp_qty=qtytoorder,
                    name='Minimum Stock')
                qty_ordered = cm['qty_ordered']
                onhand += qty_ordered

        _logger.info(end_msg)

        if mrp_lowest_llc > llc:
            job_desc = _("MRP Multi-level: MRP Calculation LLC {} for {}".format(llc, mrp_area.name))
            self.with_delay(description=job_desc)._mrp_calculation_llc(mrp_area, mrp_lowest_llc, llc)
        else:
            job_desc = _(
                "MRP Multi-level: MRP Final Process for {}".format(mrp_area.name)
            )
            self.with_delay(description=job_desc)._mrp_final_process_queued(mrp_area)

            end_msg = "End MRP calculation"

        return end_msg
