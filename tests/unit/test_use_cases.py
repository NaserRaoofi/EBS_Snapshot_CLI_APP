import pytest
from unittest.mock import Mock
from src.application.dtos import CreateSnapshotRequest, CreateSnapshotResponse
from src.domain.services import SnapshotService
from src.application.use_cases import CreateSnapshotUseCase


@pytest.mark.unit
class TestCreateSnapshotUseCase:
    def setup_method(self):
        self.mock_snapshot_service = Mock(spec=SnapshotService)
        self.use_case = CreateSnapshotUseCase(self.mock_snapshot_service)

    def test_execute_success(self):
        self.mock_snapshot_service.create_instance_snapshot.return_value = "snap-123"

        request = CreateSnapshotRequest(
            instance_id="i-123",
            instance_name="test-instance",
            description="test snapshot",
        )

        response = self.use_case.execute(request)

        assert response.success is True
        assert response.snapshot_id == "snap-123"
        assert "successfully" in response.message

    def test_execute_failure(self):
        self.mock_snapshot_service.create_instance_snapshot.return_value = None

        request = CreateSnapshotRequest(
            instance_id="i-123", instance_name="test-instance"
        )

        response = self.use_case.execute(request)

        assert response.success is False
        assert response.snapshot_id is None
        assert "Failed" in response.message

    def test_execute_exception(self):
        self.mock_snapshot_service.create_instance_snapshot.side_effect = Exception(
            "AWS Error"
        )

        request = CreateSnapshotRequest(
            instance_id="i-123", instance_name="test-instance"
        )

        response = self.use_case.execute(request)

        assert response.success is False
        assert response.snapshot_id is None
        assert "Error creating snapshot" in response.message
