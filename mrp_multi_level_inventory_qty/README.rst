.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================
Inventory Turnover report
=========================

Use this module together with ABC functionality. A new menu is
created, "Inventory Turnover". Click it to open a pop up (wizard)
to create a report by filtering products. Filtering is possible
by product category, ABC profile of a product or ABC level of a
product. Filters can also be combined. Or just select one product.

Main idea is to use SQL level of computation to quickly get values
for the pivot view. There are several columns whose results are
calculated from linked data of a product:

* Quantity Now: Available quantity calculated from value layers
* Value now: Stock value of a product. Computed from value layers
* Demand Quantity: Demand quantity according to a selected days range.
  This is selected in the wizard. MRP Moves of a product are used
  for computing this result.
* Demand Value: Demand quantity multiplied by a product cost and -1 to
  show (usually) a positive value
* Coverage in Days: The sufficiency of a product for a given days range.
  It is computed by:

  (<Quantity Now> / <Demand Quantity>) * <Days range>

  Note that <Days range> is an integer
* Inventory Turnover: Same as Coverage in Days, but 365 is divided by
  the yearlier result, thus:

  365 / ((<Quantity Now> / <Demand Quantity>) * <Days range>)

Be wary to change something in the SQL computation. Many things there
are used to make code run faster and to avoid computing same things
more than once. Note how "with clause" helps in this by computing
results to temporary tables. "read_group" is used to insert proper
column sum values to Coverage in Days and Inventory Turnover.

Configuration
=============
\-

Usage
=====
\-

Known issues / Roadmap
======================
\-

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
