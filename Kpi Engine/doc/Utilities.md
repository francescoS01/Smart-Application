# Utilities

this part comment the utilities used for the realization of the project

- **calculate segments** takes the the desired time range specified with **start_date** and **end_date** and a **unit** which specifies which time aggregation is requested and the function will return return a list of time-segments
- **remove_nan** just removes nan values and also round float values for the serialization of the result
- **extract kpi_names** takes an **expression** and a list of **kpi names** and extracts the names from the expression and gives them back.

- the **get_token** , **call_with_token** and **call_and_retry** functions are used to authenticate to the api layer and facilitate the usage.
- **calculate_range_kpi** takes a **time_range**, a **machine_id** and an **expression** and is the responsible for using the calculation engine in order to do the calculations and gives back the  result when done to do calculations in a certain time range.
- **calculate_range_alert** is similar only it uses the alert calculation capabilities.