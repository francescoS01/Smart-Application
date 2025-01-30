UPDATE public.kpi
SET formula     = 'cycles / total_time',
    has_formula = true
WHERE kpi_id = 21;

UPDATE public.kpi
SET formula     = '(consumption_idle+consumption_working) / cycles',
    has_formula = true
WHERE kpi_id = 14;


UPDATE public.kpi
SET formula     = '(idle_time / (working_time + idle_time + offline_time)) * 100',
    has_formula = true
WHERE kpi_id = 3;

UPDATE public.kpi
SET formula = '(good_cycles*average_cycle_time)/(working_time+idle_time+offline_time)',
    has_formula = true
WHERE kpi_id = 20;

UPDATE public.kpi
SET formula = 'working_time/bad_cycles',
    has_formula = true
WHERE kpi_id = 19;

UPDATE public.kpi
SET formula     = '(bad_cycles / cycles) * 100',
    has_formula = true
WHERE kpi_id = 8;

UPDATE public.kpi
SET formula = '(offline_time * 10) /100',
    has_formula = true
WHERE kpi_id = 18;

UPDATE public.kpi
SET formula     = '(working_time / (working_time + idle_time + offline_time)) * 100',
    has_formula = true
WHERE kpi_id = 2;

UPDATE public.kpi
SET formula     = 'working_time / idle_time',
    has_formula = true
WHERE kpi_id = 5;

UPDATE public.kpi
SET formula     = '(cost_idle + cost_working) / cycles',
    has_formula = true
WHERE kpi_id = 9;

UPDATE public.kpi
SET formula     = '(idle_time + offline_time) / (working_time + idle_time + offline_time) * 100',
    has_formula = true
WHERE kpi_id = 4;

UPDATE public.kpi
SET formula     = 'consumption / cycles',
    has_formula = true
WHERE kpi_id = 13;

UPDATE public.kpi
SET formula     = '(good_cycles / cycles) * 100',
    has_formula = true
WHERE kpi_id = 6;


