import logging

from markupsafe import Markup

from odoo import _, models

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        for picking in self:
            wos = picking.purchase_id and picking.purchase_id.workorder_ids
            try:
                wos.action_mark_as_done()
            except Exception as e:
                message = _("Related Work Order could not be set as Done.")
                _logger.exception(message)
                message = Markup("%s<br/><br/>%s<br/>%s") % (
                    message,
                    _("This specific error occurred:"),
                    str(e),
                )
                picking.sudo().message_post(body=message)

        return super()._action_done()
