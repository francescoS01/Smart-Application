# data validation
this part regards the data validation models implemented in pydantic used to valdiate data for the API endpoints.

The validation offered by pydantic was used for both alert and calculations Each class contained in the *_requests.py files is an object inheriting from the BaseModel class offered by pydantic and handles the validation of the  reuquests automatically e.g. if a necessary paramter is not specified the response is automatically sent by fastapi without manual handling of the problem.