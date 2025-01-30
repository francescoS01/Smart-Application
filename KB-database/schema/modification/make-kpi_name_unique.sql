alter table public.kpi
    add constraint kpi_pk
        unique (name);
