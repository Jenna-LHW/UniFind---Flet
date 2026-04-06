import flet as ft
from api import get_lost_items, get_found_items
from storage import load_tokens

BASE_URL = 'http://127.0.0.1:8000'

def home_view(page: ft.Page, go):
    page.title = 'UniFind — Home'
    access, _ = load_tokens()
    is_auth   = bool(access)

    status_l, lost_data  = get_lost_items()
    status_f, found_data = get_found_items()

    lost_items  = lost_data  if isinstance(lost_data,  list) else lost_data.get('results',  [])
    found_items = found_data if isinstance(found_data, list) else found_data.get('results', [])

    from itertools import chain
    all_items = sorted(
        chain(
            [{'type': 'lost',  **i} for i in lost_items],
            [{'type': 'found', **i} for i in found_items],
        ),
        key=lambda x: x.get('submitted_at', ''),
        reverse=True
    )[:6]

    total_users = len(lost_items) + len(found_items)

    def item_card(item):
        is_found    = item['type'] == 'found'
        badge_color = '#3b5c38' if is_found else '#5c3a38'
        badge_text  = 'FOUND'   if is_found else 'LOST'
        location    = item.get('found_at') or item.get('last_seen', '')
        date        = item.get('date_found') or item.get('date_lost', '')
        photo_url = item.get('photo_url')

        if photo_url:
            full_url = photo_url if photo_url.startswith('http') else BASE_URL + photo_url
            photo = ft.Image(
                src=full_url,
                width=220,
                height=140,
                fit="cover",
                border_radius=ft.border_radius.only(top_left=10, top_right=10),
            )
        else:
            photo = ft.Container(
                content=ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED, color='#b4b2a9', size=32),
                width=220,
                height=140,
                bgcolor='#f5f2ee',
                alignment=ft.Alignment(0, 0),
                border_radius=ft.border_radius.only(top_left=10, top_right=10),
            )

        return ft.Container(
            content=ft.Column([
                photo,
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Text(badge_text, color='white', size=10,
                                            weight=ft.FontWeight.BOLD),
                            bgcolor=badge_color,
                            padding=ft.padding.symmetric(horizontal=8, vertical=3),
                            border_radius=20,
                        ),
                        ft.Text(item.get('item_name', ''), size=14,
                                weight=ft.FontWeight.W_600, color='#2c2c2a',
                                max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(f"📍 {location[:28]}", size=11, color='#7a7670'),
                        ft.Text(str(date), size=11, color='#7a7670'),
                        ft.ElevatedButton(
                            'View Details',
                            bgcolor='#5c4f3a',
                            color='white',
                            height=34,
                            on_click=lambda e: go('browse_found' if is_found else 'browse_lost'),
                        ),
                    ], spacing=5),
                    padding=12,
                ),
            ], spacing=0),
            bgcolor='white',
            border_radius=10,
            border=ft.border.all(1, '#d6d1c8'),
            width=220,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

    recent_row = ft.Row(
        [item_card(i) for i in all_items] if all_items else [
            ft.Text('No items yet.', color='#7a7670')
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=16,
    )

    return ft.Column([

        # ── Hero ──
        ft.Container(
            content=ft.Column([
                ft.Text(
                    'Lost Something?\nFound Something?',
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color='#2c2c2a',
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    'Report it now and let the UoM community help you!',
                    size=14,
                    color='#5c5e5a',
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Row([
                    ft.OutlinedButton(
                        'Report Lost Item',
                        on_click=lambda e: go('login') if not is_auth else go('report_lost'),
                        style=ft.ButtonStyle(
                            side=ft.BorderSide(2, '#5c4f3a'),
                            color='#5c4f3a',
                        ),
                    ),
                    ft.OutlinedButton(
                        'Report Found Item',
                        on_click=lambda e: go('login') if not is_auth else go('report_found'),
                        style=ft.ButtonStyle(
                            side=ft.BorderSide(2, '#5c4f3a'),
                            color='#5c4f3a',
                        ),
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16),
            padding=40,
            bgcolor='#ede9e3',
            border_radius=16,
            margin=ft.margin.only(bottom=8),
            alignment=ft.Alignment(0, 0),
        ),

        # ── How it works ──
        ft.Container(
            content=ft.Column([
                ft.Text('How It Works', size=20,
                        weight=ft.FontWeight.BOLD, color='#2c2c2a',
                        text_align=ft.TextAlign.CENTER),
                ft.Row([
                    _how_card('🚩', 'Report Items',
                              'Report lost or found items with photos in under 3 minutes.'),
                    _how_card('🔍', 'Search & Browse',
                              'Browse all reported items with filters by category and date.'),
                    _how_card('🤝', 'Connect & Reclaim',
                              'Get in touch and safely recover your belongings.'),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=16, wrap=True),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16),
            padding=ft.padding.symmetric(vertical=24, horizontal=0),
        ),

        # ── Stats ──
        ft.Container(
            content=ft.Row([
                _stat('100+', 'Items Reunited'),
                ft.VerticalDivider(width=1, color='#d6cfc4'),
                _stat(f'{len(lost_items) + len(found_items)}+', 'Items Reported'),
                ft.VerticalDivider(width=1, color='#d6cfc4'),
                _stat('500+', 'Active Users'),
            ],
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=28,
            bgcolor='#ede9e3',
            border_radius=12,
            margin=ft.margin.only(bottom=8),
        ),

        # ── Recent items ──
        ft.Text('Recent Items', size=20,
                weight=ft.FontWeight.BOLD, color='#2c2c2a'),
        recent_row,
        ft.Divider(height=8, color='transparent'),
        ft.Row([
            ft.ElevatedButton(
                'Browse Lost Items',
                bgcolor='#5c4f3a',
                color='white',
                icon=ft.Icons.SEARCH,
                on_click=lambda e: go('browse_lost'),
            ),
            ft.ElevatedButton(
                'Browse Found Items',
                bgcolor='#3b5c38',
                color='white',
                icon=ft.Icons.INVENTORY_2,
                on_click=lambda e: go('browse_found'),
            ),
        ], alignment=ft.MainAxisAlignment.CENTER),

    ], spacing=16, scroll=ft.ScrollMode.AUTO)


def _how_card(icon, title, desc):
    return ft.Container(
        content=ft.Column([
            ft.Text(icon, size=30, text_align=ft.TextAlign.CENTER),
            ft.Text(title, size=14, weight=ft.FontWeight.W_600,
                    color='#2c2c2a', text_align=ft.TextAlign.CENTER),
            ft.Text(desc, size=12, color='#7a7670',
                    text_align=ft.TextAlign.CENTER),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=8),
        padding=20,
        bgcolor='white',
        border_radius=12,
        border=ft.border.all(1, '#d6d1c8'),
        width=200,
        alignment=ft.Alignment(0, 0),
    )


def _stat(number, label):
    return ft.Column([
        ft.Text(number, size=26, weight=ft.FontWeight.BOLD,
                color='#2c2c2a', text_align=ft.TextAlign.CENTER),
        ft.Text(label, size=12, color='#7a7670',
                text_align=ft.TextAlign.CENTER),
    ],
    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    spacing=4)