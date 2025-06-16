import boto3
import click
from botocore.exceptions import ClientError
from logger import logger
from backup import list_snapshots, list_ec2_instances


def select_instance(instances, prompt):
    logger.info(prompt)
    for i, inst in enumerate(instances, 1):
        logger.info(f"{i}. {inst['InstanceId']} - {inst['Name']}")
    selected = int(input("Select instance: "))
    if not (1 <= selected <= len(instances)):
        logger.warning("❌ Invalid instance selection.")
        return None
    return instances[selected - 1]


def select_snapshot(snapshots):
    logger.info("💾 Available Snapshots:")
    for i, snap in enumerate(snapshots, 1):
        logger.info(f"{i}. ID: {snap['SnapshotId']} - {snap.get('Description', '')}")
    snap_choice = int(input("Select snapshot to restore: "))
    if not (1 <= snap_choice <= len(snapshots)):
        logger.warning("❌ Invalid snapshot choice.")
        return None
    return snapshots[snap_choice - 1]['SnapshotId']


def create_volume_from_snapshot(ec2, snapshot_id, az):
    logger.info(f"🧩 Step 3: Creating a new volume from snapshot {snapshot_id}.")
    try:
        volume_response = ec2.create_volume(
            SnapshotId=snapshot_id,
            AvailabilityZone=az,
            VolumeType='gp2',
            TagSpecifications=[{
                'ResourceType': 'volume',
                'Tags': [{'Key': 'Name', 'Value': f"Restored-{snapshot_id}"}]
            }]
        )
        volume_id = volume_response['VolumeId']
        logger.info(f"✅ Created volume {volume_id} from snapshot.")
        ec2.get_waiter('volume_available').wait(VolumeIds=[volume_id])
        return volume_id
    except ClientError as e:
        logger.error(f"❌ Failed to create volume: {e}")
        return None


def fetch_root_volume(ec2, target_instance_id):
    logger.info("🔍 Fetching root volume of the selected target instance...")
    try:
        instance_info = ec2.describe_instances(InstanceIds=[target_instance_id])
        mappings = instance_info['Reservations'][0]['Instances'][0]['BlockDeviceMappings']
        root_mapping = next((m for m in mappings if m['DeviceName'] in ['/dev/sda1', '/dev/xvda']), None)
        if not root_mapping:
            logger.error("❌ No root volume found.")
            return None, None
        root_volume_id = root_mapping['Ebs']['VolumeId']
        root_device_name = root_mapping['DeviceName']
        return root_volume_id, root_device_name
    except Exception as e:
        logger.error(f"Error fetching root volume: {e}")
        return None, None


def stop_instance(ec2, instance_id):
    logger.info(f"🛑 Stopping instance {instance_id}...")
    ec2.stop_instances(InstanceIds=[instance_id])
    ec2.get_waiter('instance_stopped').wait(InstanceIds=[instance_id])


def detach_volume(ec2, volume_id, instance_id, device):
    logger.info(f"❌ Detaching original root volume {volume_id}...")
    ec2.detach_volume(VolumeId=volume_id, InstanceId=instance_id, Device=device)
    ec2.get_waiter('volume_available').wait(VolumeIds=[volume_id])


def attach_volume(ec2, instance_id, volume_id, device):
    logger.info(f"📎 Attaching restored volume {volume_id} as root device {device}...")
    ec2.attach_volume(InstanceId=instance_id, VolumeId=volume_id, Device=device)


def start_instance(ec2, instance_id):
    logger.info(f"🚀 Starting instance {instance_id}...")
    ec2.start_instances(InstanceIds=[instance_id])
    ec2.get_waiter('instance_running').wait(InstanceIds=[instance_id])


