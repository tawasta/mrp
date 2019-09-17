# -*- coding: utf-8 -*-


from __future__ import division
from odoo import api, fields, models


class MaterialRequirement(models.Model):

    _name = 'material.requirement'
    _description = 'Material Requirement'

#     product = fields.Selection(
#             string="Product",
#             selection='_get_products',
#             )

    product = fields.Many2one(
            comodel_name='product.template',
            string="Product",
            domain=[('bom_ids','!=',False)]
            )

#             compute='_get_products',
#             selection='_get_products',
#             )

    product_variant_id = fields.Integer(
            string="Product Variant ID",
            _compute="_get_product_variant_id",
            )

    name = fields.Char(
            )

    requirement = fields.Float(
            compute='calculate_requirement'
            )

    qty_to_manufacture = fields.Float(
            string="Quantity to Manufacture",
            compute='calculate_requirement',
            )

    qty_available = fields.Float(
            string="Available quantity",
            compute='_calculate_availability',
            )

    qty_promised = fields.Float(
            string="Promised Quantity",
            compute='_calculate_promised',
            )


#     bom = fields.Selection(
#             string="BoM",
#             selection='_get_bom',
# #             compute='_get_bom',
#             default='',
#             )

    bom = fields.Many2one(
            comodel_name='mrp.bom',
            string='BoM'
            )

    bom_lines = fields.Many2many(
#             compute='_get_bom_ids',
            comodel_name='mrp.bom.line',
            string='BoM lines',
            )

    bom_prod = fields.Integer(
            string="BOM Prod",
            )

    bom_product = fields.Char(
            string="BoM Product",
            )

    bom_qty_to_manufacture = fields.Float(
            string="Quantity to Manufacture",
#             compute='calculate_requirement',
            )

    bom_qty_available = fields.Float(
            string="Available quantity",
            compute='_calculate_availability',
            )

    material_requirement_line = fields.One2many(
            'material.requirement.line',
            'material_requirement_id',
            string='Material Requirement Line',
#             store=True,
            readonly=False,
            )

    product_variants = fields.Many2one(
            comodel_name='product.product',
            string='Product Variants',
#             domain=[('product_tmpl_id','=',product)]
#             compute='get_product_variants',
            )

    def _get_bom_ids(self, product):
        """Fetch product BoM lines"""

        return product.bom_ids

    @api.model
    def create(self, vals):

        vals['name'] = self.env['ir.sequence'].\
            next_by_code('material.requirement')

        res = super(MaterialRequirement, self).create(vals)
        return res

    @api.onchange('product_variants')
    def _calculate_promised(self):
        """This function calculates the promised quantity, meaning that it
        sums Available Quantity and the Quantity to Manyfacture"""
        for record in self:
            product = self.env['product.product'].search([
                ('id','=',int(record.product_variants))
            ])

            record.qty_promised = product.qty_available + record.qty_to_manufacture

    @api.onchange('product_variants')
    def _calculate_availability(self):
        for record in self:
            product = self.env['product.product'].search([
                ('id','=',int(record.product_variants))
            ])

            print "PRODUCT TO GET AVAILABILITY: ", product
            print "PRODUCT TO GET AVAILABILITY 2: ", product.qty_available

            record.qty_available = product.qty_available

            #DELETE STUFF BELOW LATER
#             quants = self.env['stock.quant'].search([('product_id.id','=',int(record.product_variants))])
#
#             for quant in quants:
#                 print "PRODUCT OF THIS QUANT IS: ", quant.product_id.name
#                 print "QUANT QTY: ", quant.qty
#                 record.qty_available = quant.qty

    @api.onchange('product')
    def get_product_variants(self):
        """Get selected product's variants"""

        for record in self:
            if record.product:
                print "RECORD PRODUCT IS INTEGER OR NOT?", record.product
                variants = record.product.product_variant_id
                for variant in variants:
                    record.product_variants = variant.id
                    print "VARIANT ID 1 IS ", variants.id
                    record.product_variant_id = variant.id
        self.get_material_requirement_line()

#     @api.multi
    @api.onchange('product_variants')
    def _get_product_variant_id(self):
        """Get product variant id"""
        for record in self:
            record.product_variant_id = record.product_variants.id
            print "PRODUCT VARIANT ID :", record.product_variant_id

    def create_requirement_lines(self, vals):
        """Create Requirement Lines using BoM values"""
        requirement_lines = self.env['material.requirement.line']

        values = []

#         for value in product_id:
#             print "VALUE: ", value
#
#             result = {
#                     'product_id': value.id,
#                     }
#
#             values.append(requirement_lines.create(result))

        #### USE THIS ONE LATER
