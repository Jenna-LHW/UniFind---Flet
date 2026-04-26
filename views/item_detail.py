import flet as ft
from api import get_lost_item, get_found_item
from storage import load_tokens

BROWN = '#5c4f3a'
GREEN = '#3b5c38'
LIGHT = '#f5f2ee'
BORDER = '#e8e2da'
TEXT_MAIN  = '#2c2c2a'
TEXT_MUTED = '#7a7670'

def item_detail_view(page: ft.Page, go, item_type: str, item_id: int):
    accent     = GREEN if item_type == 'found' else BROWN
    loading    = ft.ProgressRing(visible=True, color=accent)
    error_text = ft.Text('', color=ft.Colors.RED_600)
    body       = ft.Column(spacing=12)

    access, _ = load_tokens()
    is_auth   = bool(access)

    def load():
        if item_type == 'lost':
            status, data = get_lost_item(item_id)
        else:
            status, data = get_found_item(item_id)
        loading.visible = False
        if status != 200:
            error_text.value = 'Failed to load item details.'
            page.update(); return
        _render(data)
        page.update()

    def _render(item):
        photo_url   = item.get('photo_url')
        name        = item.get('item_name', '')
        category    = item.get('category', '').replace('_', ' ').title()
        description = item.get('description', '')
        status_val  = item.get('status', '')
        reported_by = item.get('reported_by', '')
        submitted   = item.get('submitted_at', '')[:10]

        if item_type == 'lost':
            location_label = 'Last seen at'
            location_value = item.get('last_seen', '')
            date_label     = 'Date lost'
            date_value     = item.get('date_lost', '')
            type_label     = 'LOST'
            type_color     = '#7a3f3a'
            claim_title    = 'Did you find this item?'
            claim_body     = 'Submit a report so the owner can be notified.'
            claim_btn_text = 'I found this item'
        else:
            location_label = 'Found at'
            location_value = item.get('found_at', '')
            date_label     = 'Date found'
            date_value     = item.get('date_found', '')
            type_label     = 'FOUND'
            type_color     = '#2e5c3a'
            claim_title    = 'Is this your item?'
            claim_body     = 'Submit a claim with proof of ownership.'
            claim_btn_text = 'Claim this item'

        if photo_url:
            photo_widget = ft.Image(src=photo_url, width=None, height=220,
                                    fit='cover', border_radius=16)
        else:
            photo_widget = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED_OUTLINED, color='#c4bdb4', size=40),
                    ft.Text('No photo provided', size=12, color=TEXT_MUTED),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
                height=160, bgcolor='#f5f2ee', border_radius=16,
                alignment=ft.Alignment(0, 0),
            )

        status_colors = {
            'pending':  ('#faeeda', '#854f0b'),
            'found':    ('#eaf3de', '#27500a'),
            'claimed':  ('#e6f1fb', '#0c447c'),
            'resolved': ('#eaf3de', '#27500a'),
        }
        badge_bg, badge_fg = status_colors.get(status_val, ('#f5f2ee', TEXT_MUTED))

        if status_val == 'resolved':
            action_box = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, color='#27500a', size=20),
                    ft.Text('This item has been reunited with its owner.',
                            size=13, color='#27500a', weight=ft.FontWeight.W_500, expand=True),
                ], spacing=10),
                padding=14, bgcolor='#eaf3de', border_radius=12,
                border=ft.border.all(1, '#c4dca8'),
            )
        elif not is_auth:
            action_box = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.LOCK_OUTLINE_ROUNDED, color=TEXT_MUTED, size=18),
                    ft.Text('Log in to submit a claim.', size=13, color=TEXT_MUTED, expand=True),
                    ft.TextButton('Log in', on_click=lambda e: go('login'),
                                  style=ft.ButtonStyle(color=accent)),
                ], spacing=10),
                padding=14, bgcolor='#f9f7f4', border_radius=12,
                border=ft.border.all(1, BORDER),
            )
        else:
            action_box = ft.Container(
                content=ft.Column([
                    ft.Text(claim_title, size=14, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Text(claim_body, size=12, color=TEXT_MUTED),
                    ft.Container(height=4),
                    ft.ElevatedButton(
                        claim_btn_text,
                        bgcolor=accent, color='white',
                        height=46, expand=True,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                        on_click=lambda e: go(f'submit_claim_{item_type}_{item_id}'),
                    ),
                ], spacing=4),
                padding=16, bgcolor='#f9f7f4', border_radius=12,
                border=ft.border.all(1, BORDER),
            )

        body.controls = [
            photo_widget,

            # Title row
            ft.Row([
                ft.Column([
                    ft.Text(name, size=20, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Container(
                        content=ft.Text(type_label, color='white', size=10,
                                        weight=ft.FontWeight.BOLD),
                        bgcolor=type_color,
                        padding=ft.padding.symmetric(horizontal=10, vertical=3),
                        border_radius=20,
                    ),
                ], spacing=6, expand=True),
                ft.Container(
                    content=ft.Text(status_val.capitalize(), size=11,
                                    weight=ft.FontWeight.BOLD, color=badge_fg),
                    bgcolor=badge_bg,
                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                    border_radius=20,
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.START),

            # Description
            ft.Container(
                content=ft.Column([
                    ft.Text('Description', size=11, weight=ft.FontWeight.W_600,
                            color='#9a8f80', style=ft.TextStyle(letter_spacing=0.8)),
                    ft.Text(description, size=13, color='#3c3c3a', selectable=True),
                ], spacing=6),
                padding=14,
                bgcolor='white',
                border_radius=12,
                border=ft.border.all(1, BORDER),
            ),

            # Meta grid
            ft.Row([
                _meta_tile(ft.Icons.LOCATION_ON_OUTLINED, location_label,
                           location_value or '—', accent),
                _meta_tile(ft.Icons.CALENDAR_TODAY_OUTLINED, date_label,
                           date_value or '—', accent),
            ], spacing=10),
            ft.Row([
                _meta_tile(ft.Icons.LABEL_OUTLINE_ROUNDED, 'Category', category or '—', accent),
                _meta_tile(ft.Icons.PERSON_OUTLINE_ROUNDED, 'Reported by',
                           str(reported_by) if reported_by else '—', accent),
            ], spacing=10),

            ft.Text(f'Submitted {submitted}', size=11, color='#9a8f80'),

            action_box,

            ft.TextButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, size=14, color=accent),
                    ft.Text(f'Back to Browse {"Lost" if item_type == "lost" else "Found"}',
                            size=13, color=accent),
                ], spacing=4),
                on_click=lambda e: go(f'browse_{item_type}'),
            ),
        ]

    load()

    return ft.Column([error_text, loading, body],
                     spacing=0, scroll=ft.ScrollMode.AUTO)


def _meta_tile(icon, label, value, accent):
    return ft.Container(
        content=ft.Row([
            ft.Container(
                content=ft.Icon(icon, size=16, color=accent),
                width=32, height=32,
                bgcolor='#ede8e0',
                border_radius=8,
                alignment=ft.Alignment(0, 0),
            ),
            ft.Column([
                ft.Text(label, size=10, color='#9a8f80',
                        style=ft.TextStyle(letter_spacing=0.4)),
                ft.Text(value, size=12, weight=ft.FontWeight.W_600,
                        color='#2c2c2a', max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
            ], spacing=1, expand=True),
        ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        padding=10,
        bgcolor='white',
        border_radius=12,
        border=ft.border.all(1, '#e8e2da'),
        expand=True,
    )