def restore_snapshot_and_replace_root():
    # 1. Select instance to restore FROM
    instances = list_ec2_instances()
    if not instances:
        logger.error("❌ No running EC2 instances found.")
        return None

    source_instance = select_instance(
        instances,
        "🧩 Step 1: Choose the source EC2 instance (where the snapshot was originally taken)."
    )
    if not source_instance:
        return None
    source_id = source_instance['InstanceId']
    az = source_instance['AZ']
    region = az[:-1]  # 'eu-west-2a' -> 'eu-west-2'
    ec2 = boto3.client('ec2', region_name=region)

    # 2. List and choose snapshot
    logger.info(f"🧩 Step 2: List snapshots for instance {source_id}.")
    snapshots = list_snapshots(source_id)
    if not snapshots:
        logger.warning("⚠️ No snapshots found for this instance.")
        return None
    snapshot_id = select_snapshot(snapshots)
    if not snapshot_id:
        return None

    # 3. Create volume from snapshot
    volume_id = create_volume_from_snapshot(ec2, snapshot_id, az)
    if not volume_id:
        return None

    # 4. Select target EC2 instance
    target_instance = select_instance(instances, "🧩 Step 4: Choose the target EC2 instance to REPLACE its root volume.")
    if not target_instance:
        return None
    target_instance_id = target_instance["InstanceId"]

    # 5. Identify root volume of target instance
    root_volume_id, root_device_name = fetch_root_volume(ec2, target_instance_id)
    if not root_volume_id:
        return None

    # ✅ Confirm with user before replacing root
    logger.info("\n⚠️ YOU ARE ABOUT TO REPLACE THE ROOT VOLUME OF AN EC2 INSTANCE!")
    logger.info(f"Old volume: {root_volume_id} on {target_instance_id} ({root_device_name})")
    logger.info(f"New volume: {volume_id} created from snapshot {snapshot_id}")
    confirm = click.confirm("Do you want to proceed with this root volume replacement?", default=False)
    if not confirm:
        logger.info("❎ Operation cancelled by user.")
        return None

    # 6. Stop target instance
    stop_instance(ec2, target_instance_id)

    # 7. Detach original root volume
    detach_volume(ec2, root_volume_id, target_instance_id, root_device_name)

    # 8. Attach new volume as root
    attach_volume(ec2, target_instance_id, volume_id, root_device_name)

    # 9. Start the instance
    start_instance(ec2, target_instance_id)

    logger.info(f"✅ Restore complete. Instance {target_instance_id} now running with root volume {volume_id}.")
    return volume_id


def restore_snapshot_to_instance_web(snapshot_id, target_instance_id, region):
    """
    Restore the given snapshot to the root volume of the target EC2 instance (non-interactive, for webapp).
    Returns a dict with status and message.
    """
    try:
        # Get all instances in region
        instances = list_ec2_instances(region)
        target_instance = next((i for i in instances if i["InstanceId"] == target_instance_id), None)
        if not target_instance:
            return {"status": "error", "message": f"Target instance {target_instance_id} not found."}
        az = target_instance["AZ"]
        ec2 = boto3.client('ec2', region_name=region)

        # Create volume from snapshot
        volume_id = create_volume_from_snapshot(ec2, snapshot_id, az)
        if not volume_id:
            return {"status": "error", "message": "Failed to create volume from snapshot."}

        # Identify root volume of target instance
        root_volume_id, root_device_name = fetch_root_volume(ec2, target_instance_id)
        if not root_volume_id:
            return {"status": "error", "message": "Could not find root volume for target instance."}

        # Stop instance
        stop_instance(ec2, target_instance_id)
        # Detach original root volume
        detach_volume(ec2, root_volume_id, target_instance_id, root_device_name)
        # Attach new volume as root
        attach_volume(ec2, target_instance_id, volume_id, root_device_name)
        # Start instance
        start_instance(ec2, target_instance_id)

        logger.info(f"✅ Restore complete. Instance {target_instance_id} now running with root volume {volume_id}.")
        return {"status": "success", "message": f"Restore complete. Instance {target_instance_id} now running with root volume {volume_id}."}
    except Exception as e:
        logger.error(f"Restore failed: {e}")
        return {"status": "error", "message": str(e)}
