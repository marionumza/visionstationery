Last update: 5 May 2019

=============
Vision Stock
=============

This customisation is designed for a very specific configuration and business case. It handles a scenario with three warehouses, with one acting as a shipping station, and two supply warehouses.

* The goods are delivered to the supply warehouses from vendors
* one of the supply warehouse is automated by a robot
* the other is a general warehouse
* All goods are shipped to customers from the shipping station, which is resupplied from both other warehouses

The general features are:

* a customised logic handles the assignement of the supply route (from automated or from normal warehouse)
* a customised logic handles the selecting of similar customer DO, to create a combined stock request - TODO
* The scheduler can be configured for frequency and quantity - TODO


Configuration
=============

There can be only three warehouses:

* 1 x automated station. Its name must contained the word **"Automated"**
* 1 x normal warehouse
* 1 x Shipping station

The shipping station must have two supply routes:

* "Automated": from the automated station
* "Normal": and one from the normal warehouse

The shipping station must be configured with two steps shipments: pick/pack and ship and the operation type for pick/pack must contain the work **"Pick"**

An optional config value for the default number of similar lines to be selected can be entered in the ir_config

* key: default_nb_similar_line
* value: integer


Usage
=====
A stock request can be created for several pickings

Odoo will search in the automated station if there is enough quantity to fulfill:

* YES: the stock request will be created using the route: Automated
* NO: the stock request will be created using the route: Normal
