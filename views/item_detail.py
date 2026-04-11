import flet as ft
from api import get_lost_item, get_found_item
from storage import load_tokens

BROWN      = '#5c4f3a'
GREEN      = '#3b5c38'
LIGHT      = '#f5f2ee'
BORDER     = '#d6d1c8'
TEXT_MAIN  = '#2c2c2a'
TEXT_MUTED = '#7a7670'

def item_detail_view(page: ft.Page, go, item_type: str, item_id: int):
    """
    item_type: 'lost' or 'found'
    item_id:   pk of the item
    """
    accent     = GREEN if item_type == 'found' else BROWN
    loading    = ft.ProgressRing(visible=True)
    error_text = ft.Text('', color=ft.Colors.RED_600)
    body       = ft.Column(spacing=0)

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
            page.update()
            return

        _render(data)
        page.update()

    def _render(item):
        photo_url  = item.get('photo_url')
        name       = item.get('item_name', '')
        category   = item.get('category', '').replace('_', ' ').title()
        description= item.get('description', '')
        status_val = item.get('status', '')
        reported_by= item.get('reported_by', '')
        submitted  = item.get('submitted_at', '')[:10]

        if item_type == 'lost':
            location_label = 'Last seen at'
            location_value = item.get('last_seen', '')
            date_label     = 'Date lost'
            date_value     = item.get('date_lost', '')
            subtitle       = 'Lost item report'
            claim_title    = 'Did you find this item?'
            claim_body     = 'If you found this item, submit a report so the owner can be notified.'
            claim_btn_text = 'I found this item'
        else:
            location_label = 'Found at'
            location_value = item.get('found_at', '')
            date_label     = 'Date found'
            date_value     = item.get('date_found', '')
            subtitle       = 'Found item report'
            claim_title    = 'Is this your item?'
            claim_body     = 'If you believe this belongs to you, submit a claim with proof of ownership.'
            claim_btn_text = 'Claim this item'

        # Photo
        if photo_url:
            photo_widget = ft.Image(
                src=photo_url,
                width=double_width(),
                height=200,
                fit='cover',
                border_radius=ft.border_radius.only(top_left=12, top_right=12),
            )
        else:
            photo_widget = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED, color='#b4b2a9', size=40),
                    ft.Text('No photo provided', size=12, color=TEXT_MUTED),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
                height=160,
                bgcolor='#f5f2ee',
                border_radius=ft.border_radius.only(top_left=12, top_right=12),
                alignment=ft.Alignment(0, 0),
            )

        # Status badge colour
        status_colors = {
            'pending':  ('#faeeda', '#854f0b'),
            'found':    ('#eaf3de', '#27500a'),
            'claimed':  ('#e6f1fb', '#0c447c'),
            'resolved': ('#eaf3de', '#27500a'),
        }
        badge_bg, badge_fg = status_colors.get(status_val, ('#f5f2ee', TEXT_MUTED))

        # Claim / resolved box
        if status_val == 'resolved':
            action_box = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color='#27500a', size=20),
                    ft.Text('This item has been reunited with its owner.',
                            size=13, color='#27500a', weight=ft.FontWeight.W_500),
                ], spacing=10),
                padding=14,
                bgcolor='#eaf3de',
                border_radius=10,
                border=ft.border.all(1, '#c4dca8'),
            )
        elif not is_auth:
            action_box = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.LOCK_OUTLINE, color=TEXT_MUTED, size=18),
                    ft.Text('Log in to submit a claim.', size=13, color=TEXT_MUTED),
                    ft.Container(expand=True),
                    ft.TextButton('Log in', on_click=lambda e: go('login')),
                ], spacing=10),
                padding=14,
                bgcolor='#f9f7f4',
                border_radius=10,
                border=ft.border.all(1, BORDER),
            )
        else:
            action_box = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.HANDSHAKE if item_type == 'found' else ft.Icons.SEARCH,
                            color='white', size=20,
                        ),
                        width=40, height=40,
                        bgcolor=accent,
                        border_radius=8,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column([
                        ft.Text(claim_title, size=13, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                        ft.Text(claim_body,  size=11, color=TEXT_MUTED),
                    ], spacing=2, expand=True),
                    ft.ElevatedButton(
                        claim_btn_text,
                        bgcolor=accent,
                        color='white',
                        on_click=lambda e: go(f'submit_claim_{item_type}_{item_id}'),
                    ),
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=14,
                bgcolor='#f9f7f4',
                border_radius=10,
                border=ft.border.all(1, BORDER),
            )

        body.controls = [
            # Photo
            photo_widget,

            # Main info card
            ft.Container(
                content=ft.Column([

                    # Title + subtitle
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Column([
                                    ft.Text(name, size=20, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                                    ft.Text(subtitle, size=11, color=TEXT_MUTED,
                                            style=ft.TextStyle(letter_spacing=0.5)),
                                ], spacing=2, expand=True),
                                ft.Container(
                                    content=ft.Text(status_val.capitalize(),
                                                    size=11, weight=ft.FontWeight.BOLD,
                                                    color=badge_fg),
                                    bgcolor=badge_bg,
                                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                    border_radius=20,
                                ),
                            ]),
                        ], spacing=4),
                        padding=ft.padding.only(bottom=16),
                        border=ft.border.only(bottom=ft.BorderSide(1, '#f0ece6')),
                    ),

                    # Description
                    ft.Text('Description', size=12, weight=ft.FontWeight.BOLD,
                            color=accent, style=ft.TextStyle(letter_spacing=0.5)),
                    ft.Text(description, size=13, color='#3c3c3a',
                            selectable=True),

                    # Meta grid
                    ft.Container(height=4),
                    ft.Row([
                        _meta_tile(ft.Icons.LOCATION_ON, location_label, location_value or '—'),
                        _meta_tile(ft.Icons.CALENDAR_TODAY, date_label, date_value or '—'),
                    ], spacing=10),
                    ft.Row([
                        _meta_tile(ft.Icons.LABEL, 'Category', category or '—'),
                        _meta_tile(ft.Icons.PERSON, 'Reported by', str(reported_by) if reported_by else '—'),
                    ], spacing=10),

                    # Submitted date
                    ft.Text(f'Submitted on {submitted}', size=11, color=TEXT_MUTED),

                    # Claim / resolved box
                    action_box,

                    # Back button
                    ft.TextButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ARROW_BACK, size=16, color=accent),
                            ft.Text(f'Back to Browse {"Lost" if item_type == "lost" else "Found"}',
                                    size=13, color=accent),
                        ], spacing=4),
                        on_click=lambda e: go(f'browse_{item_type}'),
                    ),

                ], spacing=12),
                padding=16,
                bgcolor='white',
                border_radius=ft.border_radius.only(bottom_left=12, bottom_right=12),
                border=ft.border.all(1, BORDER),
            ),
        ]

    load()

    return ft.Column([
        error_text,
        loading,
        body,
    ], spacing=0, scroll=ft.ScrollMode.AUTO)


def double_width():
    return None  # let it fill the container width


def _meta_tile(icon, label, value):
    return ft.Container(
        content=ft.Row([
            ft.Container(
                content=ft.Icon(icon, size=16, color='#5c4f3a'),
                width=32, height=32,
                bgcolor='#ede8e0',
                border_radius=6,
                alignment=ft.Alignment(0, 0),
            ),
            ft.Column([
                ft.Text(label, size=10, color=TEXT_MUTED,
                        style=ft.TextStyle(letter_spacing=0.4)),
                ft.Text(value, size=12, weight=ft.FontWeight.W_600,
                        color='#2c2c2a', max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS),
            ], spacing=1, expand=True),
        ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        padding=10,
        bgcolor='#f9f7f4',
        border_radius=10,
        border=ft.border.all(1, '#ebe7e0'),
        expand=True,
    )