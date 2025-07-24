from dependency_injector import containers, providers

from ..domain.services import SnapshotService, EC2Service, RestoreService
from ..application.use_cases import (
    CreateSnapshotUseCase,
    ListSnapshotsUseCase,
    DeleteSnapshotUseCase,
    ListInstancesUseCase,
    RestoreSnapshotUseCase,
)
from ..infrastructure.aws import (
    AWSEC2Repository,
    AWSSnapshotRepository,
    AWSVolumeRepository,
)
from ..infrastructure.config import AppConfig
from ..infrastructure.logging import Logger


class Container(containers.DeclarativeContainer):
    config = providers.Singleton(AppConfig.load)

    logger = providers.Singleton(
        Logger, level=config.provided.log_level, log_file=config.provided.log_file
    )

    ec2_repository = providers.Singleton(
        AWSEC2Repository, default_region=config.provided.aws.region
    )

    snapshot_repository = providers.Singleton(
        AWSSnapshotRepository, default_region=config.provided.aws.region
    )

    volume_repository = providers.Singleton(
        AWSVolumeRepository, default_region=config.provided.aws.region
    )

    ec2_service = providers.Singleton(EC2Service, ec2_repo=ec2_repository)

    snapshot_service = providers.Singleton(
        SnapshotService, ec2_repo=ec2_repository, snapshot_repo=snapshot_repository
    )

    restore_service = providers.Singleton(
        RestoreService,
        ec2_repo=ec2_repository,
        snapshot_repo=snapshot_repository,
        volume_repo=volume_repository,
    )

    create_snapshot_use_case = providers.Singleton(
        CreateSnapshotUseCase, snapshot_service=snapshot_service
    )

    list_snapshots_use_case = providers.Singleton(
        ListSnapshotsUseCase, snapshot_service=snapshot_service
    )

    delete_snapshot_use_case = providers.Singleton(
        DeleteSnapshotUseCase, snapshot_service=snapshot_service
    )

    list_instances_use_case = providers.Singleton(
        ListInstancesUseCase, ec2_service=ec2_service
    )

    restore_snapshot_use_case = providers.Singleton(
        RestoreSnapshotUseCase, restore_service=restore_service
    )
