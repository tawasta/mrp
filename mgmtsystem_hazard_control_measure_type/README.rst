.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================
Hazard Control Measure Type
===========================

* Adds a "Type" field to the control measures of a hazard. It is shown on the
  Control Measures tab of the hazard form, in the control measure form and in
  the control measure list, and it can be searched.
* The values of the type are defined in the configuration. They are shared by
  all control measures, and each value belongs to a company.

Configuration
=============
* Go to Management System > Configuration > Hazards > Control Measure Types
  and create the types, for example "Technical" or "Administrative". The menu
  is available to the Management System managers.

Usage
=====
* Open a hazard, go to the Control Measures tab and add or edit a control
  measure. Select its type.
* A type that is in use cannot be deleted.

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
