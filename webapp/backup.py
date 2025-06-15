import flet as ft

def backup_panel(page: ft.Page):
    page.scroll = ft.ScrollMode.AUTO

    # Dummy instance list
    simulated_instances = [f"i-0{str(i).zfill(4)} - web-server-{i}" for i in range(1, 21)]

    selected_instance = ft.Text(value="⚠️ No instance selected", size=14, italic=True, color=ft.Colors.RED_400)

    # --- Search Field Logic Placeholder ---
    def on_search_change(e):
        pass

    def on_instance_select(e):
        selected_instance.value = f"✅ Selected: {e.control.data}"
        selected_instance.color = ft.Colors.GREEN_800
        page.update()

    # --- UI Components ---
    region_dropdown = ft.Dropdown(
        label="🌐 Select AWS Region",
        width=400,
        options=[
            ft.dropdown.Option(key="us-east-1", text="🇺🇸 US East (N. Virginia)"),
            ft.dropdown.Option(key="us-west-1", text="🌉 US West (N. California)"),
            ft.dropdown.Option(key="us-west-2", text="🌲 US West (Oregon)")
        ],
        value="us-east-1"
    )

    ec2_search_field = ft.TextField(
        label="Search EC2 Instances",
        hint_text="Type instance name or ID",
        width=400,
        prefix_icon=ft.Icons.SEARCH,
        on_change=on_search_change
    )

    instance_scroll_list = ft.ListView(
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
            ) for inst in simulated_instances
        ],
        height=300,
        width=400,
        spacing=6,
    )

    snapshot_description = ft.TextField(
        label="Snapshot Description",
        value="Backup via WebUI",
        multiline=True,
        max_lines=3,
        width=400
    )

    create_snapshot_button = ft.ElevatedButton(
        "📸 Create Snapshot",
        icon="camera_alt",
        on_click=None,  # No logic for now
        style=ft.ButtonStyle(
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor=ft.Colors.BLUE_600,
            color=ft.Colors.WHITE
        )
    )

    loading_indicator = ft.ProgressRing(visible=False)

    return ft.Container(
        content=ft.Column([
            # --- Title Section ---
            ft.Text("🔄 Create EC2 Snapshot", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
            ft.Text("Safely back up your EC2 instance volumes", size=16, color=ft.Colors.GREY_700),
            ft.Divider(height=24, thickness=1, color=ft.Colors.GREY_200),

            # --- Region and Search ---
            ft.Row([
                region_dropdown,
                ec2_search_field
            ], spacing=20),

            ft.Divider(height=16),

            # --- Two Column Layout ---
            ft.Row([
                # Left Column: Instance list
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("📦 Available Instances", size=16, weight=ft.FontWeight.W_600),
                            ft.Container(expand=True, height=1, bgcolor=ft.Colors.GREY_300)
                        ]),
                        instance_scroll_list
                    ], spacing=14),
                    padding=20,
                    width=420,
                    bgcolor=ft.Colors.GREY_100,
                    border_radius=12,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.GREY_200, offset=ft.Offset(2, 2))
                ),

                # Right Column: Selected + Description
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("🖥️ Selected Instance", size=16, weight=ft.FontWeight.W_600),
                            ft.Container(expand=True, height=1, bgcolor=ft.Colors.GREY_300)
                        ]),
                        selected_instance,
                        ft.Divider(height=10),
                        ft.Text("📝 Snapshot Description", size=14, weight=ft.FontWeight.W_500),
                        snapshot_description,
                        ft.Row([create_snapshot_button, loading_indicator], spacing=12, alignment=ft.MainAxisAlignment.CENTER),
                    ], spacing=16),
                    padding=20,
                    width=420,
                    bgcolor=ft.Colors.GREY_100,
                    border_radius=12,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.GREY_200, offset=ft.Offset(2, 2))
                )
            ], spacing=32)
        ], spacing=28),
        padding=32,
        bgcolor=ft.Colors.BLUE_GREY_50,
        border_radius=18
    )
