
=============
Vision Stock
=============

Customisation for the picking process of Vision Stationery
Alitec Pte Ltd
Last update: 29 Apr 2019

Configuration
=============

There can be only three warehouses:
- 1 x automated station. Its name must contained the word **"Automated"**
- 1 x normal warehouse
- 1 x Shipping station

The shipping station must have two supply routes:
- "Automated": from the automated station
- "Normal": and one from the normal warehouse

The shipping station must be configured with two steps shipments: pick/pack and ship
The operation type for pick/pack must contain the work **"Pick"**

Usage
=====
A stock request can be created for several pickings

Odoo will search in the automated station if there is enough quantity to fulfill:
- YES: the stock request will be created using the route: Automated
- NO: the stock request will be created using the route: Normal
