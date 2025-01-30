# integration of multiple kpi to evaluate the global status of a machine

# hp: we receive the machineID to evaluate and the ####### aggregation_type 
    # request from historical feature store: kpis = unique(kpi), 'trend_drift' values of kpi related to machineID 

concept_drifts = {kpi: 0 for kpi in kpis}            # create a dictionary for the concept drifts

for k in kpis:                                       # for given machineID and aggr_type:
      trend_drift = feat_s_data[(feat_s_data['name'] == name) & (feat_s_data['kpi'] == k) & (feat_s_data['col'] == col)]['trend_drift'].iloc[0] 
        # trend drift goes from -n_period to + n_period
      if trend_drift != 0:
        if trend_drift > 0:
          concept_drifts[k] = 1
        else:
          concept_drifts[k] = -1
      else:
        concept_drifts[k] = 0

# rules for the integration
rules = [
    {"condition": {"cycles": 1, "energy_consumption": 1}, "status": "Producing more"},
    {"condition": {"cycles": 1, "energy_consumption": -1}, "status": "Producing more efficiently consuming less energy"},
    {"condition": {"cycles": -1, "energy_consumption": 1}, "status": "Consuming more with less production"},
    {"condition": {"cycles": -1, "energy_consumption": -1}, "status": "Producing less but conserving energy"},
    {"condition": {"working_time": 1, "idle_time": 1}, "status": "Working and idle time are high. Check for inefficiency."},
    {"condition": {"working_time": -1, "idle_time": -1}, "status": "Low working and idle time. Possible downtime."},
    {"condition": {"consumption_working": 1, "consumption_idle": -1}, "status": "High consumption during working time, low idle consumption."},
    {"condition": {"consumption_working": -1, "consumption_idle": 1}, "status": "Low consumption during working time, high idle consumption."},
    {"condition": {"cycles": 1, "bad_cycles": -1}, "status": "Increase in good cycles, low bad cycles. Optimized production."},
    {"condition": {"cycles": -1, "bad_cycles": 1}, "status": "Decrease in good cycles, increase in bad cycles. Quality issue."},
    {"condition": {"power": 1, "working_time": 1}, "status": "High power usage during working time, investigate for inefficiency."},
    {"condition": {"power": -1, "working_time": -1}, "status": "Low power usage with reduced working time, possible machine underuse."},
    {"condition": {"cost_working": 1, "cost_idle": -1}, "status": "Higher cost during working time than idle. Efficiency issues."},
    {"condition": {"cost_working": -1, "cost_idle": 1}, "status": "Cost-efficient idle time compared to working time."},
    {"condition": {"bad_cycles": 1, "good_cycles": -1}, "status": "High bad cycles, low good cycles. Possible process malfunction."},
    {"condition": {"average_cycle_time": 1, "good_cycles": -1}, "status": "Increase in cycle time, decrease in good cycles. Investigate quality."},
    {"condition": {"working_time": 1, "cost": 1}, "status": "High working time, high cost. Review productivity."},
    {"condition": {"working_time": -1, "cost": -1}, "status": "Low working time and low cost. Possibly under-utilized."},
    {"condition": {"offline_time": 1, "working_time": -1}, "status": "Increase in offline time, decrease in working time. Unplanned downtime."},
    {"condition": {"cycles": 1, "power": 1}, "status": "Higher cycles and power usage, check for energy inefficiencies."},
    {"condition": {"cycles": -1, "power": -1}, "status": "Fewer cycles and lower power usage, could indicate production slowdown."},
    {"condition": {"cost_idle": 1, "idle_time": 1}, "status": "High cost during idle time, investigate machine settings."},
    {"condition": {"cost_idle": -1, "idle_time": -1}, "status": "Low cost during idle time, optimal energy savings."},
    {"condition": {"consumption": 1, "cost": 1}, "status": "Increase in both consumption and cost, possible inefficiency."},
    {"condition": {"consumption": -1, "cost": -1}, "status": "Decrease in both consumption and cost, potential energy savings."}
]

def evaluate_machine_status(concept_drifts, rules):
    """
    Valuta lo stato generale di una macchina basandosi sui concept drift dei KPI.

    Parameters:
    - concept_drifts: Dizionario in cui le chiavi sono i KPI e i valori sono i concept drift (+1 per positivo, -1 per negativo, 0 per neutrale).
      Esempio: {"cycles": 1, "energy_consumption": -1}
    - rules: Lista di regole che mappano i concept drift a stati generali della macchina.
      Esempio:
      [
          {"condition": {"cycles": 1, "energy_consumption": 1}, "status": "Producing more"},
          {"condition": {"cycles": -1, "energy_consumption": 1}, "status": "Inefficient"}
      ]

    Returns:
    - machine_status: Stato generale della macchina determinato dalle regole.
    """
    for rule in rules:
        condition = rule["condition"]
        if all(concept_drifts.get(kpi, 0) == condition.get(kpi, 0) for kpi in condition):
            return rule["status"]

    return "Unknown behavior"  # Stato di default se nessuna regola è soddisfatta

# Valutazione dello stato della macchina

machine_status = evaluate_machine_status(concept_drifts, rules)
print(f"Machine Status: {machine_status}")
