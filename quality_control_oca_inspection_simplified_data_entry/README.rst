.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================================================
Quality Control OCA: Simplified Inspection Data Entry
=====================================================

* Adds simplified step-by-step views for answering inspections' questions.
* Use case: entering answers for an inspection's questions
  can be inconvenient especially with `quality_control_oca_inspection_line_freetext_value`
  since there are three different value columns on the inspection form (qualitative,
  quantitative, freetext), and it depends on the test question type which of
  these should be filled in. Also horizontal space begins to get crowded
  on a smaller screen.

Configuration
=============
* Set up a QC test as usal

Usage
=====
* Create an inspection for a test and mark it as todo. Launch the data 
  entry views from the "Fill in Answers" button on the inspection
  form. After each answer you can click "Save & Next" to jump through
  all of the test's questions one by one. 
* Adding the answers as before via the inspection lines field is still possible,
  just show the fields that have been marked with `optional=hide` for space 
  saving purposes by this module.

Known issues / Roadmap
======================
* Radio buttons are used for showing the full list of quantitative
  answer options to the user so they don't need to click a dropdown first
  to see what is available.
  Consider making radio/dropdown a configurable option, for use cases
  where there is a huge amount of options per test question.
* The module also depends on `quality_control_oca_inspection_line_freetext_value`.
  Moving the freetext value support functionality into a new
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
