from datetime import timedelta
from feast import Entity, FeatureStore, FeatureView, Field
from feast.types import Float64, String, UnixTimestamp
from feast.data_source import PushSource

# Define entity
snap_entity = Entity(
    name="snap",
    description="A snap package",
)

# Define push source for real-time data
snap_push_source = PushSource(
    name="snap_metrics_push_source",
    batch_source=None,
)

# Define feature view
snap_metrics_fv = FeatureView(
    name="snap_metrics",
    entities=[snap_entity],
    ttl=timedelta(days=7),
    schema=[
        Field(name="download_total", dtype=Float64),
    ],
    source=snap_push_source,
)
