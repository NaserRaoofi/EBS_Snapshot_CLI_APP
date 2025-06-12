import boto3
from botocore.exceptions import ClientError
from utils import add_snapshot_to_env, remove_snapshot_from_env
from logger import logger


def get_root_volume_id(instance_id):
    ec2 = boto3.client('ec2')
    try:
        response = ec2.describe_instances(InstanceIds=[instance_id])
        volume_id = response['Reservations'][0]['Instances'][0]['BlockDeviceMappings'][0]['Ebs']['VolumeId']
        return volume_id
    except (KeyError, IndexError, ClientError) as e:
        logger.error(f"Error retrieving root volume ID: {e}")
        return None


def create_snapshot(instance_id, instance_name, description="Automated snapshot"):
    ec2 = boto3.client('ec2')
    volume_id = get_root_volume_id(instance_id)
    if not volume_id:
        return None

    try:
        response = ec2.create_snapshot(
            VolumeId=volume_id,
            Description=description,
            TagSpecifications=[{
                'ResourceType': 'snapshot',
                'Tags': [
                    {'Key': 'instance-id', 'Value': instance_id},
                    {'Key': 'Name', 'Value': instance_name}
                ]
            }]
        )
        snapshot_id = response['SnapshotId']
        add_snapshot_to_env(snapshot_id, instance_id)
        logger.info(f"📸 Snapshot created: {snapshot_id}")
        return snapshot_id
    except ClientError as e:
        logger.error(f"Error creating snapshot: {e}")
        return None


def list_snapshots(instance_id):
    ec2 = boto3.client('ec2')
    try:
        response = ec2.describe_snapshots(
            Filters=[{'Name': 'tag:instance-id', 'Values': [instance_id]}],
            OwnerIds=['self']
        )
        return sorted(response['Snapshots'], key=lambda s: s['StartTime'], reverse=True)
    except ClientError as e:
        logger.error(f"Error listing snapshots: {e}")
        return []


def delete_snapshot(snapshot_id):
    ec2 = boto3.client('ec2')
    if not snapshot_id:
        logger.error("No snapshot ID provided.")
        return False
    try:
        ec2.delete_snapshot(SnapshotId=snapshot_id)
        remove_snapshot_from_env(snapshot_id)
        logger.info(f"🗑️ Deleted snapshot: {snapshot_id}")
        return True
    except ClientError as e:
        logger.error(f"Error deleting snapshot: {e}")
        return False


def list_ec2_instances():
    ec2 = boto3.client('ec2')
    instances = []
    try:
        reservations = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])['Reservations']
        for res in reservations:
            for inst in res['Instances']:
                instances.append({
                    'InstanceId': inst['InstanceId'],
                    'Name': next((tag['Value'] for tag in inst.get('Tags', []) if tag['Key'] == 'Name'), 'No Name'),
                    'AZ': inst['Placement']['AvailabilityZone']
                })
    except ClientError as e:
        logger.error(f"Error listing EC2 instances: {e}")
    return instances