#         if vals.bom_ids:
#             print "THIS PRODUCT HAS A BOM", vals.bom_ids
#             print "QTY TO MANUFACTURE", self.calculate_bom_lines(vals.bom_ids.bom_line_ids)

#         bom_id = mrp_bom.search(
#                 [('product_tmpl_id.id','=',vals.id)])

############################
        print "VALS: ", vals
#         print "VALS PRODUCT: ", vals.product_id
#         print "VALS PRODUCT ATTR: ", vals.product_id.attribute_value_ids
#         print "VALS ATT: ", vals.attribute_value_ids
############################
#         for line in vals:
        result = {
                'product_id': vals.product_id.id,
#                 'product_availability': vals.product_id.qty_available,
#                 'variant': vals.attribute_value_ids.name,
#                 'product_availability':vals['product_id'].qty_available,
#                 'variant':vals['variant'],
# #                 'bom':bom_id.id,
# #                 'bom':vals.bom_ids.id,
# #                 'qty_to_manufacture':vals
                }

        print "RESULT", result

#         values.append(requirement_lines.new(result))


#         print "RES PRODUCT: ", res.product_id

        print "VALUES ", values

#         return values

        return result

#         res = requirement_lines.create(result)
# #
#         return res

#         new = requirement_lines.new(result)
# #
#         return new

#     @api.multi
    @api.onchange('product')
    def get_material_requirement_line(self):
        """"Get Material requirement line"""

        print "ONCHANGE PRODUCT VARIANTS"

        self._get_product_variant_id()

        mrp_bom = self.env['mrp.bom']

        value_line = []

#         for record in self:
        vals = {
                'product_id': "",
                'variant': "",
#                     'product_id':[],
#                     'variant':[],
                }

        get_name = self.env['product.product'].search([('id','=', self.product_variant_id)])

        print "PRODUCT VARIANT ID FOR BOM: ", self.product_variants

        bom_id = mrp_bom.search(
            ['&',
             ('product_tmpl_id.id','=', self.product.id),
             '|',
             ('product_id','=', self.product_variant_id),
             ('product_id','=', False)],limit=1
        )

        material = self.env['material.requirement.line']

        print "DOES BOM HAVE PRODUCT ID: ", bom_id.product_id

        print "BOM LINESTUFFF", bom_id.bom_line_ids

        mate_list = []

        for line in bom_id.bom_line_ids:
            print "Creating a new requirement line..."
#                 vals['product_id'] = line.product_id
#                 vals['variant'] = line.attribute_value_ids
#                 vals['product_id'].append(line.product_id)
#                 vals['variant'].append(line.attribute_value_ids)
#             self.material_requirement_line += self.create_requirement_lines(line)
            mate_list.append(material.new(self.create_requirement_lines(line)).id)

#             self.create_requirement_lines(line)
#
#         self.material_requirement_line = material
#         for mat in material:
        self.material_requirement_line = [(6, 0, mate_list)]
#         line_ids = [(6, 0, material.ids)]
#
#         print "MATERIAL ", material
#         print "MATERIAL IDS", material.ids

#         print "LINE IDS", line_ids

#         for mat in material:
#         res = self.update({
#             'material_requirement_line': line_ids
#             })

        print "MATE LIST: ", mate_list




#         return {'value': {'material_requirement_line': mate_list}}

#
#             for mat in material:
#                 self.material_requirement_line = [(4, mat.id, 0)]
#                 print "MAT ID", mat.id
#                 self.material_requirement_line = mat
#
#
# #             self.material_requirement_line = [(4, self.create_requirement_lines(line).id, 0)]
#             print "SELF MATERIAL REQUIREMENT LINE ", self.material_requirement_line

#             for mat in material:
#             self.material_requirement_line += material

#         self.material_requirement_line = self.create_requirement_lines(bom_id.bom_line_ids)
#             material += mat
#         self.material_requirement_line = [(6, 0, material)]




#         valu = {'material_requirement_line': [(6, 0, material)]}
#
#         print "VALUUUUUU ", valu
#
#         return super(MaterialRequirement, self).create(valu)



#                 record.material_requirement_line += self.create_requirement_lines(line)
#
#                 print "RECORD MATERIAL REQUIREMENT LINE ", record.material_requirement_line



#                 return material
#                 record.material_requirement_line = self.create_requirement_lines(line)
#                 new = material.new(self.create_requirement_lines(line))
#                 print "RECORD LINE: ", record.material_requirement_line
#                 value_line.append(new)
#                 return value_line


#                 record.material_requirement_line = self.create_requirement_lines(vals)
#
#                 material += record.material_requirement_line
#
#             record.material_requirement_line = material

