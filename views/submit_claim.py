import flet as ft
from api import get_lost_item, get_found_item, submit_claim

BROWN      = '#5c4f3a'
GREEN      = '#3b5c38'
BORDER     = '#d6d1c8'
TEXT_MAIN  = '#2c2c2a'
TEXT_MUTED = '#7a7670'

def submit_claim_view(page: ft.Page, go, item_type: str, item_id: int):
    """
    item_type: 'lost' or 'found'
    item_id:   pk of the item
    """
    accent = GREEN if item_type == 'found' else BROWN

    details_field = ft.TextField(
        label='Supporting Details',
        hint_text=(
            'Provide details to verify ownership '
            '(e.g. specific marks, contents, or precise time/location).'
        ),
        multiline=True,
        min_lines=5,
        max_lines=8,
        border_color=BORDER,
        focused_border_color=accent,
        expand=True,
    )

    loading    = ft.ProgressRing(visible=False, width=20, height=20)
    status_text = ft.Text('', size=13)
    item_name_text  = ft.Text('Loading...', size=15, weight=ft.FontWeight.W_600, color=TEXT_MAIN)
    item_loc_text   = ft.Text('', size=13, color=TEXT_MUTED)

    # Load the item summary
    def load_item():
        if item_type == 'lost':
            code, data = get_lost_item(item_id)
        else:
            code, data = get_found_item(item_id)

        if code == 200:
            item_name_text.value = data.get('item_name', '')
            loc = data.get('last_seen') or data.get('found_at') or ''
            item_loc_text.value  = f'📍 {loc}' if loc else ''
        else:
            item_name_text.value = 'Unknown item'

    load_item()

    def on_submit(e):
        details = details_field.value.strip()
        if not details:
            status_text.value = 'Please provide supporting details.'
            status_text.color = ft.Colors.RED_600
            page.update()
            return

        loading.visible     = True
        status_text.value   = ''
        page.update()

        code, data = submit_claim(item_type, item_id, details)
        loading.visible = False

        if code == 201:
            status_text.value = '✓ Claim submitted! Awaiting admin review.'
            status_text.color = ft.Colors.GREEN_700
            details_field.value   = ''
            details_field.disabled = True
            page.update()
            # Navigate back after a short delay
            import time
            time.sleep(1.5)
            go(f'browse_{item_type}')
        else:
            # Show the first error message from the API
            err = data
            if isinstance(err, dict):
                msg = next(iter(err.values()), 'Submission failed.')
                if isinstance(msg, list):
                    msg = msg[0]
            else:
                msg = 'Submission failed. Please try again.'
            status_text.value = str(msg)
            status_text.color = ft.Colors.RED_600
            page.update()

    return ft.Column([

        # Header card
        ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.HANDSHAKE if item_type == 'found' else ft.Icons.SEARCH,
                        color='white', size=22,
                    ),
                    width=44, height=44,
                    bgcolor=accent,
                    border_radius=10,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Text('Request & Recovery', size=17,
                            weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Text(
                        'Claim a found item' if item_type == 'found' else 'Report you found it',
                        size=12, color=TEXT_MUTED,
                    ),
                ], spacing=2),
            ], spacing=14),
            padding=20,
            bgcolor='white',
            border_radius=12,
            border=ft.border.all(1, BORDER),
        ),

        # Item summary box
        ft.Container(
            content=ft.Column([
                ft.Text('ITEM', size=10, color=TEXT_MUTED,
                        style=ft.TextStyle(letter_spacing=0.6)),
                item_name_text,
                ft.Container(height=2),
                ft.Text('LOCATION', size=10, color=TEXT_MUTED,
                        style=ft.TextStyle(letter_spacing=0.6)),
                item_loc_text,
            ], spacing=4),
            padding=16,
            bgcolor='#fcfaf7',
            border_radius=10,
            border=ft.border.all(1, '#cdc8bf'),
        ),

        # Details form
        ft.Container(
            content=ft.Column([
                details_field,
                ft.Container(height=4),
                ft.Row([
                    ft.TextButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CHEVRON_LEFT, size=16, color=TEXT_MUTED),
                            ft.Text('Back', size=13, color=TEXT_MUTED),
                        ], spacing=2),
                        on_click=lambda e: go(f'browse_{item_type}'),
                    ),
                    ft.Container(expand=True),
                    loading,
                    ft.ElevatedButton(
                        'Submit Claim',
                        bgcolor=accent,
                        color='white',
                        icon=ft.Icons.SEND,
                        on_click=on_submit,
                    ),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                status_text,
            ], spacing=12),
            padding=20,
            bgcolor='white',
            border_radius=12,
            border=ft.border.all(1, BORDER),
        ),

        # Footer hint
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.LOCK_OUTLINE, size=14, color=TEXT_MUTED),
                ft.Text('Privacy maintained · Verified by admin',
                        size=11, color=TEXT_MUTED),
            ], spacing=6),
            alignment=ft.Alignment(0, 0),
        ),

    ], spacing=16, scroll=ft.ScrollMode.AUTO)