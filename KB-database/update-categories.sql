UPDATE public.kpi
SET category_id = 4
WHERE kpi_id = 22;

UPDATE public.kpi
SET category_id = 1
WHERE kpi_id = 27;

UPDATE public.kpi
SET category_id = 2
WHERE kpi_id = 25;

UPDATE public.kpi
SET category_id = 1
WHERE kpi_id = 24;

UPDATE public.kpi
SET category_id = 2
WHERE kpi_id = 26;

UPDATE public.kpi
SET category_id = 1
WHERE kpi_id = 23;

DELETE
FROM public.kpicategory
WHERE category_id = 7;
