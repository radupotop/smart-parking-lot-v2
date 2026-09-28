# Entity Relationship Diagram

This is the Entity Relationship Diagram (ERD) document.
Use a simple format to document relationships, for example.

```
Vehicles: id (int) | name (str) | price (decimal) | customer_id (FK -> Customers) | spots (M2M -> ParkingSpots)
```

* Where the types are 'natural' rather than strictly valid Python or SQL.
* Model names should always be plural (it's a collection).
* The relation between the tables/models should be explained by the FK/M2M relations.
* You can add comments below each model where necessary; start comments with `#`.
* DO NOT do ASCII art.
* DO NOT do mermaid diagrams or any other type of diagram, keep it in this `.md` file.
* Do a summary of the relationships at the bottom of the document.

--------
