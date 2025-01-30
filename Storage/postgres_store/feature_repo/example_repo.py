from datetime import timedelta
from feast import Entity, FeatureView, Field, PushSource
from feast.infra.offline_stores.contrib.postgres_offline_store.postgres_source import (
    PostgreSQLSource,
)
from feast.types import Float64, Int32, Bool, Array, ValueType

# Definizione delle entità con specifica del value_type
machineid = Entity(name="machineid", join_keys=["machineid"], value_type=ValueType.INT64)
kpi = Entity(name="kpi", join_keys=["kpi"], value_type=ValueType.STRING)
aggregation_type = Entity(name="aggregation_type", join_keys=["aggregation_type"], value_type=ValueType.STRING)

# Definizione della sorgente PostgreSQL per historical_store
historical_store_source = PostgreSQLSource(
    name="kpi_data_source",
    query="SELECT * FROM historical_store",
    timestamp_field="timestamp")

# Definizione della FeatureView per historical_store
historical_store_fv = FeatureView(
    name="historical_store",
    entities=[machineid, kpi, aggregation_type],
    ttl=timedelta(days=1),
    schema=[
        Field(name="value", dtype=Float64),
        Field(name="imputation", dtype=Bool),
        Field(name="anomaly", dtype=Bool),
        Field(name="trend_drift", dtype=Int32),
        Field(name="next_days_predictions", dtype=Array(Float64)),
        Field(name="confidence_interval_lower", dtype=Array(Float64)),
        Field(name="confidence_interval_upper", dtype=Array(Float64))
    ],
    online=True,
    source=historical_store_source
)

# Push source per historical_store
historical_store_push_source = PushSource(
    name="historical_store_push_source",
    batch_source=historical_store_source)

# Definizione della FeatureView per historical_store_fresh
historical_store_fresh_fv = FeatureView(
    name="historical_store_fresh",
    entities=[machineid, kpi, aggregation_type],
    ttl=timedelta(days=1),
    schema=[
        Field(name="value", dtype=Float64),
        Field(name="imputation", dtype=Bool),
        Field(name="anomaly", dtype=Bool),
        Field(name="trend_drift", dtype=Int32),
        Field(name="next_days_predictions", dtype=Array(Float64)),
        Field(name="confidence_interval_lower", dtype=Array(Float64)),
        Field(name="confidence_interval_upper", dtype=Array(Float64))
    ],
    online=True,
    source=historical_store_push_source
)

# Definizione della sorgente PostgreSQL per thresholds
thresholds = PostgreSQLSource(
    name="thresholds",
    query="SELECT * FROM thresholds",
    timestamp_field="timestamp")

# FeatureView per thresholds
thresholds_fv = FeatureView(
    name="thresholds",
    entities=[machineid, kpi, aggregation_type],
    ttl=timedelta(days=1),
    schema=[
        Field(name="min_threshold", dtype=Float64),
        Field(name="max_threshold", dtype=Float64),
    ],
    online=True,
    source=thresholds
)

# Push source per thresholds
thresholds_push_source = PushSource(
    name="thresholds_push_source",
    batch_source=thresholds)

# FeatureView per thresholds_fresh
thresholds_fresh_fv = FeatureView(
    name="thresholds_fresh",
    entities=[machineid, kpi, aggregation_type],
    ttl=timedelta(days=1),
    schema=[
        Field(name="min_threshold", dtype=Float64),
        Field(name="max_threshold", dtype=Float64),
    ],
    online=True,
    source=thresholds_push_source
)

# Definizione della sorgente PostgreSQL per seasonalities
seasonalities = PostgreSQLSource(
    name="seasonalities",
    query="SELECT * FROM seasonalities",
    timestamp_field="timestamp")

# FeatureView per seasonalities
seasonalities_fv = FeatureView(
    name="seasonalities",
    entities=[machineid, kpi, aggregation_type],
    ttl=timedelta(days=1),
    schema=[
        Field(name="selected_f", dtype=Int32)
    ],
    online=True,
    source=seasonalities
)

# Push source per seasonalities
seasonalities_push_source = PushSource(
    name="seasonalities_push_source",
    batch_source=seasonalities)

# FeatureView per seasonalities_fresh
seasonalities_fresh_fv = FeatureView(
    name="seasonalities_fresh",
    entities=[machineid, kpi, aggregation_type],
    ttl=timedelta(days=1),
    schema=[
        Field(name="selected_f", dtype=Int32)
    ],
    online=True,
    source=seasonalities_push_source
)
