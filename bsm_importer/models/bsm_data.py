from odoo import fields, models


class BsmData(models.Model):
    _name = "bsm.data"
    _inherit = ["mail.thread"]
    _description = "BSM Data"

    """
    *124169*=Toimitusnumero
    *TCP90EU*=Tyyppitieto
    *102N32T0017297*=sarjanumero
    *351535052976123*=IMEI
    *BGS2-W 01.3010*=GSM versio
    *CT1P.01.013.0000*=FW versio
    *XTrac2.3.0BF*= GPS versio
    *32,1,A,1,1,T0* =HW versio
    *T2* =takuuaika
    """

    bsm_delivery_number = fields.Char("Delivery Number", size=64)
    bsm_product_code = fields.Char("Product Code", size=64)
    name = fields.Char("BSM Serial")
    bsm_imei_code = fields.Char("IMEI Code", size=15)
    bsm_gsm_version = fields.Char("GSM Version")
    bsm_fw_version = fields.Char("FW Version")
    bsm_gps_version = fields.Char("GPS Version")
    bsm_hw_version = fields.Char("HW Version")
    bsm_warranty_time = fields.Float("Warranty")
    bsm_warranty_code = fields.Char("Warranty Code")
    bsm_used = fields.Boolean("Used", default=False)
    bsm_prodlot_id = fields.Many2one("stock.production.lot", "Lot")
