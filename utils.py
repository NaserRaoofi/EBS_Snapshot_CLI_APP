from dotenv import set_key, unset_key, dotenv_values
import os

ENV_FILE = os.path.join(os.path.dirname(__file__), '.env')


def add_snapshot_to_env(snapshot_id, instance_id):
    config = dotenv_values(ENV_FILE)

    # Collect keys that belong to this instance
    prefix = f"SNAPSHOT_{instance_id}_"
    instance_keys = {k: v for k, v in config.items() if k.startswith(prefix)}
    new_index = len(instance_keys) + 1

    # Save under SNAPSHOT_instanceid_index
    key = f"{prefix}{new_index}"
    set_key(ENV_FILE, key, snapshot_id)

    # Optionally update LATEST_SNAPSHOT
    set_key(ENV_FILE, "LATEST_SNAPSHOT", snapshot_id)


def remove_snapshot_from_env(snapshot_id):
    config = dotenv_values(ENV_FILE)

    for k, v in config.items():
        if v == snapshot_id and k.startswith("SNAPSHOT_"):
            unset_key(ENV_FILE, k)

    if config.get("LATEST_SNAPSHOT") == snapshot_id:
        unset_key(ENV_FILE, "LATEST_SNAPSHOT")


def save_instance_ids_to_env(instance_ids):
    ids_str = ",".join(instance_ids)
    set_key(ENV_FILE, "ALL_INSTANCE_IDS", ids_str)
