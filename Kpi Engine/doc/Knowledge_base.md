# Knowledge base

It is a interface that comunicates with Knowledge based. This interface contains base query functions that extracts base information for the KB:

- *check_kpi_availability* : takes a **machine_id** and a **KPI's list**, this function gives a **boolean** saying wehter the request kpis can be calculated or not on the requested machine.

- *retrieve_kpi_data* = taking a **KPI's list**, this functions gives **information foreach KPI** inside the list, the information for each kpi is a dictionary with informations from the KB.

- *calculate_unit* = taking a **set of unit metrics**, this function gives a **unit**,it is used since the engine can also calculate and give back the unit of the calculation requested when it can be calculated.

- *get_base_kpis* = taking nothing, this functions gives a list of all **base KPI names** taken from the KB.

These functions are used only for taking information, from the KB, about KPI and machines during **semantic validation phase**, by **engine KPI** and **API**.