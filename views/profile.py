import flet as ft
from api import get_user, get_my_lost_items, get_my_found_items, get_my_claims
from storage import load_tokens, clear_tokens

BROWN      = '#5c4f3a'
LIGHT_BG   = '#f5f2ee'
CARD_BG    = 'white'
BORDER_CLR = '#d6d1c8'
DIVIDER    = '#f0ece6'
MUTED      = '#7a7670'
DARK       = '#2c2c2a'

STATUS_COLORS = {
    'pending':  ('#fff7e6', '#b45309'),
    'found':    ('#e6f4ea', '#2e7d32'),
    'claimed':  ('#e6f0fb', '#1565c0'),
    'resolved': ('#f3e6fb', '#6a1b9a'),
    'returned': ('#f3e6fb', '#6a1b9a'),
    'rejected': ('#fdecea', '#c62828'),
}


def profile_view(page: ft.Page, go):
    access, _ = load_tokens()
    if not access:
        go('login')
        return ft.Text('')

    status, user = get_user()
    if status != 200:
        clear_tokens()
        go('login')
        return ft.Container()

    _, lost_data  = get_my_lost_items()
    _, found_data = get_my_found_items()
    _, claim_data = get_my_claims()

    lost_items  = lost_data  if isinstance(lost_data,  list) else []
    found_items = found_data if isinstance(found_data, list) else []
    claims      = claim_data if isinstance(claim_data, list) else []

    # helpers 

    def do_logout(e):
        clear_tokens()
        go('login')

    def status_badge(s):
        bg, fg = STATUS_COLORS.get(s, ('#e8e2d9', BROWN))
        return ft.Container(
            content=ft.Text(s.capitalize(), size=11, weight=ft.FontWeight.BOLD, color=fg),
            bgcolor=bg,
            padding=ft.Padding.symmetric(horizontal=8, vertical=3),
            border_radius=20,
        )

    def type_badge(t):
        bg = '#fdecea' if t == 'lost' else '#e6f4ea'
        fg = '#c62828' if t == 'lost' else '#2e7d32'
        return ft.Container(
            content=ft.Text(t.capitalize(), size=11, weight=ft.FontWeight.BOLD, color=fg),
            bgcolor=bg,
            padding=ft.Padding.symmetric(horizontal=8, vertical=3),
            border_radius=20,
        )

    def field_row(label, value):
        return ft.Container(
            content=ft.Row([
                ft.Text(label, size=13, color=MUTED, width=120),
                ft.Text(value or '—', size=14, color=DARK, weight=ft.FontWeight.W_500),
            ]),
            padding=ft.Padding.symmetric(vertical=10),
            border=ft.Border.only(bottom=ft.BorderSide(1, DIVIDER)),
        )

    def section_header(icon, label):
        return ft.Row([
            ft.Icon(icon, color=BROWN, size=18),
            ft.Text(label, size=14, weight=ft.FontWeight.W_600, color=BROWN),
        ], spacing=8)

    def empty_state(msg):
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.FOLDER_OPEN_OUTLINED, color=MUTED, size=16),
                ft.Text(msg, size=13, color=MUTED, italic=True),
            ], spacing=8),
            padding=ft.Padding.symmetric(vertical=12),
        )

    def card(*children):
        return ft.Container(
            content=ft.Column(list(children), spacing=0),
            padding=24,
            bgcolor=CARD_BG,
            border_radius=12,
            border=ft.Border.all(1, BORDER_CLR),
        )

    # item row builders 

    def lost_row(item):
        return ft.Container(
            content=ft.Row([
                ft.TextButton(
                    item.get('item_name', '—'),
                    style=ft.ButtonStyle(color=BROWN),
                    on_click=lambda e, pk=item['id']: go(f"item_detail_lost_{pk}"),
                ),
                ft.Text(item.get('category', '').replace('_', ' ').title(),
                        size=12, color=MUTED, expand=True),
                ft.Text(item.get('date_lost', '—'), size=12, color=MUTED),
                status_badge(item.get('status', '')),
            ], spacing=8),
            padding=ft.Padding.symmetric(vertical=8),
            border=ft.Border.only(bottom=ft.BorderSide(1, DIVIDER)),
        )

    def found_row(item):
        return ft.Container(
            content=ft.Row([
                ft.TextButton(
                    item.get('item_name', '—'),
                    style=ft.ButtonStyle(color=BROWN),
                    on_click=lambda e, pk=item['id']: go(f"item_detail_found_{pk}"),
                ),
                ft.Text(item.get('category', '').replace('_', ' ').title(),
                        size=12, color=MUTED, expand=True),
                ft.Text(item.get('date_found', '—'), size=12, color=MUTED),
                status_badge(item.get('status', '')),
            ], spacing=8),
            padding=ft.Padding.symmetric(vertical=8),
            border=ft.Border.only(bottom=ft.BorderSide(1, DIVIDER)),
        )

    def claim_row(claim):
        item_name = claim.get('item_name', '—')
        item_type = claim.get('item_type', '')
        item_pk   = claim.get('lost_item') or claim.get('found_item')
        details   = claim.get('details', '')
        if len(details) > 60:
            details = details[:57] + '...'

        return ft.Container(
            content=ft.Row([
                ft.TextButton(
                    item_name,
                    style=ft.ButtonStyle(color=BROWN),
                    on_click=lambda e, t=item_type, pk=item_pk: go(f"item_detail_{t}_{pk}"),
                ),
                type_badge(item_type),
                ft.Text(details, size=12, color=MUTED, expand=True),
                ft.Text(claim.get('created_at', '')[:10], size=12, color=MUTED),
                status_badge(claim.get('status', '')),
            ], spacing=8),
            padding=ft.Padding.symmetric(vertical=8),
            border=ft.Border.only(bottom=ft.BorderSide(1, DIVIDER)),
        )

    # layout 

    return ft.Column([

        # Header
        card(
            ft.Row([
                ft.Container(
                    content=ft.Text(
                        user.get('username', '?')[0].upper(),
                        size=24, weight=ft.FontWeight.BOLD, color='white',
                    ),
                    width=56, height=56,
                    bgcolor=BROWN,
                    border_radius=28,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Text(user.get('username', ''), size=18,
                            weight=ft.FontWeight.BOLD, color=DARK),
                    ft.Container(
                        content=ft.Text(user.get('role', '').capitalize(),
                                        size=11, weight=ft.FontWeight.BOLD, color=BROWN),
                        bgcolor='#e8e2d9',
                        padding=ft.Padding.symmetric(horizontal=10, vertical=3),
                        border_radius=20,
                    ),
                ], spacing=6),
            ], spacing=16),
        ),

        # Account info
        card(
            section_header(ft.Icons.INFO_OUTLINE, 'Account Information'),
            ft.Divider(height=12, color='transparent'),
            field_row('Username',   user.get('username')),
            field_row('Email',      user.get('email')),
            field_row('First Name', user.get('first_name')),
            field_row('Last Name',  user.get('last_name')),
            field_row('Role',       user.get('role', '').capitalize()),
            field_row('Phone',      user.get('phone')),
            field_row('Student ID', user.get('student_id')),
        ),

        # Lost reports
        card(
            section_header(ft.Icons.SEARCH, 'My Lost Item Reports'),
            ft.Divider(height=12, color='transparent'),
            *(
                [lost_row(i) for i in lost_items]
                if lost_items else
                [empty_state("You haven't reported any lost items yet.")]
            ),
        ),

        # Found reports
        card(
            section_header(ft.Icons.INVENTORY_2_OUTLINED, 'My Found Item Reports'),
            ft.Divider(height=12, color='transparent'),
            *(
                [found_row(i) for i in found_items]
                if found_items else
                [empty_state("You haven't reported any found items yet.")]
            ),
        ),

        # Claims
        card(
            section_header(ft.Icons.TASK_ALT_OUTLINED, 'My Claims'),
            ft.Divider(height=12, color='transparent'),
            *(
                [claim_row(c) for c in claims]
                if claims else
                [empty_state("You haven't submitted any claims yet.")]
            ),
        ),

        # Actions
        ft.Row([
            ft.ElevatedButton(
                'Log Out',
                icon=ft.Icons.LOGOUT,
                bgcolor='#e8e2d9',
                color=BROWN,
                on_click=do_logout,
            ),
        ]),

    ], spacing=16, scroll=ft.ScrollMode.AUTO)