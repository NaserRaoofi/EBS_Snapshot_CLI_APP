import flet as ft

def restore_panel(page: ft.Page):
    page.scroll = ft.ScrollMode.AUTO

    ec2_instances = [f"i-0{str(i).zfill(4)} - app-server-{i}" for i in range(1, 11)]
    snapshots = [f"snap-0{str(i).zfill(4)} - Daily Backup {i}" for i in range(1, 11)]

    selected_instance = ft.Text(value="⚠️ No instance selected", size=14, italic=True, color=ft.Colors.RED_400)
    selected_snapshot = ft.Text(value="⚠️ No snapshot selected", size=14, italic=True, color=ft.Colors.RED_400)

    # --- Selection Handlers ---
    def on_instance_select(e):
        selected_instance.value = f"✅ Selected Instance: {e.control.data}"
        selected_instance.color = ft.Colors.GREEN_800
        page.update()

    def on_snapshot_select(e):
        selected_snapshot.value = f"✅ Selected Snapshot: {e.control.data}"
        selected_snapshot.color = ft.Colors.GREEN_800
        page.update()

    # --- UI Lists ---
    ec2_list = ft.ListView(
        controls=[
            ft.Container(
                content=ft.Row([
                    ft.Icon(name="dns", color=ft.Colors.BLUE_700, size=18),
                    ft.Text(inst, size=14)
                ]),
                padding=10,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                ink=True,
                data=inst,
                on_click=on_instance_select,
                shadow=ft.BoxShadow(blur_radius=3, color=ft.Colors.GREY_200, offset=ft.Offset(1, 1)),
                on_hover=lambda e: setattr(e.control, "bgcolor", ft.Colors.BLUE_50 if e.data else ft.Colors.WHITE)
            ) for inst in ec2_instances
        ],
        height=300,
        spacing=6,
        width=420
    )

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
        height=300,
        spacing=6,
        width=420
    )

    # --- Restore Button ---
    restore_button = ft.ElevatedButton(
        "🧩 Restore Snapshot",
        icon="restore",
        on_click=None,  # Connect later
        style=ft.ButtonStyle(
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor=ft.Colors.GREEN_600,
            color=ft.Colors.WHITE
        )
    )

    return ft.Container(
        content=ft.Column([
            ft.Text("🧩 Restore from Snapshot", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_900),
            ft.Text("Attach a snapshot to a selected EC2 instance", size=16, color=ft.Colors.GREY_700),
            ft.Divider(height=24, thickness=1, color=ft.Colors.GREY_300),

            # --- Main Selection Layout ---
            ft.Row([
                # EC2 Column
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("🖥️ Available EC2 Instances", size=16, weight=ft.FontWeight.W_600),
                            ft.Container(expand=True, height=1, bgcolor=ft.Colors.GREY_300)
                        ]),
                        ec2_list
                    ], spacing=14),
                    padding=20,
                    width=440,
                    bgcolor=ft.Colors.GREY_100,
                    border_radius=12,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.GREY_200, offset=ft.Offset(2, 2))
                ),

                # Snapshot Column
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("📸 Available Snapshots", size=16, weight=ft.FontWeight.W_600),
                            ft.Container(expand=True, height=1, bgcolor=ft.Colors.GREY_300)
                        ]),
                        snapshot_list
                    ], spacing=14),
                    padding=20,
                    width=440,
                    bgcolor=ft.Colors.GREY_100,
                    border_radius=12,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.GREY_200, offset=ft.Offset(2, 2))
                )
            ], spacing=32),

            ft.Divider(height=24),

            # --- Selection Summary + Restore ---
            ft.Row([
                ft.Column([selected_instance], spacing=8, expand=True),
                ft.Column([selected_snapshot], spacing=8, expand=True),
                ft.Container(content=restore_button, padding=ft.padding.only(left=10))
            ], alignment=ft.MainAxisAlignment.CENTER)
        ], spacing=28),
        padding=32,
        bgcolor=ft.Colors.BLUE_GREY_50,
        border_radius=18
    )
