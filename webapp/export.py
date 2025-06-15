import flet as ft

def export_panel(page: ft.Page):
    page.scroll = ft.ScrollMode.AUTO

    # Future export options (UI-only for now)
    export_options = ft.RadioGroup(
        content=ft.Column([
            ft.Radio(value="csv", label="📄 Export as CSV"),
            ft.Radio(value="json", label="🧾 Export as JSON"),
            ft.Radio(value="log", label="📘 Download Log File"),
        ], spacing=10),
        value="csv"
    )

    export_description = ft.TextField(
        label="📋 File Description / Note",
        hint_text="Optional short note to attach to the export",
        width=460
    )

    export_button = ft.ElevatedButton(
        "📥 Export File",
        icon="download",
        disabled=True,  # Placeholder for now
        style=ft.ButtonStyle(
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor=ft.Colors.BLUE_600,
            color=ft.Colors.WHITE
        )
    )

    # Visual preview container (mock)
    preview_card = ft.Container(
        content=ft.Column([
            ft.Text("📦 Export Preview", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.BLUE_700),
            ft.Divider(height=1, color=ft.Colors.GREY_300),
            ft.Text("• Instance ID: i-0123abcd\n• Snapshot: snap-0456\n• Region: us-west-2", size=13, color=ft.Colors.GREY_800)
        ], spacing=8),
        padding=20,
        bgcolor=ft.Colors.GREY_100,
        border_radius=12,
        border=ft.border.all(1, ft.Colors.GREY_300),
        shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.GREY_200, offset=ft.Offset(1, 1)),
        width=460
    )

    return ft.Container(
        content=ft.Column([
            ft.Text("📥 Export Logs or Snapshots", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
            ft.Text("Choose your format and prepare export-ready files", size=16, color=ft.Colors.GREY_700),
            ft.Divider(height=24, thickness=1, color=ft.Colors.GREY_300),

            ft.Container(
                content=ft.Column([
                    ft.Text("🗂️ Export Format", size=16, weight=ft.FontWeight.W_600),
                    export_options,
                    ft.Text("📝 Add Export Note", size=16, weight=ft.FontWeight.W_600),
                    export_description,
                    ft.Text("🔍 Preview Data", size=16, weight=ft.FontWeight.W_600),
                    preview_card,
                    ft.Row([export_button], alignment=ft.MainAxisAlignment.CENTER)
                ], spacing=24),
                padding=20,
                bgcolor=ft.Colors.GREY_100,
                border_radius=12,
                border=ft.border.all(1, ft.Colors.GREY_300),
                shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.GREY_200, offset=ft.Offset(2, 2)),
                width=520
            )
        ], spacing=28),
        padding=32,
        bgcolor=ft.Colors.BLUE_GREY_50,
        border_radius=18
    )
