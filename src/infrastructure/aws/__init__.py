import boto3
from typing import List, Optional
from datetime import datetime
from botocore.exceptions import ClientError

from ...domain.entities import EC2Instance, EBSVolume, Snapshot
from ...domain.repositories import EC2Repository, SnapshotRepository, VolumeRepository


class AWSEC2Repository(EC2Repository):
    def __init__(self, default_region: Optional[str] = None):
        self._default_region = default_region

    def _get_client(self, region: Optional[str] = None):
        return boto3.client("ec2", region_name=region or self._default_region)

    def list_running_instances(self, region: Optional[str] = None) -> List[EC2Instance]:
        client = self._get_client(region)
        instances = []

        try:
            response = client.describe_instances(
                Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
            )

            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    name = next(
                        (
                            tag["Value"]
                            for tag in instance.get("Tags", [])
                            if tag["Key"] == "Name"
                        ),
                        "No Name",
                    )

                    instances.append(
                        EC2Instance(
                            instance_id=instance["InstanceId"],
                            name=name,
                            availability_zone=instance["Placement"]["AvailabilityZone"],
                            state=instance["State"]["Name"],
                        )
                    )
        except ClientError:
            pass

        return instances

    def get_instance_volumes(
        self, instance_id: str, region: Optional[str] = None
    ) -> List[EBSVolume]:
        client = self._get_client(region)
        volumes = []

        try:
            response = client.describe_instances(InstanceIds=[instance_id])
            instance = response["Reservations"][0]["Instances"][0]
            root_device_name = instance.get("RootDeviceName", "/dev/sda1")

            for mapping in instance.get("BlockDeviceMappings", []):
                if "Ebs" in mapping:
                    volume_response = client.describe_volumes(
                        VolumeIds=[mapping["Ebs"]["VolumeId"]]
                    )
                    volume_info = volume_response["Volumes"][0]

                    volumes.append(
                        EBSVolume(
                            volume_id=mapping["Ebs"]["VolumeId"],
                            device_name=mapping["DeviceName"],
                            instance_id=instance_id,
                            size=volume_info["Size"],
                            volume_type=volume_info["VolumeType"],
                            is_root=(mapping["DeviceName"] == root_device_name),
                        )
                    )
        except (ClientError, KeyError, IndexError):
            pass

        return volumes

    def get_root_volume(
        self, instance_id: str, region: Optional[str] = None
    ) -> Optional[EBSVolume]:
        volumes = self.get_instance_volumes(instance_id, region)
        root_volumes = [v for v in volumes if v.is_root]
        return root_volumes[0] if root_volumes else (volumes[0] if volumes else None)


class AWSSnapshotRepository(SnapshotRepository):
    def __init__(self, default_region: Optional[str] = None):
        self._default_region = default_region

    def _get_client(self, region: Optional[str] = None):
        return boto3.client("ec2", region_name=region or self._default_region)

    def create_snapshot(
        self, volume_id: str, description: str, tags: dict, region: Optional[str] = None
    ) -> Optional[str]:
        client = self._get_client(region)

        try:
            tag_specifications = [
                {
                    "ResourceType": "snapshot",
                    "Tags": [{"Key": k, "Value": v} for k, v in tags.items()],
                }
            ]

            response = client.create_snapshot(
                VolumeId=volume_id,
                Description=description,
                TagSpecifications=tag_specifications,
            )

            return response["SnapshotId"]
        except ClientError:
            return None

    def list_snapshots(
        self, instance_id: str, region: Optional[str] = None
    ) -> List[Snapshot]:
        client = self._get_client(region)
        snapshots = []

        try:
            response = client.describe_snapshots(
                Filters=[{"Name": "tag:instance-id", "Values": [instance_id]}],
                OwnerIds=["self"],
            )

            for snapshot_data in response["Snapshots"]:
                snapshots.append(
                    Snapshot(
                        snapshot_id=snapshot_data["SnapshotId"],
                        volume_id=snapshot_data["VolumeId"],
                        instance_id=instance_id,
                        description=snapshot_data["Description"],
                        start_time=snapshot_data["StartTime"],
                        state=snapshot_data["State"],
                        progress=snapshot_data.get("Progress", ""),
                        size=snapshot_data["VolumeSize"],
                    )
                )

            snapshots.sort(key=lambda s: s.start_time, reverse=True)
        except ClientError:
            pass

        return snapshots

    def delete_snapshot(self, snapshot_id: str, region: Optional[str] = None) -> bool:
        client = self._get_client(region)

        try:
            client.delete_snapshot(SnapshotId=snapshot_id)
            return True
        except ClientError:
            return False

    def get_snapshot(
        self, snapshot_id: str, region: Optional[str] = None
    ) -> Optional[Snapshot]:
        client = self._get_client(region)

        try:
            response = client.describe_snapshots(SnapshotIds=[snapshot_id])
            snapshot_data = response["Snapshots"][0]

            instance_id = next(
                (
                    tag["Value"]
                    for tag in snapshot_data.get("Tags", [])
                    if tag["Key"] == "instance-id"
                ),
                "",
            )

            return Snapshot(
                snapshot_id=snapshot_data["SnapshotId"],
                volume_id=snapshot_data["VolumeId"],
                instance_id=instance_id,
                description=snapshot_data["Description"],
                start_time=snapshot_data["StartTime"],
                state=snapshot_data["State"],
                progress=snapshot_data.get("Progress", ""),
                size=snapshot_data["VolumeSize"],
            )
        except (ClientError, KeyError, IndexError):
            return None


class AWSVolumeRepository(VolumeRepository):
    def __init__(self, default_region: Optional[str] = None):
        self._default_region = default_region

    def _get_client(self, region: Optional[str] = None):
        return boto3.client("ec2", region_name=region or self._default_region)

    def create_volume_from_snapshot(
        self, snapshot_id: str, availability_zone: str, region: Optional[str] = None
    ) -> Optional[str]:
        client = self._get_client(region)

        try:
            response = client.create_volume(
                SnapshotId=snapshot_id, AvailabilityZone=availability_zone
            )
            return response["VolumeId"]
        except ClientError:
            return None

    def attach_volume(
        self,
        volume_id: str,
        instance_id: str,
        device: str,
        region: Optional[str] = None,
    ) -> bool:
        client = self._get_client(region)

        try:
            client.attach_volume(
                VolumeId=volume_id, InstanceId=instance_id, Device=device
            )
            return True
        except ClientError:
            return False

    def detach_volume(self, volume_id: str, region: Optional[str] = None) -> bool:
        client = self._get_client(region)

        try:
            client.detach_volume(VolumeId=volume_id)
            return True
        except ClientError:
            return False
