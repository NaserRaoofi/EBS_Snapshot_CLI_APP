import flet as ft

def iam_panel(page: ft.Page):
    page.scroll = ft.ScrollMode.AUTO

    # Dummy IAM entries (placeholder)
    credentials = [
        {"profile": "default", "access_key": "AKIA...1234", "status": "Active"},
        {"profile": "prod-admin", "access_key": "AKIA...5678", "status": "Inactive"},
    ]

    profile_cards = [
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(f"🔐 Profile: {cred['profile']}", size=16, weight=ft.FontWeight.W_600),
                    ft.Container(
                        content=ft.Text(f"{cred['status']}", size=12, color=ft.Colors.GREEN_700 if cred["status"] == "Active" else ft.Colors.RED_600),
                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
                        bgcolor=ft.Colors.GREEN_100 if cred["status"] == "Active" else ft.Colors.RED_100,
                        border_radius=8
                    )
                ]),
                ft.Text(f"Access Key: {cred['access_key']}", size=13, color=ft.Colors.GREY_800),
                ft.Row([
                    ft.ElevatedButton("🔁 Rotate Key", icon="autorenew", disabled=True),
                    ft.OutlinedButton("⛔ Revoke", disabled=True)
                ], spacing=10)
            ], spacing=8),
            padding=16,
            bgcolor=ft.Colors.GREY_100,
            border_radius=12,
            border=ft.border.all(1, ft.Colors.GREY_300),
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.GREY_200),
            width=480
        )
        for cred in credentials
    ]

    add_role_button = ft.ElevatedButton(
        "➕ Add New Role",
        icon="add",
        disabled=True,
        style=ft.ButtonStyle(
            padding=18,
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE
        )
    )

    return ft.Container(
        content=ft.Column([
            ft.Text("🔐 IAM & Credential Management", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
            ft.Text("Manage your AWS access keys, roles, and credential profiles", size=16, color=ft.Colors.GREY_700),
            ft.Divider(height=24, thickness=1, color=ft.Colors.GREY_300),
            ft.Column(profile_cards, spacing=20),
            ft.Divider(height=20),
            ft.Row([add_role_button], alignment=ft.MainAxisAlignment.CENTER)
        ], spacing=28),
        padding=32,
        bgcolor=ft.Colors.BLUE_GREY_50,
        border_radius=18
    )
