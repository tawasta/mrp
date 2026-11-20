.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================
MRP multi level optimization
============================

* This module optimizes the time usage of the code in MRP multi level
* The low level codes (LLC) of the products are calculated level by level
  and saved with a few SQL updates instead of one ORM write per level
* The time used by the calculation is written to the server log

Configuration
=============
\-

Usage
=====
* Go to Apps to install this module
* Run MRP Multi Level as before

Known issues / Roadmap
======================
\-

Changes from version 17
=======================
* The calculation stops at the same recursion limit as MRP multi level
  (system parameter mrp_multi_level.llc_calculation_recursion_limit,
  default 20), so a BoM cycle between active BoMs cannot loop forever

Credits
=======

Contributors
------------

* Jarmo Kortetjärvi <jarmo.kortetjarvi@tawasta.fi>
* Timo Kekäläinen <timo.kekalainen@tawasta.fi>
* Miika Nissi <miika.nissi@tawasta.fi>
* Valtteri Lattu <valtteri.lattu@futural.fi>

Maintainer
----------

.. image:: http://tawasta.fi/templates/tawastrap/images/logo.png
   :alt: Oy Tawasta OS Technologies Ltd.
   :target: http://tawasta.fi/

This module is maintained by Oy Tawasta OS Technologies Ltd.
