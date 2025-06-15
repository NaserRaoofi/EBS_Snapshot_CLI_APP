import flet as ft

def settings_panel(page: ft.Page):
    page.scroll = ft.ScrollMode.AUTO

    # Theme mode toggle
    theme_switch = ft.Switch(label="🌗 Dark Mode", value=False, disabled=True)

    # Log level dropdown
    log_dropdown = ft.Dropdown(
        label="📋 Logging Level",
        width=400,
        value="INFO",
        disabled=True,
        options=[
            ft.dropdown.Option("DEBUG"),
            ft.dropdown.Option("INFO"),
            ft.dropdown.Option("WARNING"),
            ft.dropdown.Option("ERROR"),
            ft.dropdown.Option("CRITICAL")
        ]
    )

    # Notification preference
    notification_toggle = ft.Switch(label="🔔 Enable Notifications", value=True, disabled=True)

    # Placeholder save button
    save_button = ft.ElevatedButton(
        "💾 Save Settings",
        icon="save",
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
            ft.Text("⚙️ Application Settings", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900),
            ft.Text("Customize preferences like logging, UI mode, and more", size=16, color=ft.Colors.GREY_700),
            ft.Divider(height=24, thickness=1, color=ft.Colors.GREY_300),

            ft.Container(
                content=ft.Column([
                    theme_switch,
                    log_dropdown,
                    notification_toggle
                ], spacing=20),
                padding=20,
                bgcolor=ft.Colors.GREY_100,
                border_radius=12,
                border=ft.border.all(1, ft.Colors.GREY_300),
                shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.GREY_200),
                width=460
            ),

            ft.Divider(height=20),

            ft.Row([save_button], alignment=ft.MainAxisAlignment.CENTER)
        ], spacing=28),
        padding=32,
        bgcolor=ft.Colors.BLUE_GREY_50,
        border_radius=18
    )
