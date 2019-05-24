.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============================
BOM Component Cost Calculation 
==============================

* Shows the cost of BOM based on its components' prices

Configuration
=============
* Go to MRP settings and define whether the calculation should be based on the
  cost price of the product or the price of the primary vendor

Usage
=====
* Open a BOM form view to see its costs
* A scheduled action calculates the prices of all BOMs once a day
* You can also click the Update Cost button to see the up-to-date cost info

Known issues / Roadmap
======================
* It should be tested in a large 10.0 installation if dynamic calculation of
  BOM costs works OK in 10.0, this would eliminate the need for a cron and a
  manual button click that the module currently uses as a calculation trigger
* In 9.0 dynamic calculation would cause a KeyError in cache, somehow related
  to this issue/comment:
  https://github.com/odoo/odoo/issues/7326#issuecomment-160159561.

Credits
=======

Contributors
------------
* Jaakko Komulainen <jaakko.komulainen@vizucom.com>
* Timo Talvitie <timo.talvitie@tawasta.fi>

Maintainer
----------

.. image:: https://tawasta.fi/templates/tawastrap/images/logo.png
   :alt: Oy Tawasta OS Technologies Ltd.
   :target: https://tawasta.fi/

This module is maintained by Oy Tawasta OS Technologies Ltd.
