# -*- coding: utf-8 -*-


from __future__ import division
from odoo import api, fields, models




class MaterialLevel(models.Model):

    _name = 'manufacturing.level'

    name = fields.Char()



class MaterialRequirement(models.Model):

    _name = 'material.requirement'
    _description = 'Material Requirement'


    name = fields.Char(
            )

#     manufacturing_level = fields.Many2one(
#             'manufacturing.level',
# #             ('level_one', 'Manufacture first BOM level'),
# #             ('level_two', 'Manufacture first and second BOM level')],
#             string='Manufacturing level',
#             )


#     manufacturing_level = fields.Selection([
#             (True, 'level_one'),
# #             ('level_one', 'Manufacture first BOM level'),
#             (False, 'Manufacture first and second BOM level')],
#             string='Manufacturing level',
#             )

    manufacturing_level = fields.Boolean(
            string="Include second level BOM also?",
            )

    product = fields.Many2one(
            comodel_name='product.template',
            string="Product",
            domain=[('bom_ids','!=',False)]
            )

    product_attribute_name = fields.Char(
            string="Product Attributes",
#             _compute="_calculate_promised",
            )

    product_variant_id = fields.Integer(
            string="Product Variant ID",
            _compute="_get_product_variant_id",
            )

#     product_values = fields.Char(
#             string="Product Attribute Values",
#             _compute="_calculate_promised",
#             )

    requirement = fields.Float(
            string='Requirement',
            )

    qty_to_manufacture = fields.Float(
            string="Quantity to Manufacture",
            readonly=True,
            )

    qty_available = fields.Float(
            string="Available quantity",
            compute='_calculate_availability',
            )

    qty_promised = fields.Float(
            string="Promised Quantity",
            compute='_calculate_promised',
            )

    bom = fields.Many2one(
            comodel_name='mrp.bom',
            string='BoM'
            )

    bom_lines = fields.Many2many(
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
            )

    bom_qty_available = fields.Float(
            string="Available quantity",
            compute='_calculate_availability',
            )

    material_requirement_line = fields.One2many(
            'material.requirement.line',
            'material_requirement_id',
            string='Material Requirement Line',
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
            print "PRODUCT VARIANTS ON ONCHANGE IS: ", record.product_variants
            product = self.env['product.product'].search([
                ('id','=',int(record.product_variants))
            ])

#             record.product_attribute_name = record.product_variants.attribute_value_ids

#             print "RECORD ATTRIBUTE VALUE IDS ", record.product_variants.attribute_value_ids.ids

            record.qty_promised = product.qty_available + record.qty_to_manufacture

    @api.onchange('product_variants')
    def _calculate_availability(self):
        for record in self:
            product = self.env['product.product'].search([
                ('id','=',int(record.product_variants))
            ])


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
                    record.product_variants = variant
                    record.product_variant_id = variant.id
        self.get_material_requirement_line()


    @api.onchange('product_variants')
    def _get_product_variant_id(self):
        """Get product variant id"""
        for record in self:
            record.product_variant_id = record.product_variants.id
#             print "PRODUCT VARIANT ID :", record.product_variant_id

    def create_requirement_lines(self, vals):
        """Create Requirement Lines using BoM values"""
        requirement_lines = self.env['material.requirement.line']

        values = []

        print "ALL ELEMS ARE HERE: ", all(elem in self.product_variants.attribute_value_ids.ids for elem in vals.attribute_value_ids.ids)
#         if not all(elem in self.product_variants.attribute_value_ids.ids for elem in vals.attribute_value_ids.ids):
#             return

        for i in vals.attribute_value_ids:
            values.append(i.display_name)

        attributes = vals.attribute_value_ids.mapped('display_name')

        if attributes == []:
            attributes = ""
        else:
            attributes = ', '.join(attributes)

        if attributes.startswith("u'"):
            attributes = attributes.replace("u'", "'", 1)

        multiplier = 0
        smallest_multiplier = []

        if vals.product_id.bom_ids:
            print "THIS PRODUCT HAS A BOM"
            lines = vals.product_id.bom_ids.bom_line_ids

            for line in lines:
                if line.product_id.qty_available <= 0:
                    multiplier = 0
                else:
                    multiplier = int(line.product_id.qty_available / line.product_qty)
                smallest_multiplier.append(multiplier)

                if not smallest_multiplier:
                    multiplier = 0
                else:
                    multiplier = min(smallest_multiplier)

                print "SMALLEST MULTIPLIER", multiplier


        print "MANUFACTURING LEVEL: ", self.manufacturing_level

#         if self.manufacturing_level == 'level_two':
#             self.qty_to_manufacture += multiplier

        if not self.manufacturing_level:
            multiplier = 0

        result = {
                'product_id': vals.product_id.id,
                'product_availability': vals.product_id.qty_available,
                'variant': attributes,
                'qty_to_manufacture': vals.product_qty,
                'product_uom_id': vals.product_uom_id,
                'can_be_manufactured': multiplier,
                'promised_qty_line': multiplier + vals.product_id.qty_available,
                }

        print "RESULT", result

        return result


    @api.onchange('product_variants')
    def get_material_requirement_line(self):
        """"Get Material requirement line"""

        self._get_product_variant_id()

        mrp_bom = self.env['mrp.bom']

        value_line = []

        vals = {
                'product_id': "",
                'variant': "",
#                     'product_id':[],
#                     'variant':[],
                }

        get_name = self.env['product.product'].search([('id','=', self.product_variant_id)])

        bom_id = mrp_bom.search(
            ['&',
             ('product_tmpl_id.id','=', self.product.id),
             '|',
             ('product_id','=', self.product_variant_id),
             ('product_id','=', False)],limit=1
        )

        material = self.env['material.requirement.line']

        product_material_lines = []

        multiplier = 0
        smallest_multiplier = []

        multiplier_line = 0
        smallest_multiplier_line = []

        for line in bom_id.bom_line_ids:
            print "Creating a new requirement line..."
#             self.material_requirement_line += self.create_requirement_lines(line)
            if all(elem in self.product_variants.attribute_value_ids.ids for elem in line.attribute_value_ids.ids):
                product_material_lines.append(material.new(self.create_requirement_lines(line)).id)

                if self.manufacturing_level and line.product_id.bom_ids:
                    for child_bom_line in line.product_id.bom_ids.bom_line_ids:

                        if child_bom_line.product_id.qty_available <= 0:
                            multiplier_line = 0
                        else:
                            multiplier_line = int(child_bom_line.product_id.qty_available / child_bom_line.product_qty)
                        smallest_multiplier_line.append(multiplier_line)

                if line.product_id.qty_available <= 0:
                    multiplier = 0
                else:
                    multiplier = int(line.product_id.qty_available / line.product_qty)
                smallest_multiplier.append(multiplier)

        if not smallest_multiplier_line:
            multiplier_line = 0
        else:
            multiplier_line = min(smallest_multiplier_line)

        print "SMALLEST MULTIPLIER LINE", multiplier_line

        print "SMALLEST MULTIPLIER", min(smallest_multiplier)

        self.qty_to_manufacture = min(smallest_multiplier) + multiplier_line
        self.qty_promised = self.qty_available + self.qty_to_manufacture

        self.material_requirement_line = [(6, 0, product_material_lines)]


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

            record.bom_prod = product.id


            for bom_record in bom_id_2:
                for line in bom_record.bom_line_ids:
                    if line.attribute_value_ids == attribute:
                        record.bom = bom_record.id
                        record.bom_lines = bom_record.bom_line_ids
                        return
#                     print "ATTRITUBUTES: ", line.attribute_value_ids

            record.bom = bom_id.id
            record.bom_lines = bom_id.bom_line_ids

#             return {'domain': {'bom': [('product_tmpl_id.id', '=',product.id)]}}

    #USE THIS FUNCTION TO CALCULATE ALL BOM LINES

#     @api.onchange('requirement')
#     def assign_requirement(self):
#         """Assign requirement"""
#         for rec in self:
#             for product_id in self._fields['requirement']._description_selection(self.env):
#                 print "PRODUCT ID", product_id

