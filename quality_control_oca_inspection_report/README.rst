.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================================
Quality Control OCA: Inspection PDF Report
==========================================

* Adds PDF printing functionality for the inspection records to the
  `quality_control_oca` module.

Configuration
=============
* Settings -> Quality Control Report -> Inspection Report:

  * Report title and section headings (per company).
  * "Trim Trailing Decimals" - when enabled, quantitative result values on
    the PDF drop insignificant trailing zeros (`12.3` instead of
    `12.3000`). 

Usage
=====
* Log a QC inspection as usual. The new PDF can be found in the print menu.

Known issues / Roadmap
======================
* The module also depends on `quality_control_oca_inspection_line_freetext_value`
  for supporting giving freetext answers to inspections' test questions
  and showing them on the PDF. Moving this functionality into a new
  glue module is straightforward to do if the need for module separation 
  ever arises.

Credits
=======

Contributors
------------

* Timo Talvitie <timo.talvitie@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
        :alt: Futural Oy
        :target: https://futural.fi/

This module is maintained by Futural Oy
