.. image:: images/logo.png

===================================================
HitPay Payment Gateway for Odoo E-commerce
===================================================

HitPay Payment Gateway for Odoo E-commerce is an open source module that links Odoo based e-commerce websites to HitPay Payment Gateway developed by https://www.hitpayapp.com/


Installation & Upgrade
======================

Download the latest module archive from https://github.com/hit-pay/odoo-extension/releases.

Now unzip the downloaded archive and copy the new payment_hitpay folder to Odoo addons directory. 

* [ODOO_ROOT_FOLDER]/server/odoo/addons/
* /var/lib/odoo/addons/[VERSION]/ (on Linux only)
* `addons_path` defined in odoo.conf

Then, youcan choose  one of these instructions:

* In your Odoo administrator interface, browse to "Configuration" tab. Here in, activate the developer mode.
* Or restart Odoo server with *sudo systemctl restart odoo* on Linux or by restarting Windows Odoo service.
  Odoo will update the applications list on startup.
*  Then browse to "Applications" tab and click on "Update applications list".
.. image:: images/1-App-Menu-Selection.png
.. image:: images/2-Click-Update-App-List.png

In your Odoo administrator interface, browse to "Applications" tab, delete "Applications" filter from
search field and search for "hitpay" keyword. Click "Install" (or "Upgrade") button of the "HitPay Payment Gateway Provider" module.

.. image:: images/3-Locate-HitPay-App-Click-Activate-Button-To-Install-App.png

Configuration
=============

* Go to "Website Admin" tab
.. image:: images/4-Website-Menu-Selection.png
* In "Configuration" section, expand "eCommerce" menu than click on "Payment Providers" entry
.. image:: images/5-Navigate-To-Payment-Providers.png
* Select HitPay Payment Gateway module
.. image:: images/6-Select-HitPay-Payment-Gateway.png
* You can now enter your HitPay Payment Gateway credentials
.. image:: images/7-Configure-Credentials.png
.. image:: images/8-Configure-Optional-Title-And-Icons.png

IMPORTANT
---------
* You should select a Payment Journal in the "Configuration" tab of the HitPay Payment Gateway
  to start using this payment method.
  
Checkout
=============
.. image:: images/9-Frontend-Checkout-Page-Choose-Hitpay.png

Payment Confirmation
--------------------
.. image:: images/10-Frontend-Payment-Confirmation.png

Sales Order
===========
Navigate to eCommerce Orders => Orders

.. image:: images/11-Sales-Order.png

Payment Transaction Details
===========================
Navigate to Configuration => eCommerce => Payment Transactions

.. image:: images/13-Payment-Transaction-Details.png

Refunds
===========================
* In the payment transaction, click the payment link eg: PBNK1/2023/00004
* You see the below screen and click the 'Refund' button and enter the amount to refund.
.. image:: images/14-Refund-Option.png
.. image:: images/15-Refund-Form.png

Change Log
==========
1.0.
--------------------
* Initial release.
