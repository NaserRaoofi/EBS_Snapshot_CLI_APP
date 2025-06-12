#!/usr/bin/env python3
import click
from dotenv import load_dotenv
from backup import (
    create_snapshot,
    list_snapshots,
    delete_snapshot,
    list_ec2_instances
)
from restore import restore_snapshot_and_replace_root
from utils import save_instance_ids_to_env
from logger import logger
from datetime import datetime

load_dotenv()


@click.command()
def cli():
    """Interactive EC2 Snapshot Tool"""

    # --- Step 1: Fetch and save all instance IDs to .env ---
    instances = list_ec2_instances()
    if not instances:
        logger.error("❌ No running EC2 instances found.")
        return
    save_instance_ids_to_env([i["InstanceId"] for i in instances])

    # --- Step 2: Show menu ---
    logger.info("\U0001F4E6 EC2 Snapshot Tool")
    logger.info("1. Take snapshot")
    logger.info("2. List snapshots")
    logger.info("3. Delete a snapshot")
    logger.info("4. Restore from snapshot")

    try:
        choice = click.prompt("Select an option", type=int)

        if choice == 1:
            _handle_take_snapshot(instances)
        elif choice == 2:
            _handle_list_snapshots(instances)
        elif choice == 3:
            _handle_delete_snapshot(instances)
        elif choice == 4:
            _handle_restore_snapshot()
        else:
            logger.warning("\u274C Invalid option selected.")

    except Exception as e:
        logger.exception(f"Unexpected error occurred: {e}")


def _handle_take_snapshot(instances):
    logger.info("🖥️ Available EC2 Instances:")
    for i, inst in enumerate(instances, 1):
        logger.info(f"{i}. {inst['InstanceId']} - {inst['Name']}")
    selected = click.prompt("Select an instance to back up", type=int)

    if 1 <= selected <= len(instances):
        instance_id = instances[selected - 1]['InstanceId']
        instance_name = instances[selected - 1]['Name']
        description = click.prompt("Enter snapshot description", default="Backup via CLI")
        snapshot_id = create_snapshot(instance_id, instance_name, description)
        if snapshot_id:
            logger.info(f"\u2705 Snapshot created: {snapshot_id}")
        else:
            logger.error("\u274C Snapshot creation failed.")
    else:
        logger.warning("❌ Invalid selection.")


def _handle_list_snapshots(instances):
    logger.info("🖥️ Available EC2 Instances:")
    for i, inst in enumerate(instances, 1):
        logger.info(f"{i}. {inst['InstanceId']} - {inst['Name']}")
    selected = click.prompt("Choose instance", type=int)
    if 1 <= selected <= len(instances):
        instance_id = instances[selected - 1]["InstanceId"]
        snaps = list_snapshots(instance_id)
        if snaps:
            logger.info("\U0001F4CB Available Snapshots:")
            for s in snaps:
                logger.info(f"\U0001F7E2 ID: {s['SnapshotId']}, Desc: {s.get('Description', 'No description')}")
        else:
            logger.warning("⚠️ No snapshots found.")
    else:
        logger.warning("❌ Invalid selection.")


def _handle_delete_snapshot(instances):
    logger.info("🖥️ Available EC2 Instances:")
    for i, inst in enumerate(instances, 1):
        logger.info(f"{i}. {inst['InstanceId']} - {inst['Name']}")
    selected = click.prompt("Choose instance", type=int)
    if 1 <= selected <= len(instances):
        instance_id = instances[selected - 1]["InstanceId"]
        snaps = list_snapshots(instance_id)
        if not snaps:
            logger.warning("⚠️ No snapshots available for deletion.")
            return

        logger.info("\U0001F4CB Available Snapshots:")
        for i, snap in enumerate(snaps, 1):
            logger.info(f"{i}. ID: {snap['SnapshotId']}, Desc: {snap.get('Description', 'No description')}")

        snap_selected = click.prompt("Enter the number of the snapshot to delete", type=int)

        if 1 <= snap_selected <= len(snaps):
            snapshot = snaps[snap_selected - 1]
            snapshot_id = snapshot['SnapshotId']
            confirm = click.confirm(f"Are you sure you want to delete snapshot {snapshot_id}?", default=False)

            if confirm:
                if delete_snapshot(snapshot_id):
                    logger.info(f"\u2705 Deleted snapshot {snapshot_id}")
                    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
                    description = snapshot.get("Description", "No description")
                    logger.info(f"{timestamp} - Deleted {snapshot_id}: {description}")
                else:
                    logger.error(f"\u274C Failed to delete snapshot {snapshot_id}")
            else:
                logger.info("❎ Deletion cancelled.")
        else:
            logger.warning("❌ Invalid snapshot selection.")
    else:
        logger.warning("❌ Invalid instance selection.")


def _handle_restore_snapshot():
    logger.info("🛠️ Starting full restore process...")
    volume_id = restore_snapshot_and_replace_root()
    if volume_id:
        logger.info(f"✅ Restore completed successfully. New root volume: {volume_id}")
    else:
        logger.warning("❌ Restore process was cancelled or failed.")


if __name__ == '__main__':
    cli()
