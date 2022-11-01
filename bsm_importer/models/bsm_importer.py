import csv
import logging
import os

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class BsmImporter(models.Model):
    """
    BSM file importer UI methods and data deserialization
    """

    _name = "bsm.importer"
    _description = "BSM Data Importer"

    def _get_selection(self):
        bsm_data = self.env["bsm.data"].search([("bsm_used", "=", False)])
        res = [(r.bsm_product_code, r.bsm_imei_code) for r in bsm_data]

        return res

    imei_selection = fields.Many2one(comodel_name="bsm.data", string="IMEI Code")
    imeis_name = fields.Selection(_get_selection, string="Unused IMEI Codes")
    prodlot_id = fields.Many2one(comodel_name="stock.production.lot", string="Lot")

    def getSerials(self):
        # Read local file from the file system
        bsm_obj = self.env["bsm.data"]
        filepath = self.env.user.company_id.bsm_path

        created = 0
        updated = 0
        bsmIDs = []

        if not filepath or filepath == "":
            raise UserError(
                _(
                    "BSM Filepath missing. "
                    "Please set it first in the Stock Settings view."
                )
            )

        try:
            os.chdir(filepath)
            for files in os.listdir():
                if files.endswith(".bsm"):
                    prodlot = None
                    lot = self.prodlot_id
                    if lot:
                        prodlot = lot.id

                    with open(files, "rt") as csvfile:
                        hasHeader = False
                        reader = csv.reader(csvfile, delimiter=",", quotechar="*")

                        # *124169*=Toimitusnumero
                        # *TCP90EU*=Tyyppitieto
                        # *102N32T0017297*=sarjanumero
                        # *351535052976123*=IMEI
                        # *BGS2-W 01.3010*=GSM versio
                        # *CT1P.01.013.0000*=FW versio
                        # *XTrac2.3.0BF*= GPS versio
                        # *32,1,A,1,1,T0* =HW versio
                        # *T2* =takuuaika

                        for row in reader:
                            if reader.line_num == 1 and hasHeader:
                                pass
                            elif len(row) >= 9:
                                # search for existing bsm
                                vals = {
                                    "bsm_delivery_number": row[0],
                                    "bsm_product_code": row[1],
                                    "name": row[2],
                                    "bsm_imei_code": row[3],
                                    "bsm_gsm_version": row[4],
                                    "bsm_fw_version": row[5],
                                    "bsm_gps_version": row[6],
                                    "bsm_hw_version": row[7],
                                    "bsm_warranty_time": float(row[8][1:]),
                                    "bsm_warranty_code": row[8],
                                    "bsm_prodlot_id": prodlot,
                                }

                                existing = bsm_obj.search([("name", "=", row[2])])
                                if len(existing) == 0:
                                    # create a new bsm

                                    newBSM = bsm_obj.sudo().create(vals)
                                    bsmIDs.append(newBSM.id)
                                    created += 1
                                else:
                                    _logger.debug(
                                        _("Updating BSM for IMEI: {}").format(row[3])
                                    )
                                    vals["bsm_used"] = False
                                    existing.write(existing)
                                    for i in existing:
                                        bsmIDs.append(i)
                                    updated += 1

                        if lot:
                            _logger.debug(
                                _("Adding ids {} to production log {}").format(
                                    bsmIDs, lot.id
                                )
                            )
                            lot.write({"bsm_ids": [(6, 0, bsmIDs)]})

                        csvfile.close()
                        # rename file to mark it read
                        fname = "{}{}".format(filepath, files)
                        _logger.debug(_("Renaming {} to {}r").format(fname, fname))
                        # os.chmod(filepath+files, 555)
                        path_from = filepath + "/" + files
                        path_to = filepath + "/" + files + "r"
                        os.rename(path_from, path_to)

        except IOError as ioe:
            raise UserError(
                _("I/O error({}): {}").format(ioe.errno, ioe.strerror)
            ) from IOError
        except ValueError as fe:
            raise UserError(fe) from ValueError
        except Exception as e:
            raise UserError(e) from Exception

    def addBSM(self):
        return {
            "view_id": "bsm_data_view",
            "views": "form",
            "type": "ir.actions.act_window",
            "view_type": "form",
            "res_model": "bsm.data",
            "view_mode": "form",
            "target": "new",
            "context": self._context,
        }