################
#     @api.onchange('bom')
#     def onchange_bom_material_line(self):
#
#         material = self.env['material.requirement.line']
#
#         for record in self:
#             for line in record.bom.bom_line_ids:
#                 record.material_requirement_line = self.create_requirement_lines(line)
###############

    @api.onchange('product_variants','product')
    def _get_bom(self):
        """When a product is selected, get that product's BoM"""
        mrp_bom = self.env['mrp.bom']
        for record in self:
            product = self.env['product.template'].search([
                ('id','=',int(record.product))
            ])

            bom_id = mrp_bom.search(
                ['&',
                 ('product_tmpl_id.id','=', record.product.id),
                 '|',
                 ('product_id','=',record.product_variant_id),
                 ('product_id','=',False)],limit=1
            )

            bom_id_2 = mrp_bom.search(
                ['&',
                 ('product_tmpl_id.id','=', record.product.id),
                 '|',
                 ('product_id','=',record.product_variant_id),
                 ('product_id','=',False)]
            )

            prod = self.env['product.product'].search([('id','=',int(record.product_variants))])

            attribute = prod.attribute_value_ids
            #########################
#             print "BOM FOR BOM CHANGE: ", bom_id
#             print "BOM 2 FOR BOM CHANGE: ", bom_id_2
            #########################

            record.bom_prod = product.id

            for bom_record in bom_id_2:
                for line in bom_record.bom_line_ids:
                    if line.attribute_value_ids == attribute:
#                         print "BOM: ", bom_record
                        record.bom = bom_record.id
                        record.bom_lines = bom_record.bom_line_ids
                        return
#                     print "ATTRITUBUTES: ", line.attribute_value_ids

            record.bom = bom_id.id
            record.bom_lines = bom_id.bom_line_ids

#             for line in record.bom_lines:
#                 print "LINE ATTRIBUTES: ", line.attribute_value_ids




#             print "MATERIAL REQUIREMENT LINE PRODUCT: ", record.material_requirement_line._fields

#             vals = {
#                     'product_id':[],
#                     }
#
#             material = self.env['material.requirement.line']
#
#             for line in bom_id.bom_line_ids:
#                 vals['product_id'].append(line.product_id)
#                 print "APPENDED VALUES :", vals['product_id']
#
#             for value in vals['product_id']:
#                 record.material_requirement_line = self.create_requirement_lines(value)
#
#                 material += record.material_requirement_line
#
#             print "MATERIAL", material
#             for i in material:
#                 print "MATERIAL LINES HERE"
#                 print i.product_id
#                 print i.product_availability

#             record.material_requirement_line = material

#             return {'domain': {'bom': [('product_tmpl_id.id', '=',product.id)]}}


    @api.onchange('product_variants')
    def calculate_requirement(self):
        """Calculate requirement for product"""
        product_id = int(self.product)
#         for rec in self:
#             for prod in self._fields['product']._description_selection(self.env):
#                 print "PRODUCT ID", prod
        product = self.env['product.product'].search([
            ('id','=',int(product_id))
        ])

        multiplier = 0
        smallest_multiplier = []

        for record in self:
            if record.bom:
                record.qty_to_manufacture = self.calculate_bom_lines(self.bom.bom_line_ids)
#                 record.calculate_bom_lines(self.bom.bom_line_ids)

#     @api.model
#     def check_bom(self, product):
# #         print "product id is: ", product
#         product = self.env['product.product'].search([('id','=',product)])
# #         print "PRODUCT HERE", product.name
# #         print "PRODUCT AVAILABILITY: ", product.qty_available
#         if product.bom_ids:
#             print "PRODUCT HAS BOM"
#             for line in product.bom_ids.bom_line_ids:
#                 self.check_bom(line.product_id.id)

    #USE THIS FUNCTION TO CALCULATE ALL BOM LINES
    def calculate_bom_lines(self, bom_lines):
        multiplier = 0
        smallest_multiplier = []

        for line in bom_lines:
            line_qty = line.product_qty
            wares = self.env['product.product'].\
                search([('id','=',line.product_id.id)]).qty_available

#             print "CHECK IF BOM LINE PRODUCT HAS BOM: ", self.check_bom(line.product_id.id)

#             print "IN WARES: ", wares
            multiplier = int(wares / line_qty)

#             print "MULTIPLIER", multiplier

            smallest_multiplier.append(multiplier)

#         print "SMALLEST MULTIPLIER", smallest_multiplier


        print "MIN SMALLST MULTIPLIER", min(smallest_multiplier)

        return min(smallest_multiplier)


#         self.qty_to_manufacture = min(smallest_multiplier)

#         for record in self:
#             record._calculate_promised()


#     @api.onchange('requirement')
#     def assign_requirement(self):
#         """Assign requirement"""
#         for rec in self:
#             for product_id in self._fields['requirement']._description_selection(self.env):
#                 print "PRODUCT ID", product_id







