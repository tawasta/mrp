.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================================
Create Log lines from BoM cost computation
==========================================

This module was created to keep an account of how computed BoM cost prices
develop over time. Product variant has "Compute BoM cost logs" -field that
is used to mark the products to which log lines a created.

BoM cost logs menu can be found by going to Manufacturing --> Reporting
--> BoM cost logs. There are all the created log lines.

Product specific log lines can be seen from "BoM cost logs" button. This
button is shown on a product if that product has any log lines linked to it.

The log lines are created upon BoM cost computation.

Configuration
=============
Configure the products which should use BoM cost logs.
Users with Manufacturing / User group can see the logs.
Admin users can delete logs.

Usage
=====
This module is meant to be used with mrp_bom_cost_cron module, but
it also works without it. However the scheduled action created by
that module makes creating logs easier, because it goes through a
bunch of products.

Use "Compute BoM cost logs" -field on product variant to mark the
products and create logs for those products.

Known issues / Roadmap
======================

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
