.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================================================================
Use Wizard and Scheduled action to create MRP Product Parameters
================================================================
::

    Module meant for developers to mass create MRP Product Parameters.

    A user can select products to open up a wizard to create parameters.
    Or use "Create MRP Product Parameters" named Scheduled action to
    create parameters to all stockable products. Stockable condition
    is the default, but it can be changed by adding a ir.config_parameter
    record with a list of product types, for example ["consu", "product"].

Configuration
=============
::

    None needed really, except if different product types are meant to be
    specified with "create_product_mrp_area_product_types" ir.config_parameter
    record.

Usage
=====
::

    Go to a product list to open up the wizard or use the scheduled action.
    This action is disabled by default.

Known issues / Roadmap
======================
::

    This module is meant to help used to create parameters. Therefore
    it should not cause any problems elsewhere.

Credits
=======

Contributors
------------

* Timo Kekäläinen <timo.kekalainen@tawasta.fi>

Maintainer
----------

.. image:: http://tawasta.fi/templates/tawastrap/images/logo.png
   :alt: Oy Tawasta OS Technologies Ltd.
   :target: http://tawasta.fi/

This module is maintained by Oy Tawasta OS Technologies Ltd.
