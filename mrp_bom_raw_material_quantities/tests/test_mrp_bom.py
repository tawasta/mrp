# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestBom(TransactionCase):

    def setUp(self):
        '''Set up some test data. This will be
        available for all the actual test methods'''
        res = super(TestBom, self).setUp()
        product_model = self.env['product.product']

        self.uom_unit = self.env.ref('product.product_uom_unit')
        self.uom_dozen = self.env.ref('product.product_uom_dozen')

        self.main_assembly_1 = product_model.create({
            'name': 'Main assembly 1',
            'purchase_line_warn': 'no-message'})

        self.main_assembly_2 = product_model.create({
            'name': 'Main assembly 2',
            'purchase_line_warn': 'no-message'})

        self.subassembly_1 = product_model.create({
            'name': 'Sub-assembly 1',
            'purchase_line_warn': 'no-message'})

        self.subassembly_2 = product_model.create({
            'name': 'Sub-assembly 2',
            'purchase_line_warn': 'no-message'})

        self.subassembly_3 = product_model.create({
            'name': 'Sub-assembly 3',
            'purchase_line_warn': 'no-message'})

        self.component_1 = product_model.create({
            'name': 'Component 1',
            'purchase_line_warn': 'no-message'})

        self.component_2 = product_model.create({
            'name': 'Component 2',
            'purchase_line_warn': 'no-message'})

        self.component_3 = product_model.create({
            'name': 'Component 3',
            'purchase_line_warn': 'no-message'})

        self.component_4 = product_model.create({
            'name': 'Component 4',
            'uom_id': self.uom_dozen.id,
            'purchase_line_warn': 'no-message'})

        return res


    def test_empty_bom(self):
        '''A bom with no lines'''
        bom_res = self.env['mrp.bom'].create({
            'product_tmpl_id': self.main_assembly_1.product_tmpl_id.id
        })
        res = bom_res.compute_raw_material_qties()
        self.assertEqual(res, [], 'Empty bom should have no quantities!')


    def test_single_level_bom(self):
        '''A bom with no sub-assemblies'''
        # Main assembly
        #  - Component1 x 5
        #  - Component2 x 5
        #  - Component2 x 5

        bom_res = self.env['mrp.bom'].create({
            'product_tmpl_id': self.main_assembly_1.product_tmpl_id.id
        })
        self.env['mrp.bom.line'].create({
            'bom_id': bom_res.id,
            'product_id': self.component_1.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 5
        })
        self.env['mrp.bom.line'].create({
            'bom_id': bom_res.id,
            'product_id': self.component_2.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 5
        })
        self.env['mrp.bom.line'].create({
            'bom_id': bom_res.id,
            'product_id': self.component_2.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 5
        })
        res = bom_res.compute_raw_material_qties()
        self.assertItemsEqual(res,
            [{ 'product': self.component_1, 'quantity': 5},
             { 'product': self.component_2, 'quantity': 10}],
            'Component quantities do not match')


    def test_subassembly(self):
        '''A bom with a single sub-assembly'''
        # Main assembly
        #  - Component1 x 10
        #  - Component2 x 20
        #  - Sub-assembly1 x 1
        #    - Component1 x 10
        #    - Component3 x 30

        subassembly_1_bom_res = self.env['mrp.bom'].create({
            'product_tmpl_id': self.subassembly_1.product_tmpl_id.id
        })
        self.env['mrp.bom.line'].create({
            'bom_id': subassembly_1_bom_res.id,
            'product_id': self.component_1.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 10
        })
        self.env['mrp.bom.line'].create({
            'bom_id': subassembly_1_bom_res.id,
            'product_id': self.component_3.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 30
        })

        main_assembly_1_bom_res = self.env['mrp.bom'].create({
            'product_tmpl_id': self.main_assembly_1.product_tmpl_id.id
        })
        self.env['mrp.bom.line'].create({
            'bom_id': main_assembly_1_bom_res.id,
            'product_id': self.component_1.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 10
        })
        self.env['mrp.bom.line'].create({
            'bom_id': main_assembly_1_bom_res.id,
            'product_id': self.component_2.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 20
        })
        self.env['mrp.bom.line'].create({
            'bom_id': main_assembly_1_bom_res.id,
            'product_id': self.subassembly_1.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 1
        })
        res = main_assembly_1_bom_res.compute_raw_material_qties()
        self.assertItemsEqual(res,
            [{ 'product': self.component_1, 'quantity': 20},
             { 'product': self.component_2, 'quantity': 20},
             { 'product': self.component_3, 'quantity': 30}],
            'Component quantities do not match')

    def test_subassembly_with_multiplier(self):
        '''A bom with a single sub-assembly that is required more than once.
        Check that the end component quantities are multiplied correctly'''
        # Main assembly
        #  - Component1 x 10
        #  - Component2 x 20
        #  - Sub-assembly1 x 2
        #    - Component1 x 10
        #    - Component3 x 30

        subassembly_1_bom_res = self.env['mrp.bom'].create({
            'product_tmpl_id': self.subassembly_1.product_tmpl_id.id
        })
        self.env['mrp.bom.line'].create({
            'bom_id': subassembly_1_bom_res.id,
            'product_id': self.component_1.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 10
        })
        self.env['mrp.bom.line'].create({
            'bom_id': subassembly_1_bom_res.id,
            'product_id': self.component_3.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 30
        })

        main_assembly_1_bom_res = self.env['mrp.bom'].create({
            'product_tmpl_id': self.main_assembly_1.product_tmpl_id.id
        })
        self.env['mrp.bom.line'].create({
            'bom_id': main_assembly_1_bom_res.id,
            'product_id': self.component_1.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 10
        })
        self.env['mrp.bom.line'].create({
            'bom_id': main_assembly_1_bom_res.id,
            'product_id': self.component_2.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 20
        })
        self.env['mrp.bom.line'].create({
            'bom_id': main_assembly_1_bom_res.id,
            'product_id': self.subassembly_1.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 2
        })
        res = main_assembly_1_bom_res.compute_raw_material_qties()
        self.assertItemsEqual(res,
            [{ 'product': self.component_1, 'quantity': 30},
             { 'product': self.component_2, 'quantity': 20},
             { 'product': self.component_3, 'quantity': 60}],
            'Component quantities do not match')

    def test_complex_multilevel_subassembly(self):
        '''A bom with a multilevel structure where same subassembly is used
        multiple times'''
        # Main assembly
        #  - Component1 x 1 units
        #  - Component2 x 2 units
        #  - Sub-assembly1 x 2 units
        #    - Component1 x 1 units
        #    - Component3 x 3 units
        #  - Sub-assembly2 x 2 units
        #    - Component1 x 1 units
        #    - Component3 x 3 units
        #    - Sub-assembly3 x 3 units
        #      - Component2 x 2 units
        #      - Sub-assembly1 x 2 units
        #        - Component1 x 1 units
        #        - Component3 x 3 units
        #
        # Expected totals:
        # - Component 1: 1 + (2*1) + (2*1) + (2*3*2*1) = 17
        # - Component 2: 2 + (2*3*2) = 14
        # - Component 3: (2*3) + (2*3) + (2*3*2*3) = 48

        subassembly_1_bom_res = self.env['mrp.bom'].create({
            'product_tmpl_id': self.subassembly_1.product_tmpl_id.id
        })
        self.env['mrp.bom.line'].create({
            'bom_id': subassembly_1_bom_res.id,
            'product_id': self.component_1.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 1
        })
        self.env['mrp.bom.line'].create({
            'bom_id': subassembly_1_bom_res.id,
            'product_id': self.component_3.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 3
        })

        subassembly_3_bom_res = self.env['mrp.bom'].create({
            'product_tmpl_id': self.subassembly_3.product_tmpl_id.id
        })
        self.env['mrp.bom.line'].create({
            'bom_id': subassembly_3_bom_res.id,
            'product_id': self.component_2.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 2
        })
        self.env['mrp.bom.line'].create({
            'bom_id': subassembly_3_bom_res.id,
            'product_id': self.subassembly_1.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 2
        })

        subassembly_2_bom_res = self.env['mrp.bom'].create({
            'product_tmpl_id': self.subassembly_2.product_tmpl_id.id
        })
        self.env['mrp.bom.line'].create({
            'bom_id': subassembly_2_bom_res.id,
            'product_id': self.component_1.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 1
        })
        self.env['mrp.bom.line'].create({
            'bom_id': subassembly_2_bom_res.id,
            'product_id': self.component_3.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 3
        })
        self.env['mrp.bom.line'].create({
            'bom_id': subassembly_2_bom_res.id,
            'product_id': self.subassembly_3.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 3
        })

        main_assembly_1_bom_res = self.env['mrp.bom'].create({
            'product_tmpl_id': self.main_assembly_1.product_tmpl_id.id
        })
        self.env['mrp.bom.line'].create({
            'bom_id': main_assembly_1_bom_res.id,
            'product_id': self.component_1.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 1
        })
        self.env['mrp.bom.line'].create({
            'bom_id': main_assembly_1_bom_res.id,
            'product_id': self.component_2.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 2
        })
        self.env['mrp.bom.line'].create({
            'bom_id': main_assembly_1_bom_res.id,
            'product_id': self.subassembly_1.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 2
        })
        self.env['mrp.bom.line'].create({
            'bom_id': main_assembly_1_bom_res.id,
            'product_id': self.subassembly_2.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 2
        })

        res = main_assembly_1_bom_res.compute_raw_material_qties()
        self.assertItemsEqual(res,
            [{ 'product': self.component_1, 'quantity': 17},
             { 'product': self.component_2, 'quantity': 14},
             { 'product': self.component_3, 'quantity': 48}],
            'Component quantities do not match')


    def test_uom_conversion(self):
        '''A BOM where different UoMs are used for same component'''
        # Main assembly
        #  - Component1 x 10 units
        #  - Component2 x 20 units
        #  - Sub-assembly1 x 2 units
        #    - Component1 x 2 dozen (=24 units)
        #    - Component3 x 30 units

        subassembly_1_bom_res = self.env['mrp.bom'].create({
            'product_tmpl_id': self.subassembly_1.product_tmpl_id.id
        })
        self.env['mrp.bom.line'].create({
            'bom_id': subassembly_1_bom_res.id,
            'product_id': self.component_1.id,
            'product_uom_id': self.uom_dozen.id,
            'product_qty': 2
        })
        self.env['mrp.bom.line'].create({
            'bom_id': subassembly_1_bom_res.id,
            'product_id': self.component_3.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 30
        })

        main_assembly_1_bom_res = self.env['mrp.bom'].create({
            'product_tmpl_id': self.main_assembly_1.product_tmpl_id.id
        })
        self.env['mrp.bom.line'].create({
            'bom_id': main_assembly_1_bom_res.id,
            'product_id': self.component_1.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 10
        })
        self.env['mrp.bom.line'].create({
            'bom_id': main_assembly_1_bom_res.id,
            'product_id': self.component_2.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 20
        })
        self.env['mrp.bom.line'].create({
            'bom_id': main_assembly_1_bom_res.id,
            'product_id': self.subassembly_1.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 2
        })

        res = main_assembly_1_bom_res.compute_raw_material_qties()
        self.assertItemsEqual(res,
            [{ 'product': self.component_1, 'quantity': 58},
             { 'product': self.component_2, 'quantity': 20},
             { 'product': self.component_3, 'quantity': 60}],
            'Dozen to Unit conversion failed, quantities do not match')


    def test_reverse_uom_conversion(self):
        '''A BOM where line uses Units but the product has another UoM
        as its default UOM '''
        # Main assembly
        #  - Component1 x 10 units
        #  - Component4 x 18 units (=1.5 dozen)

        main_assembly_1_bom_res = self.env['mrp.bom'].create({
            'product_tmpl_id': self.main_assembly_1.product_tmpl_id.id
        })
        self.env['mrp.bom.line'].create({
            'bom_id': main_assembly_1_bom_res.id,
            'product_id': self.component_1.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 10
        })
        self.env['mrp.bom.line'].create({
            'bom_id': main_assembly_1_bom_res.id,
            'product_id': self.component_4.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 18
        })

        res = main_assembly_1_bom_res.compute_raw_material_qties()
        self.assertItemsEqual(res,
            [{ 'product': self.component_1, 'quantity': 10 },
             { 'product': self.component_4, 'quantity': 1.5}],
            'Unit to Dozen conversion failed, quantities do not match')


    def test_two_boms(self):
        '''Recordset with two boms'''

        '''A bom with no sub-assemblies'''
        # Main assembly
        #  - Component1 x 5
        #  - Component2 x 5
        #  - Component2 x 5

        # Main assembly 2
        #  - Component1 x 5
        #  - Sub-assembly1 x1
        #    - Component2 x 2
        #    - Component3 x 3

        # Totals:
        # - Component 1: 10
        # - Component 2: 12
        # - Component 3: 3

        subassembly_1_bom_res = self.env['mrp.bom'].create({
            'product_tmpl_id': self.subassembly_1.product_tmpl_id.id
        })
        self.env['mrp.bom.line'].create({
            'bom_id': subassembly_1_bom_res.id,
            'product_id': self.component_2.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 2
        })
        self.env['mrp.bom.line'].create({
            'bom_id': subassembly_1_bom_res.id,
            'product_id': self.component_3.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 3
        })


        main_assembly_1_bom_res = self.env['mrp.bom'].create({
            'product_tmpl_id': self.main_assembly_1.product_tmpl_id.id
        })
        self.env['mrp.bom.line'].create({
            'bom_id': main_assembly_1_bom_res.id,
            'product_id': self.component_1.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 5
        })
        self.env['mrp.bom.line'].create({
            'bom_id': main_assembly_1_bom_res.id,
            'product_id': self.component_2.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 5
        })
        self.env['mrp.bom.line'].create({
            'bom_id': main_assembly_1_bom_res.id,
            'product_id': self.component_2.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 5
        })

        main_assembly_2_bom_res = self.env['mrp.bom'].create({
            'product_tmpl_id': self.main_assembly_2.product_tmpl_id.id
        })
        self.env['mrp.bom.line'].create({
            'bom_id': main_assembly_2_bom_res.id,
            'product_id': self.component_1.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 5
        })
        self.env['mrp.bom.line'].create({
            'bom_id': main_assembly_2_bom_res.id,
            'product_id': self.subassembly_1.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 1
        })

        recordset = self.env['mrp.bom'].browse([main_assembly_1_bom_res.id,
                                                main_assembly_2_bom_res.id])

        res = recordset.compute_raw_material_qties()
        self.assertItemsEqual(res,
            [{ 'product': self.component_1, 'quantity': 10},
             { 'product': self.component_2, 'quantity': 12},
             { 'product': self.component_3, 'quantity': 3}],
            'Component quantities do not match')

    def test_same_bom_twice(self):
        '''Three-BOM recordset with the same BOM twice'''
        # Main assembly
        #  - Component1 x 5
        #  - Component2 x 5
        #  - Component2 x 5

        # Main assembly 2 twice
        #  - Component1 x 5
        #  - Sub-assembly1 x1
        #    - Component2 x 2
        #    - Component3 x 3

        # Totals:
        # - Component 1: 15
        # - Component 2: 14
        # - Component 3: 6

        subassembly_1_bom_res = self.env['mrp.bom'].create({
            'product_tmpl_id': self.subassembly_1.product_tmpl_id.id
        })
        self.env['mrp.bom.line'].create({
            'bom_id': subassembly_1_bom_res.id,
            'product_id': self.component_2.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 2
        })
        self.env['mrp.bom.line'].create({
            'bom_id': subassembly_1_bom_res.id,
            'product_id': self.component_3.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 3
        })


        main_assembly_1_bom_res = self.env['mrp.bom'].create({
            'product_tmpl_id': self.main_assembly_1.product_tmpl_id.id
        })
        self.env['mrp.bom.line'].create({
            'bom_id': main_assembly_1_bom_res.id,
            'product_id': self.component_1.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 5
        })
        self.env['mrp.bom.line'].create({
            'bom_id': main_assembly_1_bom_res.id,
            'product_id': self.component_2.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 5
        })
        self.env['mrp.bom.line'].create({
            'bom_id': main_assembly_1_bom_res.id,
            'product_id': self.component_2.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 5
        })

        main_assembly_2_bom_res = self.env['mrp.bom'].create({
            'product_tmpl_id': self.main_assembly_2.product_tmpl_id.id
        })
        self.env['mrp.bom.line'].create({
            'bom_id': main_assembly_2_bom_res.id,
            'product_id': self.component_1.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 5
        })
        self.env['mrp.bom.line'].create({
            'bom_id': main_assembly_2_bom_res.id,
            'product_id': self.subassembly_1.id,
            'product_uom_id': self.uom_unit.id,
            'product_qty': 1
        })

        recordset = self.env['mrp.bom'].browse([main_assembly_1_bom_res.id,
                                                main_assembly_2_bom_res.id,
                                                main_assembly_2_bom_res.id])

        res = recordset.compute_raw_material_qties()
        self.assertItemsEqual(res,
            [{ 'product': self.component_1, 'quantity': 15},
             { 'product': self.component_2, 'quantity': 14},
             { 'product': self.component_3, 'quantity': 6}],
            'Component quantities do not match')