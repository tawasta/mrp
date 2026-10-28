.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================
Hazard Residual Risk Number
===========================

* Adds a "Risk number" field to the residual risk evaluations. It is computed
  in the same way as the risk of the hazard and is shown on the Residual Risk
  Evaluations tab.
* Adds a "Residual risk numbers" column to the hazard list. A hazard can have
  several residual risk evaluations, so the column lists all their risk
  numbers, for example "3, 6, 9". Risk numbers that cannot be computed are left
  out.

Configuration
=============
\-

Usage
=====
* Open a hazard and go to the Residual Risk Evaluations tab. Select the
  probability, severity and occupation / usage of a line to see its risk
  number.
* The risk numbers of the residual risk evaluations are shown in the hazard
  list.

Known issues / Roadmap
======================
\-

Credits
=======

Contributors
------------

* Valtteri Lattu <valtteri.lattu@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
   :alt: Futural Oy
   :target: https://futural.fi/

This module is maintained by Futural Oy
