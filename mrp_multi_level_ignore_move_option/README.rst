.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================================================
MRP Multi Level – Option to ignore certain orders
=================================================

::

    Normally MRP demands are calculated with all possible demands and supplies
    per product. This module adds an option to exclude manufacturing orders
    from these calculations. There is also options to ignore sale and purchase
    orders from calculations.

    Only use the module if there is a good reason to exclude certain orders.
    Blanket oders from OCA's sale_blanket_order module create sale orders, which
    already create estimated procurements for manufacturing orders. Then these
    procurements are used in MRP demand calculations and it is better to opt-out
    the proper manufacturing orders from calculations.

Configuration
=============
::

    Choose MRP area and select some of these options:
    -Ignore manufacturing orders
    -Ignore purchase orders
    -Ignore sale orders

    This module is mainly used for excluding manufacturing orders.

Usage
=====
::

    Run MRP demand calculations with 'Ignore manufacturing orders' -option
    enabled. Manufacturing orders should not appear in MRP profiles after
    this.

    Or use some other option to exclude certain orders. These options
    can be enabled at the same time if needed.

Known issues / Roadmap
======================
::

    Check how the module bahaves in future versions.

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
