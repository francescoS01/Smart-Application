
# Calculation logic

The main point of the KPI engine is parsing string expression to do calculations using the data retrieved from the database. To do so, step by step,the KPI engine will do the following actions:

- Take the **string expression**.
- Parse the string to get a **syntax tree**.
- Do **semantical checking** i.e. check if everything is ok (like no division by 0 etc.) using the knowledge base.
- **calculate the expression** according to syntax defined below.

An **expression** can either be a **mathematical expression** or an **alert** the difference being that mathematical expression can only use numerical operations while alert expressions allow the use of boolean operators and evaluate to only scalar-boolean expressions.

Considering variable *EXPR* like an expression that gives either a single number or a column of numbers, an **alert** is defined like:

$$Alert = \bold{EXPR} \text{ <boolean operator> }  \bold{EXPR}$$

Depending on the use case,see below,you can also specify one expr term if you want onlynumbers.

Where boolean operator can be any kind of inequality like **\=**, **\<**, **\>**, etc.

Inside the expression $\bold{EXPR}$, every term can be:
- **Scalar-like**: a single numerical value.
- **column-like** which is either a list of kpi values coming directly from the machines, it’s values are drawn from the specified time range, or is the result of doing operations other column-like / base kpis.

we can use the four basic operators +,-,/ and - among the term regardless of their types and perform the corresponding operations:
- when the elements are two scalars we get a scalar with the applied operation
- for two column kinds we get an elements wise application of the operations.
- for mixed kinds we have that the scalar value is applied on every element of the column one.

It is possible to apply some **aggregation** base functions on base kpi values that give back a scalar applicable with the following syntax:
$$\text{<aggregation>}(\text{<column-like value>})$$


the available ones are *sum*, *min*, *avg*, *var*, *max* etc.
This kind of operations is appliable only to column-like values.

This allows a lot of flexibility in the use of the engine to accommodate the functionalities needed by parts outside the system.

There are also some  cases where engine can refuse to do calculations, giving an error, this cases are:

- String expression doesn’ t follow the correct syntax structure.  
- There is a division by 0\.  
- A variable is not a *base function* or a KPI base name.

The terms used inside an expression can be names of both base kpis and ones from the knowledge base, for that case the engine will retrieve the corresponding formula from the KB,if no aggregation functions is used then you will get back a column like-value.

Such feature is used for alert and calculation capabilities offered in the API endpoints **calculate** and **alert**, you can see them from the [localhost:8000/docs](localhost:8000/docs) link offered by fastapi, here we are gonna explain how it works since it differs by the endpoints.
## normal calculations
Note before starting: the data received by the engine is in the form of aggregated values meaning we don't get raw data but only aggregations of it at a certain point in time, in particular we get the sum, average, minimum and maximum to do our operation on the kpi values we need to select one of them using an aggregation selector.

For the the **calculate endpoint** we have to specify a time range, an aggregation operation and the expression we want to parse. In this part we are allowed to use expressions that only give back numerical values. 
To better undestand this imagine a set of filters and group operations being applied:
- select for which machine you want to do the calculation
- first we filter only the time range we want
- then we filter by picking the aggregation selector between 'sum','max','min','avg'
- now we can group together in time segments, in particular values can be grouped by day,week,month,year or not be grouped at all.
- finally for each segment the expression is applied as specified before and we have the result returned to us.

Note here boolean operators are not possible, use only mathematical ones.

## alert calculations

Here the logic is similar, we use expressions but now they only give back scalar boolean values, for this part we still use the filter logic but it's different it's not possible to aggregate instead we have only a sliding window. 

Each time the alert calculation is done the data selected is taken looking back starting from the current time minus the **sliding window size** which determines how far back we can look in the past.

the calculation goes as follows:
- pick the machine you want the data for
- pick a sliding window size to decide how far back you want to to take data for.
- write an expression as explained in this section
- finally you get the result back

this is meant for the alert monitor to use however it is testable using the openapi documentation available at [localhost:8000/docs](localhost:8000/docs)


#### technologies used

**Parsing** and **semantic checking** are done by [Lark](https://github.com/lark-parser/lark) library, this tool allows semantic checking with more flexibility, e.g. check if there is a division by 0\.  
Calculation phase are made with [py_expression_eval](https://pypi.org/project/py-expression-eval/) library, because this tool allows us to operate with strings using parallel calculations. In this way the calculations are faster.

To check the capacity of engine KPI and Alert monitor to manage more request in parallel, we used the [**Locust**](https://locust.io/) please visit the section from the kpi engine introduction to see how to use it.