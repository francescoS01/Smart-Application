# Database

It is a interface that comunicates with Databse. This interface contains base query functions that extract values:

- *retrieve_data_db* = Taking **machine_id**, the **KPI's list**, **aggregation_operation**, and **range**, this function get a matrix of values, where every row is a **KPI** (inside **KPI's list**) of **machine** (identified by **machine_id**). All rows are referred to the temporal range described by **range**.

This function are used only for taking information during calculation phase by KPI engine.

As an additional feature, there is also *get_time_range* function, that taking **time_range**, **start_time**, **end_time**, this function gives time inside **time_range** (and between **start_time** - **end_time**) converting to datetime objects (the conventional form). This function is not directly correlated to DB connection, but it is used for converting string date in more conventional form for calculation, and also for filtering date outside the temporal range.