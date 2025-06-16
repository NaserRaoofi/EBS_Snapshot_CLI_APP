import flet as ft
from datetime import datetime, timedelta
from backup import list_ec2_instances

def backup_panel(page: ft.Page):
    page.scroll = ft.ScrollMode.AUTO

    # State variables (must be defined before update_instance_and_panel)
    selected_instance = ft.Ref[ft.Text]()
    selected_instance_val = {"id": None, "name": None}
    notification_text = ft.Ref[ft.Text]()
    right_panel_ref = ft.Ref[ft.Container]()
    instance_list_ref = ft.Ref[ft.Container]()

    # Fetch real instance list from backend for the selected region
    real_instances = list_ec2_instances("us-east-1")

    def on_instance_select(e):
        data = e.control.data
        selected_instance_val["id"] = data["id"]
        selected_instance_val["name"] = data["name"]
        selected_instance.current.value = f"✅ Selected: {data['id']} - {data['name']}"
        selected_instance.current.color = ft.Colors.GREEN_800
        selected_instance.current.bgcolor = ft.Colors.GREEN_50
        # Update right panel content using ref
        right_panel_ref.current.content = right_panel_content(data["id"])
        # Rebuild instance list to update row colors
        instance_scroll_list, _ = build_instance_and_panel(real_instances)
        instance_list_ref.current.content = instance_scroll_list
        page.update()

    # Helper to build instance list and right panel
    def build_instance_and_panel(instances):
        if instances:
            def get_row_bgcolor(inst_id):
                return ft.Colors.BLUE_100 if selected_instance_val["id"] == inst_id else ft.Colors.WHITE
            def get_row_border(inst_id):
                return ft.border.only(left=ft.BorderSide(6, ft.Colors.BLUE_400)) if selected_instance_val["id"] == inst_id else None
            def build_row(inst, is_last):
                row = ft.Container(
                    content=ft.Row([
                        ft.Icon(
                            name="dns",
                            color=ft.Colors.BLUE_700,
                            size=20
                        ),
                        ft.Text(f"{inst['InstanceId']} - {inst['Name']}", size=15),
                        ft.Container(
                            ft.Text("● Running", color=ft.Colors.GREEN_700, size=12),
                            padding=ft.padding.only(left=8)
                        )
                    ], expand=True),
                    padding=ft.padding.symmetric(horizontal=16, vertical=8),
                    bgcolor=get_row_bgcolor(inst['InstanceId']),
                    border_radius=12,
                    ink=True,
                    data={"id": inst['InstanceId'], "name": inst['Name']},
                    on_click=on_instance_select,
                    shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.GREY_100, offset=ft.Offset(2, 2)),
                    on_hover=lambda e: setattr(
                        e.control, "bgcolor",
                        ft.Colors.BLUE_50 if (not selected_instance_val["id"] or e.control.data["id"] != selected_instance_val["id"]) else ft.Colors.BLUE_200
                    ),
                    expand=True,
                    margin=ft.margin.only(bottom=0),
                    border=get_row_border(inst['InstanceId'])
                )
                if not is_last:
                    return ft.Column([
                        row,
                        ft.Divider(height=1, color=ft.Colors.GREY_200, thickness=1)
                    ], spacing=0)
                else:
                    return row
            instance_scroll_list = ft.Container(
                content=ft.ListView(
                    controls=[
                        build_row(inst, i == len(instances) - 1)
                        for i, inst in enumerate(instances)
                    ],
                    spacing=0,
                    expand=True,
                    auto_scroll=False,
                    height=290
                ),
                bgcolor=ft.Colors.GREY_50,
                border_radius=10,
                expand=True,
                padding=0
            )
            # The header is outside the scrollable area
            instance_list_box = ft.Column([
                ft.Row([
                    ft.Icon(name="dns", color=ft.Colors.BLUE_700, size=22),
                    ft.Text("EC2 List", size=17, weight=ft.FontWeight.W_600),
                    ft.Container(expand=True, height=1, bgcolor=ft.Colors.GREY_300)
                ], alignment=ft.MainAxisAlignment.START, spacing=8),
                instance_scroll_list
            ], spacing=10)
            right_panel_content_val = right_panel_content(instances[0]["InstanceId"])
            return instance_list_box, right_panel_content_val
        else:
            instance_scroll_list = ft.ListView(
                controls=[ft.Text("No EC2 instances found.", color=ft.Colors.RED_400, size=16)],
                height=350,
                width=340,
                spacing=7,
            )
            right_panel_content_val = ft.Column([
                ft.Text("No EC2 instances found.", size=18, color=ft.Colors.RED_400, weight=ft.FontWeight.BOLD),
                ft.Text("Please launch an EC2 instance in your AWS account.", size=15, color=ft.Colors.GREY_700)
            ], spacing=18)
            return instance_scroll_list, right_panel_content_val

    # Helper functions must be defined before right_panel_content
    def get_instance_detail(instance_id):
        inst = next((i for i in real_instances if i["InstanceId"] == instance_id), None)
        if not inst:
            return {"id": instance_id, "name": "-", "type": "-", "status": "-", "launch_time": "-", "volumes": [], "tags": {}}
        return {
            "id": inst["InstanceId"],
            "name": inst["Name"],
            "type": inst.get("InstanceType", "t2.micro"),
            "status": inst.get("State", "running"),
            "launch_time": inst.get("LaunchTime", datetime.now() - timedelta(days=12)),
            "volumes": inst.get("BlockDeviceMappings", []),
            "tags": {tag['Key']: tag['Value'] for tag in inst.get('Tags', [])} if 'Tags' in inst else {}
        }

    def get_recent_snapshots(instance_id):
        return [
            {
                "id": f"snap-0{instance_id[-1]}0{i}",
                "date": datetime.now() - timedelta(days=i),
                "status": "completed" if i % 2 else "failed",
                "size": 50,
                "tags": {"Env": "Dev", "Purpose": "Backup"},
            }
            for i in range(5)
        ]

    def get_activity_feed(instance_id):
        return [
            {"time": datetime.now() - timedelta(hours=i*2), "event": "Snapshot created", "user": "Sirwan"}
            for i in range(4)
        ]

    from backup import list_snapshots
    # --- New: right panel with details, snapshots, activity feed ---
    def right_panel_content(instance_id):
        selected_instance = get_instance_detail(instance_id)
        # Fetch real snapshots from backend with region
        region = page.session.get("region") or "us-east-1"
        real_snapshots = list_snapshots(instance_id, region=region)
        activity_feed = get_activity_feed(instance_id)
        instance_info = ft.Container(
            content=ft.Column([
                ft.Text(f"🖥️ Instance ID: {selected_instance['id']}", size=16, weight=ft.FontWeight.BOLD),
                ft.Text(f"Name: {selected_instance['name']} | Type: {selected_instance['type']} | Status: {selected_instance['status']}", size=14, color=ft.Colors.GREY_700),
                ft.Text(f"Launched: {selected_instance['launch_time'].strftime('%Y-%m-%d %H:%M')}", size=12, color=ft.Colors.GREY_500),
                ft.Text(f"Volumes: {', '.join([v['id'] for v in selected_instance['volumes']])}", size=12, color=ft.Colors.GREY_600),
                ft.Text(f"Tags: {', '.join([f'{k}:{v}' for k,v in selected_instance['tags'].items()])}", size=12, color=ft.Colors.GREY_500)
            ], spacing=6),
            padding=12,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_200)
        )
        # Show real snapshots, no delete/restore icons
        snapshot_list = ft.Column([
            ft.Row([
                ft.Text("Recent Snapshots", size=15, weight=ft.FontWeight.W_600),
                ft.Container(expand=True),
                ft.TextButton("View All")
            ]),
            ft.Container(
                ft.ListView(
                    controls=[
                        ft.Container(
                            content=ft.Row([
                                ft.Icon("cloud_done" if s.get("State", "completed") == "completed" else "error", color=ft.Colors.GREEN_700 if s.get("State", "completed") == "completed" else ft.Colors.RED_400, size=16),
                                ft.Text(s["SnapshotId"], size=13),
                                ft.Text(s["StartTime"].strftime('%Y-%m-%d'), size=12, color=ft.Colors.GREY_600),
                                ft.Text(f"{s.get('VolumeSize', '?')} GiB", size=12, color=ft.Colors.GREY_600),
                                ft.Text(", ".join([f"{t['Key']}:{t['Value']}" for t in s.get("Tags", [])]), size=11, color=ft.Colors.GREY_500),
                            ], spacing=8),
                            padding=6, border_radius=8, bgcolor=ft.Colors.GREY_100, margin=ft.margin.only(bottom=5)
                        ) for s in real_snapshots[:10]
                    ],
                    height=140,
                    spacing=4
                ),
                padding=ft.padding.only(top=8, bottom=8)
            )
        ], spacing=5)
        activity_list = ft.Column([
            ft.Text("Activity Feed", size=15, weight=ft.FontWeight.W_600),
            *[
                ft.Row([
                    ft.Icon("history", size=13, color=ft.Colors.GREY_600),
                    ft.Text(a["event"], size=12),
                    ft.Text(f"by {a['user']}", size=11, color=ft.Colors.GREY_500),
                    ft.Text(a["time"].strftime('%Y-%m-%d %H:%M'), size=10, color=ft.Colors.GREY_400),
                ], spacing=7)
                for a in activity_feed
            ]
        ], spacing=2)
        return ft.Column([
            ft.Text("📋 Instance Detail & Snapshots", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
            instance_info,
            snapshot_list,
            ft.Divider(),
            activity_list
        ], spacing=22)

    # --- Region selection state ---
    def update_instance_and_panel(region):
        global real_instances
        real_instances = list_ec2_instances(region)
        # Reset selected instance when region changes
        selected_instance_val["id"] = None
        selected_instance_val["name"] = None
        selected_instance.current.value = "⚠️ No instance selected"
        selected_instance.current.color = ft.Colors.RED_400
        selected_instance.current.bgcolor = ft.Colors.RED_50
        instance_scroll_list, right_panel_content_val = build_instance_and_panel(real_instances)
        instance_list_ref.current.content = instance_scroll_list
        right_panel_ref.current.content = right_panel_content_val
        page.update()

    def on_region_change(e):
        page.session.set("region", e.control.value)
        update_instance_and_panel(e.control.value)

    # Initial rendering
    instance_scroll_list, right_panel_content_val = build_instance_and_panel(real_instances)

    # Get region from session or default
    region_value = page.session.get("region") or "us-east-1"
    region_dropdown = ft.Dropdown(
        label="🌐 Select AWS Region",
        width=340,
        options=[
            ft.dropdown.Option(key="us-east-1", text="🇺🇸 US East (N. Virginia)"),
            ft.dropdown.Option(key="us-west-1", text="🌉 US West (N. California)"),
            ft.dropdown.Option(key="us-west-2", text="🌲 US West (Oregon)")
        ],
        value=region_value,
        tooltip="Select your AWS region",
        on_change=on_region_change
    )

    # (No duplicate helper functions after this point)

    def on_create_snapshot(e):
        # Call backend to create snapshot for selected instance
        if selected_instance_val["id"]:
            instance_id = selected_instance_val["id"]
            instance_name = selected_instance_val["name"]
            description = snapshot_description.value if snapshot_description.value else "Backup via WebUI"
            from backup import create_snapshot, get_root_volume_id, list_snapshots
            # Ensure correct region for boto3 client
            region = page.session.get("region") or "us-east-1"
            # Patch create_snapshot to accept region if needed
            try:
                snapshot_id = create_snapshot(instance_id, instance_name, description, region=region)
            except TypeError:
                # Fallback for old signature
                snapshot_id = create_snapshot(instance_id, instance_name, description)
            if snapshot_id:
                notification_text.current.value = f"✅ Snapshot created: {snapshot_id}"
                notification_text.current.color = ft.Colors.GREEN_700
                # Refresh snapshot list in right panel and update UI
                right_panel_ref.current.content = right_panel_content(instance_id)
                page.update()
            else:
                # Try to give more details if root volume is missing
                root_vol = get_root_volume_id(instance_id)
                if not root_vol:
                    notification_text.current.value = "❌ Snapshot creation failed: No root volume found for this instance."
                else:
                    notification_text.current.value = "❌ Snapshot creation failed. Check AWS permissions, region, and logs."
                notification_text.current.color = ft.Colors.RED_400
                page.update()
        else:
            notification_text.current.value = "Please select an instance first."
            notification_text.current.color = ft.Colors.RED_400
            page.update()

    ec2_search_field = ft.TextField(
        label="Search EC2 Instances",
        hint_text="Type instance name or ID",
        width=340,
        prefix_icon=ft.Icons.SEARCH,
        tooltip="Search for EC2 instances by name or ID"
    )

    snapshot_description = ft.TextField(
        label="Snapshot Description",
        value="Backup via WebUI",
        multiline=True,
        max_lines=3,
        width=340,
        tooltip="Write a description for the snapshot (optional)"
    )

    create_snapshot_button = ft.ElevatedButton(
        "📸 Create Snapshot",
        icon="camera_alt",
        on_click=on_create_snapshot,
        style=ft.ButtonStyle(
            padding=16
        )
    )

    # --- Visual Workflow Bar ---
    workflow_bar = ft.Container(
        content=ft.Row([
            ft.Icon(name="dns", color=ft.Colors.BLUE_700, size=28),
            ft.Text("1. Select EC2 Instance", size=17, weight=ft.FontWeight.W_600, color=ft.Colors.BLUE_700),
            ft.Icon(name="arrow_forward", color=ft.Colors.GREY_500, size=22),
            ft.Icon(name="photo_camera", color=ft.Colors.ORANGE_700, size=28),
            ft.Text("2. Take Snapshot", size=17, weight=ft.FontWeight.W_600, color=ft.Colors.ORANGE_700),
        ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
        padding=ft.padding.symmetric(vertical=10),
        bgcolor=ft.Colors.GREY_100,
        border_radius=10,
        margin=ft.margin.only(bottom=8)
    )

    return ft.Container(
        content=ft.Column([
            ft.Text("📸 Create EC2 Snapshot", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
            workflow_bar,
            ft.Text("Safely back up your EC2 instance volumes", size=16, color=ft.Colors.GREY_700),
            ft.Divider(height=24, thickness=1, color=ft.Colors.GREY_200),
            # --- Region & Search, center-aligned ---
            ft.Row([
                region_dropdown,
                ec2_search_field
            ], spacing=28, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Divider(height=16),
            ft.Text(ref=notification_text, value="", size=14),
            # --- Three Column Layout with expand, top-aligned ---
            ft.Row([
                # Left: Instances List
                ft.Container(
                    ref=instance_list_ref,
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(name="dns", color=ft.Colors.BLUE_700, size=22),
                            ft.Text("EC2 List", size=17, weight=ft.FontWeight.W_600),
                            ft.Container(expand=True, height=1, bgcolor=ft.Colors.GREY_300)
                        ]),
                        # No divider here
                        instance_scroll_list
                    ], spacing=10),
                    padding=18,
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=14,
                    border=ft.border.all(1, ft.Colors.GREY_200),
                    shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.GREY_100, offset=ft.Offset(2, 2)),
                    expand=True,
                    height=420
                ),
                # Middle: Selected Instance
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(name="check_circle", color=ft.Colors.GREEN_700, size=22),
                            ft.Text("Selected Instance", size=17, weight=ft.FontWeight.W_600),
                            ft.Container(expand=True, height=1, bgcolor=ft.Colors.GREY_300)
                        ]),
                        ft.Divider(height=10),
                        ft.Container(
                            ft.Text(ref=selected_instance, value="⚠️ No instance selected", size=15, italic=True, color=ft.Colors.RED_400),
                            bgcolor=ft.Colors.RED_50,
                            border_radius=8,
                            padding=8
                        ),
                        ft.Divider(height=10),
                        ft.Text("📝 Snapshot Description", size=14, weight=ft.FontWeight.W_500),
                        snapshot_description,
                        ft.Container(height=1),  # Spacer
                        ft.Container(
                            ft.ElevatedButton(
                                "📸 Create Snapshot",
                                icon="camera_alt",
                                on_click=on_create_snapshot,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.BLUE_700,
                                    color=ft.Colors.WHITE,
                                    shape=ft.RoundedRectangleBorder(radius=12),
                                    padding=20,
                                    elevation=6,
                                    overlay_color=ft.Colors.BLUE_900,
                                ),
                                width=260,
                                height=52,
                                tooltip="Create a backup snapshot of the selected EC2 instance",
                            ),
                            alignment=ft.alignment.bottom_center,
                            margin=ft.margin.only(top=18)
                        ),
                    ], spacing=18, expand=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=18,
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=14,
                    border=ft.border.all(1, ft.Colors.GREY_200),
                    shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.GREY_100, offset=ft.Offset(2, 2)),
                    expand=True,
                    height=420
                ),
                # Right: Instance Details & Snapshots
                ft.Container(
                    ref=right_panel_ref,
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(name="assignment", color=ft.Colors.BLUE_700, size=22),
                            ft.Text("Instance Detail & Snapshots", size=17, weight=ft.FontWeight.W_600),
                            ft.Container(expand=True, height=1, bgcolor=ft.Colors.GREY_300)
                        ]),
                        # No divider here
                        right_panel_content_val
                    ], spacing=10),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=18,
                    border=ft.border.all(1, ft.Colors.GREY_200),
                    shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.GREY_100, offset=ft.Offset(2,2)),
                    padding=22,
                    expand=True,
                    height=420
                )
            ], spacing=44, expand=True, vertical_alignment=ft.CrossAxisAlignment.START),
        ], spacing=34),
        padding=36,
        bgcolor=ft.Colors.BLUE_GREY_50,
        border_radius=20
    )
