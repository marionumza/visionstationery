Last update: 14 May 2019

=============
Vision Stock
=============

This customisation is designed for a very specific configuration and business case. It handles a scenario with several warehouses, with one acting as a shipping station, and several supply warehouses.

* The goods are delivered to the supply warehouses from vendors
* one of the supply warehouse is automated has priority (it must be : priority = 1)
* Other supply warehouses have lower priority (e.g. priority > 1)
* All goods are shipped to customers from the shipping station, which is resupplied from other warehouses

The general features are:

* a customised logic handles the assignement of the supply route : from automated (priority = 1) or from other warehouses
* a customised logic handles the selecting of similar customer DO, to create a combined stock request - TODO
* The scheduler can be configured for frequency and quantity - TODO


Configuration
=============

A typical set up would be four warehouses:

* 1 x automated station (priority = 1)
* 1 x normal warehouse - Area A (priority = 2)
* 1 x normal warehouse - Area B (priority = 3)
* 1 x Shipping station (priority = 10)

The shipping station must have three supply routes:

* "Automated": from the automated station - request rule = True, sequence = 1
* "Area A": and one from the warehouse Area A - request rule = True, sequence = 2
* "Area B": and one from the warehouse Area B - request rule = True, sequence = 3

The shipping station must be configured with two steps shipments: pick/pack and ship

An optional config value for the default number of similar lines to be selected can be entered in the ir_config

* key: default_nb_similar_line
* value: integer


Usage
=====
A stock request can be created for several pickings

Odoo will search in the station with priority=1 if there is enough quantity to fulfill:

* YES: the stock request will be created using the route: Automated
* NO: the stock request will search through all the other warehouse, which one would have enough qty

#TODO: add the default warehouse in the product record? would that not be too complicated to set up?

