import flet as ft
from backup import list_ec2_instances, list_snapshots
from datetime import datetime

def list_snapshots_panel(page: ft.Page):
    page.scroll = ft.ScrollMode.AUTO

    # Fetch EC2 instances for dropdown
    region = page.session.get("region") or "us-east-1"
    ec2_instances = list_ec2_instances(region)
    instance_options = [ft.dropdown.Option(key=i["InstanceId"], text=f"{i['InstanceId']} - {i['Name']}") for i in ec2_instances]
    default_instance_id = ec2_instances[0]["InstanceId"] if ec2_instances else None

    # State
    selected_instance_id = ft.Ref[ft.Dropdown]()
    selected_snapshot = ft.Text(value="⚠️ No snapshot selected", size=14, italic=True, color=ft.Colors.RED_400)

    def get_snapshots(instance_id):
        if not instance_id:
            return []
        snaps = list_snapshots(instance_id, region=region)
        return [
            f"{s['SnapshotId']} - {s.get('Description', 'No description')}" for s in snaps
        ]

    # Initial snapshot list
    current_instance_id = default_instance_id
    snapshots = get_snapshots(current_instance_id)

    def on_instance_change(e):
        nonlocal snapshots, current_instance_id
        current_instance_id = e.control.value
        snapshots = get_snapshots(current_instance_id)
        snapshot_list.controls = [
            ft.Container(
                content=ft.Row([
                    ft.Icon(name="backup", color=ft.Colors.ORANGE_700, size=18),
                    ft.Text(snap, size=14)
                ]),
                padding=10,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                ink=True,
                data=snap,
                on_click=on_snapshot_select,
                shadow=ft.BoxShadow(blur_radius=3, color=ft.Colors.GREY_200, offset=ft.Offset(1, 1)),
                on_hover=lambda e: setattr(e.control, "bgcolor", ft.Colors.ORANGE_50 if e.data else ft.Colors.WHITE)
            ) for snap in snapshots
        ]
        selected_snapshot.value = "⚠️ No snapshot selected"
        selected_snapshot.color = ft.Colors.RED_400
        page.update()

    def on_snapshot_select(e):
        selected_snapshot.value = f"✅ Selected: {e.control.data}"
        selected_snapshot.color = ft.Colors.GREEN_800
        page.update()

    def on_delete_click(e):
        val = selected_snapshot.value or ""
        if val.startswith("✅ Selected: "):
            snap_id = val.replace("✅ Selected: ", "").split(" - ")[0].strip()
            from backup import delete_snapshot
            success = delete_snapshot(snap_id)
            if success:
                # Remove from UI
                for i, c in enumerate(snapshot_list.controls):
                    if c.data and str(c.data).startswith(snap_id):
                        snapshot_list.controls.pop(i)
                        selected_snapshot.value = "⚠️ No snapshot selected"
                        selected_snapshot.color = ft.Colors.RED_400
                        break
                snack = ft.SnackBar(ft.Text(f"🗑️ Deleted snapshot: {snap_id}"))
                page.overlay.append(snack)
                snack.open = True
            else:
                snack = ft.SnackBar(ft.Text(f"❌ Failed to delete snapshot: {snap_id}"))
                page.overlay.append(snack)
                snack.open = True
            page.update()

    # Instance dropdown
    instance_dropdown = ft.Dropdown(
        ref=selected_instance_id,
        label="EC2 Instance",
        options=instance_options,
        value=default_instance_id,
        on_change=on_instance_change,
        width=400
    )

    # Snapshot Scroll List
    snapshot_list = ft.ListView(
        controls=[
            ft.Container(
                content=ft.Row([
                    ft.Icon(name="backup", color=ft.Colors.ORANGE_700, size=18),
                    ft.Text(snap, size=14)
                ]),
                padding=10,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                ink=True,
                data=snap,
                on_click=on_snapshot_select,
                shadow=ft.BoxShadow(blur_radius=3, color=ft.Colors.GREY_200, offset=ft.Offset(1, 1)),
                on_hover=lambda e: setattr(e.control, "bgcolor", ft.Colors.ORANGE_50 if e.data else ft.Colors.WHITE)
            ) for snap in snapshots
        ],
        height=400,
        spacing=6,
        width=540
    )

    delete_button = ft.ElevatedButton(
        "🗑️ Delete Selected Snapshot",
        icon="delete",
        on_click=on_delete_click,
        style=ft.ButtonStyle(
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor=ft.Colors.RED_600,
            color=ft.Colors.WHITE
        )
    )

    # Card Layout
    return ft.Container(
        content=ft.Column([
            ft.Text("📝 Snapshot List & Delete", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_900),
            ft.Text("View and delete your EC2 snapshots safely", size=16, color=ft.Colors.GREY_700),
            ft.Divider(height=24, thickness=1, color=ft.Colors.GREY_300),
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
                bgcolor=ft.Colors.GREY_100,
                border_radius=12,
                border=ft.border.all(1, ft.Colors.GREY_300),
                shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.GREY_200, offset=ft.Offset(2, 2)),
                width=560
            ),
            ft.Divider(height=24),
            ft.Row([
                selected_snapshot,
                ft.Container(content=delete_button, padding=ft.padding.only(left=10))
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        ], spacing=28),
        padding=32,
        bgcolor=ft.Colors.BLUE_GREY_50,
        border_radius=18
    )
