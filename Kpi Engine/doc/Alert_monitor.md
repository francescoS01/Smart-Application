# Alert monitoring

The alert monitor has the responsibility of checking kpi expressions e.g. "sum(cycles)", it knows which are the kpis to monitor and does so by interacting with the kpi engine to calculate alert expressions. The way it works is that it does polling on a defined time-interval using the following informations:
- the machine for which the values are to be calculated.
- the expression used.
- the sliding window size i.e. how far back from the time it was polling it has to take data from.

The actual calculation is done by the kpi engine, the alert monitor uses the time range determined by the sliding window size and asks the kpi engine to calculate a boolean expression, if it evaluates to true then it has to contact the api layer and notify it that an alert has been fired giving the necessary informations.  

Also the alert monitor holds information about which expression are to be monitored.