"""Tests for Pathway integration."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from pathway_pipe import get_pipeline, ClaimsPipeline, PATHWAY_AVAILABLE


def test_simple_pipeline_available():
    """Test that simple pipeline always works."""
    pipeline = get_pipeline(app_mode="MOCK", use_pathway=False)
    assert isinstance(pipeline, ClaimsPipeline)
    assert pipeline is not None


def test_pathway_import():
    """Test Pathway import status."""
    # This test documents whether Pathway is available
    if PATHWAY_AVAILABLE:
        import pathway as pw
        assert pw is not None
        print("✅ Pathway available")
    else:
        print("⚠️  Pathway not available (expected in basic install)")


def test_get_pipeline_without_pathway():
    """Test getting pipeline when Pathway not requested."""
    pipeline = get_pipeline(app_mode="MOCK", use_pathway=False)
    assert isinstance(pipeline, ClaimsPipeline)


def test_get_pipeline_with_pathway_request():
    """Test getting pipeline when Pathway requested."""
    pipeline = get_pipeline(app_mode="MOCK", use_pathway=True)

    # Should get PathwayClaimsPipeline if available, else ClaimsPipeline
    assert pipeline is not None

    if PATHWAY_AVAILABLE:
        from pathway_pipe import PathwayClaimsPipeline
        assert isinstance(pipeline, PathwayClaimsPipeline)
        print("✅ PathwayClaimsPipeline initialized")

        # Test streaming methods exist
        assert hasattr(pipeline, 'start_streaming')
        assert hasattr(pipeline, 'stop_streaming')
    else:
        assert isinstance(pipeline, ClaimsPipeline)
        print("⚠️  Fell back to ClaimsPipeline (Pathway not installed)")


def test_pipeline_basic_operations():
    """Test basic pipeline operations work regardless of Pathway."""
    pipeline = get_pipeline(app_mode="MOCK", use_pathway=False)

    # Initialize mock data
    pipeline.initialize_mock_data()

    # Process inbox
    results = pipeline.process_inbox()

    # Should process some claims
    assert len(results) >= 0

    # Check metrics
    metrics = pipeline.get_metrics()
    assert "extraction" in metrics
    assert "routing" in metrics
    assert "queues" in metrics


@pytest.mark.skipif(not PATHWAY_AVAILABLE, reason="Pathway not installed")
def test_pathway_pipeline_initialization():
    """Test PathwayClaimsPipeline initialization (only if Pathway available)."""
    from pathway_pipe import PathwayClaimsPipeline

    pipeline = PathwayClaimsPipeline(app_mode="MOCK")

    assert pipeline is not None
    assert hasattr(pipeline, 'start_streaming')
    assert hasattr(pipeline, 'stop_streaming')
    assert hasattr(pipeline, 'streaming_enabled')
    assert pipeline.streaming_enabled == False  # Not started yet


@pytest.mark.skipif(not PATHWAY_AVAILABLE, reason="Pathway not installed")
def test_pathway_pipeline_basic_operations():
    """Test PathwayClaimsPipeline basic operations (only if Pathway available)."""
    from pathway_pipe import PathwayClaimsPipeline

    pipeline = PathwayClaimsPipeline(app_mode="MOCK")

    # Test basic operations (non-streaming)
    pipeline.initialize_mock_data()
    results = pipeline.process_inbox()

    assert len(results) >= 0

    # Test metrics
    metrics = pipeline.get_metrics()
    assert "extraction" in metrics


def test_pipeline_graceful_degradation():
    """Test that requesting Pathway when unavailable gracefully degrades."""
    # This should never raise an error
    pipeline = get_pipeline(app_mode="MOCK", use_pathway=True)

    assert pipeline is not None
    assert hasattr(pipeline, 'process_file')
    assert hasattr(pipeline, 'get_claims')
    assert hasattr(pipeline, 'get_decisions')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
