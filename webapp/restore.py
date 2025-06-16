import flet as ft
from datetime import datetime
from typing import Any
from backup import list_ec2_instances, list_snapshots

def restore_panel(page: ft.Page):
    page.scroll = ft.ScrollMode.AUTO

    # --- State ---
    selected_snapshot: dict[str, Any] = {"obj": None}
    selected_instance: dict[str, Any] = {"obj": None}
    progress = ft.Ref[ft.ProgressRing]()
    details_ref = ft.Ref[ft.Container]()
    history_ref = ft.Ref[ft.Column]()
    dialog_ref = ft.Ref[ft.AlertDialog]()
    snack_ref = ft.Ref[ft.SnackBar]()
    restore_history = []

    # --- Fetch real data from backend ---
    region = page.session.get("region") or "us-east-1"
    ec2_instances_raw = list_ec2_instances(region)
    ec2_instances = [
        {
            "id": i["InstanceId"],
            "name": i["Name"],
            "type": i.get("InstanceType", "t3.medium"),
            "status": "running",  # Only running are listed
            "launch_time": i.get("LaunchTime", datetime.now()),
            "volumes": [],  # Could be filled with describe_instances if needed
        }
        for i in ec2_instances_raw
    ]
    # For snapshot list, default to first instance if available
    default_instance_id = ec2_instances[0]["id"] if ec2_instances else None
    snapshots_raw = list_snapshots(default_instance_id, region=region) if default_instance_id else []
    snapshots = [
        {
            "id": s["SnapshotId"],
            "desc": s.get("Description", "No description"),
            "date": s["StartTime"],
            "size": s.get("VolumeSize", 0),
            "source_instance": next((t["Value"] for t in s.get("Tags", []) if t["Key"] == "instance-id"), "-"),
            "volumes": [],  # Could be filled with describe_snapshots if needed
        }
        for s in snapshots_raw
    ]

    def safe_vol_ids(vols):
        if not isinstance(vols, list):
            return []
        return [v['id'] for v in vols if v and isinstance(v, dict) and 'id' in v]

    # --- Visual Guide ---
    visual_guide = ft.Container(
        content=ft.Row([
            ft.Icon(name="photo_camera", color=ft.Colors.ORANGE_700, size=28),
            ft.Text("1. Select Snapshot", size=17, weight=ft.FontWeight.W_600, color=ft.Colors.ORANGE_700),
            ft.Icon(name="arrow_forward", color=ft.Colors.GREY_500, size=22),
            ft.Icon(name="dns", color=ft.Colors.BLUE_700, size=28),
            ft.Text("2. Select EC2 Instance", size=17, weight=ft.FontWeight.W_600, color=ft.Colors.BLUE_700),
            ft.Icon(name="arrow_forward", color=ft.Colors.GREY_500, size=22),
            ft.Icon(name="restore", color=ft.Colors.GREEN_900, size=28),
            ft.Text("3. Restore!", size=17, weight=ft.FontWeight.W_600, color=ft.Colors.GREEN_900),
        ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
        padding=ft.padding.symmetric(vertical=10),
        bgcolor=ft.Colors.GREY_100,
        border_radius=10,
        margin=ft.margin.only(bottom=8)
    )

    # --- Improved Snapshot Detail Box ---
    def show_details():
        if selected_snapshot["obj"] or selected_instance["obj"]:
            snapshot = selected_snapshot["obj"]
            instance = selected_instance["obj"]
            lines = []
            if snapshot:
                vols = snapshot.get('volumes')
                # Modern table-style snapshot details
                lines += [
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(name="photo_camera", color=ft.Colors.ORANGE_700, size=22),
                                ft.Text("Snapshot Details", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.ORANGE_700),
                            ], spacing=10),
                            ft.Divider(height=8),
                            ft.Container(
                                content=ft.Column([
                                    ft.Row([
                                        ft.Text("ID", size=13, color=ft.Colors.GREY_700, width=110),
                                        ft.Text(snapshot['id'], size=13, selectable=True, color=ft.Colors.GREY_900, width=200),
                                    ], spacing=10),
                                    ft.Divider(height=1, color=ft.Colors.GREY_200),
                                    ft.Row([
                                        ft.Text("Description", size=13, color=ft.Colors.GREY_700, width=110),
                                        ft.Text(snapshot['desc'], size=13, color=ft.Colors.GREY_900, width=200),
                                    ], spacing=10),
                                    ft.Divider(height=1, color=ft.Colors.GREY_200),
                                    ft.Row([
                                        ft.Text("Date", size=13, color=ft.Colors.GREY_700, width=110),
                                        ft.Text(snapshot['date'].strftime('%Y-%m-%d'), size=13, color=ft.Colors.GREY_900, width=90),
                                        ft.Text("Size", size=13, color=ft.Colors.GREY_700, width=40),
                                        ft.Text(f"{snapshot['size']} GiB", size=13, color=ft.Colors.GREY_900, width=60),
                                    ], spacing=10),
                                    ft.Divider(height=1, color=ft.Colors.GREY_200),
                                    ft.Row([
                                        ft.Text("Source Instance", size=13, color=ft.Colors.GREY_700, width=110),
                                        ft.Text(snapshot['source_instance'], size=13, color=ft.Colors.GREY_900, width=200),
                                    ], spacing=10),
                                    ft.Divider(height=1, color=ft.Colors.GREY_200),
                                    ft.Row([
                                        ft.Text("Volumes", size=13, color=ft.Colors.GREY_700, width=110),
                                        ft.Text(", ".join(safe_vol_ids(vols)), size=13, color=ft.Colors.GREY_900, width=200),
                                    ], spacing=10),
                                ], spacing=4),
                                bgcolor=ft.Colors.ORANGE_50,
                                border_radius=10,
                                padding=ft.padding.symmetric(vertical=10, horizontal=16),
                                border=ft.border.all(1, ft.Colors.ORANGE_100),
                                width=340,
                            ),
                        ], spacing=6),
                        margin=ft.margin.only(bottom=8),
                        width=360,
                        alignment=ft.alignment.top_left
                    )
                ]
            if instance:
                vols = instance.get('volumes')
                lines += [
                    ft.Divider(),
                    ft.Text(f"🖥️ Instance: {instance['id']}", size=15, weight=ft.FontWeight.W_600),
                    ft.Text(f"Name: {instance['name']}  |  Type: {instance['type']}  |  Status: {instance['status']}", size=13),
                    ft.Text(f"Launched: {instance['launch_time'].strftime('%Y-%m-%d')}", size=12),
                    ft.Text(f"Volumes: {', '.join(safe_vol_ids(vols))}", size=12),
                ]
            details_ref.current.content = ft.Column(lines, spacing=7)
        else:
            details_ref.current.content = ft.Text("ℹ️ Select a snapshot and instance to preview details.", color=ft.Colors.GREY_500)
        page.update()

    def show_snack(msg):
        snack = ft.SnackBar(ft.Text(msg))
        snack_ref.current = snack
        page.overlay.append(snack)
        snack.open = True
        page.update()

    def show_dialog(dialog):
        dialog_ref.current = dialog
        if dialog not in page.overlay:
            page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def close_dialog():
        if dialog_ref.current:
            dialog_ref.current.open = False
            page.update()

    def on_snapshot_select(e):
        snap_id = e.control.data
        snap_obj = next((s for s in snapshots if s["id"] == snap_id), None)
        selected_snapshot["obj"] = snap_obj
        show_details()

    def on_instance_select(e):
        inst_id = e.control.data
        inst_obj = next((i for i in ec2_instances if i["id"] == inst_id), None)
        selected_instance["obj"] = inst_obj
        # Rebuild EC2 list to update highlight
        ec2_list.controls = [
            ft.Container(
                content=ft.Row([
                    ft.Icon(name="dns", color=ft.Colors.BLUE_700, size=18),
                    ft.Text(f"{inst['id']} - {inst['name']}", size=14)
                ]),
                padding=10,
                bgcolor=ft.Colors.BLUE_100 if selected_instance["obj"] and selected_instance["obj"]["id"] == inst["id"] else ft.Colors.WHITE,
                border_radius=12,
                ink=True,
                data=inst['id'],
                on_click=on_instance_select,
                shadow=ft.BoxShadow(blur_radius=3, color=ft.Colors.GREY_200, offset=ft.Offset(1, 1)),
                on_hover=lambda e: setattr(
                    e.control, "bgcolor",
                    ft.Colors.BLUE_50 if (not selected_instance["obj"] or e.control.data != selected_instance["obj"]["id"]) else ft.Colors.BLUE_100
                )
            ) for inst in ec2_instances
        ]
        show_details()
        page.update()

    def on_restore(e):
        # Confirmation modal with restore summary
        if not selected_snapshot["obj"] or not selected_instance["obj"]:
            show_snack("Select both snapshot and EC2 instance.")
            return

        def do_restore(confirm_e):
            progress.current.visible = True
            page.update()
            from restore import restore_snapshot_to_instance_web
            snap_id = selected_snapshot["obj"]["id"]
            inst_id = selected_instance["obj"]["id"]
            result = restore_snapshot_to_instance_web(snap_id, inst_id, region)
            progress.current.visible = False
            status = result.get("status")
            msg = result.get("message", "Unknown error")
            restore_history.insert(0, {
                "when": datetime.now(),
                "snapshot": snap_id,
                "instance": inst_id,
                "status": "Success" if status == "success" else "Failed",
            })
            refresh_history()
            close_dialog()
            show_snack(msg)
            page.update()

        # --- Modern, professional modal with visual process diagram ---
        snap = selected_snapshot["obj"]
        inst = selected_instance["obj"]
        # Visual process diagram: Source EC2 -> Snapshot -> Target EC2
        process_diagram = ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Icon(name="dns", color=ft.Colors.BLUE_700, size=38),
                    ft.Text("Source EC2", size=15, weight=ft.FontWeight.W_600, color=ft.Colors.BLUE_700),
                    ft.Text(snap["source_instance"], size=13, color=ft.Colors.GREY_800, selectable=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
                width=180,
                alignment=ft.alignment.center,
            ),
            ft.Icon(name="arrow_forward", color=ft.Colors.GREY_500, size=38),
            ft.Container(
                content=ft.Column([
                    ft.Icon(name="photo_camera", color=ft.Colors.ORANGE_700, size=38),
                    ft.Text("Snapshot", size=15, weight=ft.FontWeight.W_600, color=ft.Colors.ORANGE_700),
                    ft.Text(snap["id"], size=13, color=ft.Colors.GREY_800, selectable=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(snap["desc"], size=12, color=ft.Colors.GREY_600, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(f"{snap['date'].strftime('%Y-%m-%d')} | {snap['size']} GiB", size=12, color=ft.Colors.GREY_600),
                ], spacing=2, alignment=ft.MainAxisAlignment.CENTER),
                width=260,
                alignment=ft.alignment.center,
            ),
            ft.Icon(name="arrow_forward", color=ft.Colors.GREY_500, size=38),
            ft.Container(
                content=ft.Column([
                    ft.Icon(name="dns", color=ft.Colors.GREEN_700, size=38),
                    ft.Text("Target EC2", size=15, weight=ft.FontWeight.W_600, color=ft.Colors.GREEN_700),
                    ft.Text(inst["id"], size=13, color=ft.Colors.GREY_800, selectable=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(inst["name"], size=12, color=ft.Colors.GREY_600, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                ], spacing=2, alignment=ft.MainAxisAlignment.CENTER),
                width=180,
                alignment=ft.alignment.center,
            ),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=32)

        summary = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(name="warning_amber", color=ft.Colors.RED_600, size=32),
                    ft.Text("Confirm Restore Operation", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_700),
                ], spacing=14, alignment=ft.MainAxisAlignment.START),
                ft.Divider(height=8),
                process_diagram,
                ft.Divider(height=8),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("Snapshot", size=15, color=ft.Colors.GREY_700, width=110),
                            ft.Text(snap["id"] if snap else "-", size=15, color=ft.Colors.GREY_900),
                        ], spacing=10),
                        ft.Row([
                            ft.Text("EC2 Instance", size=15, color=ft.Colors.GREY_700, width=110),
                            ft.Text(inst["id"] if inst else "-", size=15, color=ft.Colors.GREY_900),
                        ], spacing=10),
                        ft.Row([
                            ft.Text("Instance Name", size=15, color=ft.Colors.GREY_700, width=110),
                            ft.Text(inst["name"] if inst else "-", size=15, color=ft.Colors.GREY_900),
                        ], spacing=10),
                    ], spacing=8),
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=10,
                    padding=ft.padding.symmetric(vertical=8, horizontal=16),
                    border=ft.border.all(1, ft.Colors.GREY_200),
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(name="error", color=ft.Colors.RED_400, size=20),
                        ft.Text("This action will overwrite the root volume of the selected EC2 instance.", color=ft.Colors.RED_600, size=15, weight=ft.FontWeight.W_600),
                    ], spacing=8),
                    bgcolor=ft.Colors.RED_50,
                    border_radius=8,
                    padding=ft.padding.symmetric(vertical=6, horizontal=12),
                    margin=ft.margin.only(top=10, bottom=2)
                ),
            ], spacing=10),
            width=1200,  # 3x wider
            height=260,  # half the previous height
            padding=ft.padding.symmetric(vertical=10, horizontal=32),
        )
        dialog = ft.AlertDialog(
            modal=True,
            title=None,
            content=summary,
            actions_alignment=ft.MainAxisAlignment.END,
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: close_dialog()),
                ft.ElevatedButton("Proceed", bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE, on_click=do_restore)
            ],
            shape=ft.RoundedRectangleBorder(radius=18),
            bgcolor=ft.Colors.WHITE
        )
        show_dialog(dialog)

    def refresh_history():
        if not restore_history:
            history_ref.current.controls = [ft.Text("No restore history.", color=ft.Colors.GREY_400)]
        else:
            history_ref.current.controls = [
                ft.Row([
                    ft.Text(f"{h['when'].strftime('%Y-%m-%d %H:%M')}", size=12, color=ft.Colors.GREY_600),
                    ft.Text(f"Restored {h['snapshot']} to {h['instance']}", size=13),
                    ft.Text(h['status'], size=12, color=ft.Colors.GREEN_800 if h['status']=='Success' else ft.Colors.RED_700),
                ], spacing=12)
                for h in restore_history[:5]
            ]
        page.update()

    # --- Instance selection for snapshot list ---
    selected_instance_id = ft.Ref[ft.Dropdown]()
    
    def update_snapshots_list(instance_id):
        snaps_raw = list_snapshots(instance_id, region=region) if instance_id else []
        snaps = [
            {
                "id": s["SnapshotId"],
                "desc": s.get("Description", "No description"),
                "date": s["StartTime"],
                "size": s.get("VolumeSize", 0),
                "source_instance": next((t["Value"] for t in s.get("Tags", []) if t["Key"] == "instance-id"), "-"),
                "volumes": [],
            }
            for s in snaps_raw
        ]
        return snaps

    # Initial instance for snapshot list
    snapshot_instance_id = ec2_instances[0]["id"] if ec2_instances else None
    snapshots = update_snapshots_list(snapshot_instance_id)

    def on_instance_dropdown_change(e):
        nonlocal snapshots
        instance_id = e.control.value
        snapshots = update_snapshots_list(instance_id)
        # Rebuild snapshot_list UI
        snapshot_list.controls = [
            ft.Container(
                content=ft.Row([
                    ft.Icon(name="backup", color=ft.Colors.ORANGE_700, size=18),
                    ft.Text(f"{snap['id']} - {snap['desc']}", size=14)
                ]),
                padding=10,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                ink=True,
                data=snap['id'],
                on_click=on_snapshot_select,
                shadow=ft.BoxShadow(blur_radius=3, color=ft.Colors.GREY_200, offset=ft.Offset(1, 1)),
                on_hover=lambda e: setattr(e.control, "bgcolor", ft.Colors.ORANGE_50 if e.data else ft.Colors.WHITE)
            ) for snap in snapshots
        ]
        page.update()

    # Dropdown for selecting instance to show snapshots for
    instance_dropdown = ft.Dropdown(
        ref=selected_instance_id,
        label="Instance for Snapshots",
        options=[ft.dropdown.Option(key=inst["id"], text=f"{inst['id']} - {inst['name']}") for inst in ec2_instances],
        value=snapshot_instance_id,
        on_change=on_instance_dropdown_change,
        width=340
    )

    # --- UI Lists ---
    snapshot_list = ft.ListView(
        controls=[
            ft.Container(
                content=ft.Row([
                    ft.Icon(name="backup", color=ft.Colors.ORANGE_700, size=18),
                    ft.Text(f"{snap['id']} - {snap['desc']}", size=14)
                ]),
                padding=10,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                ink=True,
                data=snap['id'],
                on_click=on_snapshot_select,
                shadow=ft.BoxShadow(blur_radius=3, color=ft.Colors.GREY_200, offset=ft.Offset(1, 1)),
                on_hover=lambda e: setattr(e.control, "bgcolor", ft.Colors.ORANGE_50 if e.data else ft.Colors.WHITE)
            ) for snap in snapshots
        ],
        height=300,
        spacing=6,
        width=380
    )

    ec2_list = ft.ListView(
        controls=[
            ft.Container(
                content=ft.Row([
                    ft.Icon(name="dns", color=ft.Colors.BLUE_700, size=18),
                    ft.Text(f"{inst['id']} - {inst['name']}", size=14)
                ]),
                padding=10,
                bgcolor=ft.Colors.BLUE_100 if selected_instance["obj"] and selected_instance["obj"]["id"] == inst["id"] else ft.Colors.WHITE,
                border_radius=12,
                ink=True,
                data=inst['id'],
                on_click=on_instance_select,
                shadow=ft.BoxShadow(blur_radius=3, color=ft.Colors.GREY_200, offset=ft.Offset(1, 1)),
                on_hover=lambda e: setattr(
                    e.control, "bgcolor",
                    ft.Colors.BLUE_50 if (not selected_instance["obj"] or e.control.data != selected_instance["obj"]["id"]) else ft.Colors.BLUE_100
                )
            ) for inst in ec2_instances
        ],
        height=300,
        spacing=6,
        width=380
    )

    restore_button = ft.ElevatedButton(
        "🧩 Restore Snapshot",
        icon="restore",
        on_click=on_restore,
        style=ft.ButtonStyle(
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor=ft.Colors.GREEN_600,
            color=ft.Colors.WHITE
        )
    )

    # --- Layout ---
    # Professional animated workflow arrows using Flet Icon and animation
    animated_arrow1 = ft.AnimatedSwitcher(
        content=ft.Icon(name="subdirectory_arrow_right", color=ft.Colors.BLUE_400, size=60, rotate=ft.Rotate(angle=-0.18)),
        duration=600,
        transition=ft.AnimatedSwitcherTransition.FADE,
    )
    animated_arrow2 = ft.AnimatedSwitcher(
        content=ft.Icon(name="subdirectory_arrow_right", color=ft.Colors.GREEN_400, size=60, rotate=ft.Rotate(angle=0.18)),
        duration=600,
        transition=ft.AnimatedSwitcherTransition.FADE,
    )
    workflow_arrows = ft.Stack([
        ft.Container(animated_arrow1, left=440, top=120),
        ft.Container(animated_arrow2, left=860, top=120),
    ], width=1400, height=320)

    return ft.Container(
        content=ft.Column([
            ft.Text("🧩 Restore from Snapshot", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_900),
            visual_guide,
            ft.Text("Select a snapshot, then choose target EC2 instance, then restore.", size=16, color=ft.Colors.GREY_700),
            ft.Divider(height=24, thickness=1, color=ft.Colors.GREY_300),
            ft.Stack([
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text("📸 Available Snapshots", size=16, weight=ft.FontWeight.W_600),
                                ft.Container(expand=True, height=1, bgcolor=ft.Colors.GREY_300)
                            ]),
                            instance_dropdown,
                            snapshot_list
                        ], spacing=14),
                        padding=20,
                        width=400,
                        bgcolor=ft.Colors.GREY_100,
                        border_radius=12,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.GREY_200, offset=ft.Offset(2, 2))
                    ),
                    ft.Container(width=120),  # Increased gap
                    ft.Container(
                        ref=details_ref,
                        content=ft.Text("ℹ️ Select a snapshot and instance to preview details.", color=ft.Colors.GREY_500),
                        padding=20,
                        width=340,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=12,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.GREY_100, offset=ft.Offset(2, 2))
                    ),
                    ft.Container(width=120),  # Increased gap
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text("🖥️ Available EC2 Instances", size=16, weight=ft.FontWeight.W_600),
                                ft.Container(expand=True, height=1, bgcolor=ft.Colors.GREY_300)
                            ]),
                            ec2_list
                        ], spacing=14),
                        padding=20,
                        width=400,
                        bgcolor=ft.Colors.GREY_100,
                        border_radius=12,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.GREY_200, offset=ft.Offset(2, 2))
                    ),
                ], spacing=0),
                workflow_arrows  # Overlay the arrows
            ], width=1600, height=340),
            ft.Divider(height=24),
            ft.Row([
                ft.ProgressRing(ref=progress, visible=False),
                ft.Container(content=restore_button, alignment=ft.alignment.bottom_right, expand=True),
            ], alignment=ft.MainAxisAlignment.END),
            ft.Divider(),
            ft.Text("📝 Restore History", size=16, weight=ft.FontWeight.W_600),
            ft.Column(ref=history_ref, controls=[ft.Text("No restore history.", color=ft.Colors.GREY_400)]),
        ], spacing=20),
        padding=32,
        bgcolor=ft.Colors.BLUE_GREY_50,
        border_radius=18
    )
