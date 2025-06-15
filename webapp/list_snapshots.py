import flet as ft

def list_snapshots_panel(page: ft.Page):
    page.scroll = ft.ScrollMode.AUTO

    snapshots = [f"snap-0{str(i).zfill(4)} - Daily Backup {i}" for i in range(1, 16)]
    selected_snapshot = ft.Text(value="⚠️ No snapshot selected", size=14, italic=True, color=ft.Colors.RED_400)

    def on_snapshot_select(e):
        selected_snapshot.value = f"✅ Selected: {e.control.data}"
        selected_snapshot.color = ft.Colors.GREEN_800
        page.update()

    def on_delete_click(e):
        if selected_snapshot.value.startswith("✅ Selected: "):
            snap_id = selected_snapshot.value.replace("✅ Selected: ", "")
            for i, c in enumerate(snapshot_list.controls):
                if c.data == snap_id:
                    snapshot_list.controls.pop(i)
                    selected_snapshot.value = "⚠️ No snapshot selected"
                    selected_snapshot.color = ft.Colors.RED_400
                    break
            page.update()

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

            # Scrollable list inside visual container
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("📸 Available Snapshots", size=16, weight=ft.FontWeight.W_600),
                        ft.Container(expand=True, height=1, bgcolor=ft.Colors.GREY_300)
                    ]),
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
