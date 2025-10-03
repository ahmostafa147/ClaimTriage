# Pathway Integration for ClaimTriage

## Overview

This document describes the Pathway streaming API integration for the ClaimTriage system. Pathway enables real-time, event-driven claim processing with stateful transformations, temporal operations, and automatic incremental computation.

## Architecture

### Components

1. **pathway_schemas.py** - Pathway schema definitions
   - `StructuredClaimSchema` - Schema for extracted claims
   - `RoutingDecisionSchema` - Schema for routing decisions
   - `MetricsSchema` - Schema for aggregated metrics
   - `QueueSizeSchema` - Schema for queue size tracking

2. **pathway_pipeline.py** - Main streaming pipeline
   - `PathwayClaimsPipeline` - Pathway-based streaming implementation
   - File watching via `pw.io.fs.read()`
   - UDF-based document extraction
   - Stateful rule evaluation
   - Real-time metrics aggregation

3. **pathway_pipe.py** (updated) - Pipeline factory
   - Supports both standard and Pathway pipelines
   - Automatic pipeline selection based on configuration
   - Maintains backward compatibility

4. **app.py** (updated) - Streamlit UI
   - Toggle for enabling/disabling Pathway streaming
   - Real-time status indicator
   - No changes to existing functionality

## Key Features

### 1. Real-Time File Watching
```python
files_table = pw.io.fs.read(
    path=str(self.inbox_dir),
    format="binary",
    mode="streaming",
    with_metadata=True
)
```
- Automatically detects new PDF files in inbox
- Streams changes in real-time
- No manual polling required

### 2. UDF-Based Processing
```python
@pw.udf
def extract_claim(filepath: str, data: bytes) -> dict:
    # Extract structured claim from PDF
    claim = self.extractor.extract(Path(filepath))
    return claim_dict
```
- Wraps existing extraction logic
- Seamless integration with MockExtractor/ADEExtractor
- Captures timing metrics automatically

### 3. Stateful Transformations
```python
self.queue_sizes_table = self.decisions_table.groupby(pw.this.route).reduce(
    route=pw.this.route,
    size=pw.reducers.count()
)
```
- Automatic queue size tracking
- Incremental updates on changes
- Efficient state management

### 4. Event-Driven Cache Updates
```python
pw.io.subscribe(
    self.claims_table,
    on_change=self._update_claims_cache,
    on_end=lambda: None
)
```
- Pathway tables automatically update UI cache
- No polling or manual synchronization
- Maintains consistency with streaming state

## Usage

### Environment Variables

```bash
# Enable Pathway streaming
export USE_PATHWAY=true

# Set application mode
export APP_MODE=MOCK  # or PROD
```

### Programmatic Usage

```python
from pathway_pipe import get_pipeline

# Get Pathway streaming pipeline
pipeline = get_pipeline(app_mode="MOCK", use_pathway=True)

# Start streaming (happens automatically)
# pipeline.start() is called internally

# Access results
claims = pipeline.get_claims()
decisions = pipeline.get_decisions()
metrics = pipeline.get_metrics()
```

### Streamlit UI

1. Launch the app: `streamlit run app.py`
2. In the sidebar, check "Use Pathway Streaming"
3. The system will restart with Pathway enabled
4. Files dropped in the inbox are processed automatically

## Testing

Run the integration test suite:

```bash
python test_pathway_integration.py
```

This will:
1. Verify Pathway installation
2. Create a streaming pipeline
3. Generate and process mock claims
4. Validate metrics and routing
5. Report test results

## Performance Characteristics

### Standard Pipeline (In-Memory)
- **Latency**: Batch processing on demand
- **Throughput**: Limited by synchronous processing
- **State**: In-memory dictionaries with locks
- **Scalability**: Single-process, memory-bound

### Pathway Pipeline (Streaming)
- **Latency**: Event-driven, sub-second response
- **Throughput**: High concurrent processing
- **State**: Persistent, recoverable state
- **Scalability**: Distributed processing capable

## Incremental Computation

When rules are updated via `reload_rules()`:
- Pathway automatically recomputes affected decisions
- Only changed claims are reprocessed
- UI updates reflect changes in real-time
- No manual refresh or reprocessing needed

## Temporal Operations

### Metrics Windows
Currently implemented with simple caching, but can be enhanced with:
```python
# Sliding window for latency metrics
metrics_table = claims_table.windowby(
    claims_table.created_at,
    window=pw.temporal.sliding(duration=timedelta(minutes=5)),
).reduce(
    p50=pw.reducers.quantile(pw.this.extraction_time_ms, 0.5),
    p95=pw.reducers.quantile(pw.this.extraction_time_ms, 0.95)
)
```

## Persistence

To enable state persistence for fault tolerance:

```python
import pathway as pw

pw.run(
    persistence_config=pw.persistence.Config(
        backend=pw.persistence.Backend.filesystem("./pathway_state"),
        snapshot_interval_ms=60000  # Snapshot every minute
    )
)
```

This enables:
- Automatic state snapshots
- Recovery from failures
- Consistent restart behavior

## Migration Guide

### From Standard to Pathway Pipeline

1. **No Code Changes Required** - The interface is identical
2. **Enable Pathway** - Set `USE_PATHWAY=true` or toggle in UI
3. **Verify Behavior** - Run test suite to validate
4. **Monitor Performance** - Check metrics for improvements

### Rollback

To disable Pathway streaming:
1. Uncheck "Use Pathway Streaming" in UI, or
2. Set `USE_PATHWAY=false` in environment
3. Restart the application

## Troubleshooting

### Issue: Pathway not available
**Solution**: Verify `pathway==0.9.0` is installed in requirements.txt

### Issue: Files not being processed
**Solution**:
- Check inbox directory permissions
- Verify files have `.pdf` extension
- Check Pathway pipeline status with `pipeline.pipeline_running`

### Issue: Cache not updating
**Solution**:
- Pathway subscribe callbacks may have errors
- Check console for exceptions in `_update_*_cache` methods

### Issue: High memory usage
**Solution**:
- Limit cache size in `_update_metric()` (currently 100 values)
- Enable Pathway persistence to offload state
- Reduce file watching scope

## Future Enhancements

1. **Distributed Processing** - Scale across multiple workers
2. **Advanced Temporal Operations** - Session windows, tumbling windows
3. **Stateful Aggregations** - Historical trend analysis
4. **Join Operations** - Cross-reference with external data sources
5. **ML Model Integration** - Real-time scoring and retraining

## API Comparison

| Feature | Standard Pipeline | Pathway Pipeline |
|---------|------------------|------------------|
| File Detection | Manual scan | Automatic watch |
| Processing Model | Batch/on-demand | Event-driven stream |
| State Management | In-memory dicts | Persistent tables |
| Concurrency | Thread locks | Native parallelism |
| Incremental Updates | Manual reprocess | Automatic propagation |
| Fault Tolerance | None | State snapshots |
| Scalability | Single process | Distributed capable |

## Resources

- [Pathway Documentation](https://pathway.com/developers/documentation/)
- [Pathway API Reference](https://pathway.com/developers/api-docs/)
- [Pathway GitHub](https://github.com/pathwaycom/pathway)

## Support

For issues related to:
- **ClaimTriage Integration**: Check `PATHWAY_INTEGRATION.md`
- **Pathway Framework**: Visit Pathway documentation
- **Performance Tuning**: See "Performance Characteristics" section above
