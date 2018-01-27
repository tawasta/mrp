.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================
BOM Raw Material Quantities
===========================

* Helper module that calculates the total raw material requirements of a BOM.
* Handles also sub-assemblies if the BOM has multiple levels
* The module does nothing on its own, you need to call the function from another
  module

Configuration
=============
\-

Usage
=====
* Call compute_raw_material_qties() function for a BOM recordset
* The return value is a list of raw materials and their total required quantities
* The quantities are represented in the UoM of the raw material. If the BoM uses
  another UoM, a conversion is made. (e.g. 1 Dozen on a BOM becomes 12 Unit(s),
  if Unit(s) is the material's UoM)
* Tip: if you need to calculate the total raw material requirements of
  e.g 2pcs of one BOM and 1pc of another, you can call the function with a
  recordset such as mrp.bom(460, 460, 58)

Known issues / Roadmap
======================
\-

Credits
=======

Contributors
------------
* Timo Talvitie <timo.talvitie@tawasta.fi>

Maintainer
----------

.. image:: http://tawasta.fi/templates/tawastrap/images/logo.png
   :alt: Oy Tawasta OS Technologies Ltd.
   :target: http://tawasta.fi/

This module is maintained by Oy Tawasta OS Technologies Ltd.