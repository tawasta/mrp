# -*- coding: utf-8 -*-


from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = 'sale.order'

#     def create(self):
#
#         print "TESTING CREATE IN SALE ORDER"
#
#         group_users = self.env.ref('sales_agent.group_agent').users
#
#
#         if self.env.user.id in group_users.ids:
#             print "CREATE WORKD IN HERE"



