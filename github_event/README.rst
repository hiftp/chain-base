Github Events
=============

This modules defines what is a GitHub event (as an Odoo object).

.. contents:: Table of Contents

Events
------
As system administrator, I go to ``Configuration > Technical > GitHub > Events``.

.. image:: static/description/menu_technical_events.png

I see the list of events:

.. image:: static/description/event_tree.png

I open the form view of an event.

.. image:: static/description/event_form.png

Process Button
--------------
The ``Process`` button in the form view of events triggers the parsing of the payload.

.. image:: static/description/event_form_process_button.png

When no extra module is installed, only the ``Action`` is filled.

Clicking multiple times on the button is idempotent.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
