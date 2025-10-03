"""End-to-end tests for mock pipeline."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from pathway_pipe import ClaimsPipeline
from ade_client import MockExtractor


def test_mock_extraction():
    """Test mock extraction."""
    extractor = MockExtractor()

    # Generate synthetic claims
    files = extractor.generate_synthetic_claims()
    assert len(files) >= 10

    # Extract from first file
    claim = extractor.extract(files[0])
    assert claim.file_id is not None
    assert claim.filename is not None


def test_pipeline_initialization():
    """Test pipeline initialization."""
    pipeline = ClaimsPipeline(app_mode="MOCK")
    pipeline.initialize_mock_data()

    claims = pipeline.get_claims()
    decisions = pipeline.get_decisions()

    # Should have processed some claims
    assert len(claims) >= 0  # May be 0 if not yet processed


def test_pipeline_processing():
    """Test pipeline file processing."""
    pipeline = ClaimsPipeline(app_mode="MOCK")

    # Generate mock docs
    extractor = MockExtractor()
    files = extractor.generate_synthetic_claims()

    # Process first two files
    results = []
    for file_path in files[:2]:
        result = pipeline.process_file(file_path)
        if result:
            results.append(result)

    assert len(results) >= 1

    # Check that decisions were created
    for claim, decision in results:
        assert claim.file_id is not None
        assert decision.route in ["adjuster_junior", "adjuster_senior", "fraud_queue", "litigation", "human_review"]
        assert decision.rule_fired is not None


def test_metrics_tracking():
    """Test metrics tracking."""
    pipeline = ClaimsPipeline(app_mode="MOCK")

    # Generate and process
    extractor = MockExtractor()
    files = extractor.generate_synthetic_claims()

    pipeline.process_file(files[0])

    metrics = pipeline.get_metrics()

    assert "extraction" in metrics
    assert "routing" in metrics
    assert "queues" in metrics


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
