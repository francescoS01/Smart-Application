-- Creates functions for the API Layer to easily interact with the database and reuse code
-- This script should be run the first time the API connects to the database

-- Function to get all KPIs from a machine type
CREATE OR REPLACE FUNCTION get_kpi_list_from_machine_type(
    IN machine_type_name VARCHAR(255)
)
RETURNS TABLE(
    kpi_name VARCHAR(255)
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT kpi.name
    FROM public.machine_typekpi 
    JOIN public.kpi ON machine_typekpi.kpi_id = kpi.kpi_id
    JOIN public.machine_type ON machine_typekpi.machine_type_id = machine_type.machine_type_id
    WHERE machine_type.type_name = machine_type_name;
END;
$$;

-- Function to get a list of KPIs optionally filtered by id and category name
CREATE OR REPLACE FUNCTION get_kpi_list(
    IN kpi_id_par VARCHAR(255)[] DEFAULT NULL,
    IN category_name_par VARCHAR(255)[] DEFAULT NULL
)
RETURNS TABLE(
    kpi_name VARCHAR(255),
    kpi_description VARCHAR(255),
    category_name VARCHAR(255),
    kpi_unit VARCHAR(255),
    kpi_formula VARCHAR(255),
    kpi_id_res bigint
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT kpi.name, kpi.description::VARCHAR(255), kpicategory.name, kpi.units, kpi.formula, kpi.kpi_id
    FROM public.kpi
    JOIN public.kpicategory ON kpi.category_id = kpicategory.category_id
    WHERE (kpi_id_par IS NULL OR kpi.name = ANY(kpi_id_par))
    AND (category_name_par IS NULL OR kpicategory.name = ANY(category_name_par));
END;
$$;

-- Function to get machine types from a KPI.
-- If the KPI does not exist, an exception is raised
CREATE OR REPLACE FUNCTION get_machine_type_list_from_kpi(
    IN kpi_name VARCHAR(255)
)
RETURNS TABLE(
    machine_type_name VARCHAR(255)
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- If the KPI does not exist, raise an exception
    IF NOT EXISTS (SELECT 1 FROM public.kpi WHERE name = kpi_name) THEN
        RAISE EXCEPTION 'KPI does not exist';
    END IF;

    RETURN QUERY
    SELECT machine_type.type_name
    FROM public.machine_typekpi 
    JOIN public.kpi ON machine_typekpi.kpi_id = kpi.kpi_id
    JOIN public.machine_type ON machine_typekpi.machine_type_id = machine_type.machine_type_id
    WHERE kpi.name = kpi_name;
END;
$$;

-- Get KPI informations not in the given list of KPI names
CREATE OR REPLACE FUNCTION get_kpi_info_not_in_list(
    IN kpi_names VARCHAR(255)[] DEFAULT NULL
)
RETURNS TABLE (
    kpi_name VARCHAR(255),
    kpi_description VARCHAR(255),
    category_name VARCHAR(255),
    kpi_unit VARCHAR(255),
    kpi_formula VARCHAR(255)
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT kpi.name, kpi.description::VARCHAR(255), kpicategory.name, kpi.units, kpi.formula
    FROM public.kpi
    JOIN public.kpicategory ON kpi.category_id = kpicategory.category_id
    WHERE kpi_names IS NULL OR kpi.name != ALL(kpi_names);
END;
$$;


-- Type containing coupples machine id and machine type name
-- Created only if it does not exist
DO
$$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'machine_type_id_name') THEN
        CREATE TYPE machine_type_id_name AS (
            machine_id INTEGER,
            machine_type_name VARCHAR(255)
        );
    END IF;
END;
$$;

-- Get relation between machine types and KPIs
CREATE OR REPLACE FUNCTION get_machine_kpi_relation(
    IN machine_types_par VARCHAR(255)[]
)
RETURNS TABLE(
    machine_type_name VARCHAR(255),
    kpi_id bigint
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT machine_type.type_name, machine_typekpi.kpi_id
    FROM public.machine_typekpi
    JOIN public.machine_type ON machine_typekpi.machine_type_id = machine_type.machine_type_id
    WHERE machine_type.type_name = ANY(CAST(machine_types_par AS VARCHAR(255)[]));
END;
$$;

-- Returns true iff the kpi exists
CREATE OR REPLACE FUNCTION kpi_exists(
    IN kpi_name VARCHAR(255)
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN EXISTS (SELECT 1 FROM public.kpi WHERE name = kpi_name);
END;
$$;
