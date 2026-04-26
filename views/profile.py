import flet as ft
from api import get_user, get_my_lost_items, get_my_found_items, get_my_claims
from storage import load_tokens, clear_tokens

BROWN = '#5c4f3a'
GREEN = '#3b5c38'
MUTED = '#7a7670'
DARK  = '#2c2c2a'
DIVIDER = '#f0ece6'

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
        go('login'); return ft.Text('')

    status, user = get_user()
    if status != 200:
        clear_tokens(); go('login'); return ft.Container()

    _, lost_data  = get_my_lost_items()
    _, found_data = get_my_found_items()
    _, claim_data = get_my_claims()

    lost_items  = lost_data  if isinstance(lost_data,  list) else []
    found_items = found_data if isinstance(found_data, list) else []
    claims      = claim_data if isinstance(claim_data, list) else []

    def do_logout(e):
        clear_tokens(); go('login')

    def status_badge(s):
        bg, fg = STATUS_COLORS.get(s, ('#e8e2d9', BROWN))
        return ft.Container(
            content=ft.Text(s.capitalize(), size=10, weight=ft.FontWeight.BOLD, color=fg),
            bgcolor=bg, padding=ft.padding.symmetric(horizontal=8, vertical=3), border_radius=20,
        )

    def type_badge(t):
        bg = '#fdecea' if t == 'lost' else '#e6f4ea'
        fg = '#c62828' if t == 'lost' else '#2e7d32'
        return ft.Container(
            content=ft.Text(t.capitalize(), size=10, weight=ft.FontWeight.BOLD, color=fg),
            bgcolor=bg, padding=ft.padding.symmetric(horizontal=8, vertical=3), border_radius=20,
        )

    def info_row(label, value):
        return ft.Container(
            content=ft.Row([
                ft.Text(label, size=12, color=MUTED, width=110),
                ft.Text(value or '—', size=13, color=DARK, weight=ft.FontWeight.W_500, expand=True),
            ], spacing=8),
            padding=ft.padding.symmetric(vertical=11),
            border=ft.Border.only(bottom=ft.BorderSide(1, DIVIDER)),
        )

    def card_header(icon, label, count=None):
        return ft.Row([
            ft.Container(
                content=ft.Icon(icon, color='white', size=16),
                width=32, height=32, bgcolor=BROWN, border_radius=8,
                alignment=ft.Alignment(0, 0),
            ),
            ft.Text(label, size=14, weight=ft.FontWeight.W_600, color=DARK, expand=True),
            ft.Container(
                content=ft.Text(str(count), size=11, weight=ft.FontWeight.BOLD, color=BROWN),
                bgcolor='#ede8e0',
                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                border_radius=12,
                visible=count is not None,
            ),
        ], spacing=10)

    def empty_msg(msg):
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.FOLDER_OPEN_OUTLINED, color=MUTED, size=16),
                ft.Text(msg, size=12, color=MUTED, italic=True),
            ], spacing=8),
            padding=ft.padding.symmetric(vertical=12),
        )

    def card(*children, inner_pad=20):
        return ft.Container(
            content=ft.Column(list(children), spacing=0),
            padding=inner_pad,
            bgcolor='white',
            border_radius=16,
            border=ft.Border.all(1, '#e8e2da'),
            shadow=ft.BoxShadow(blur_radius=4, color='#08000000'),
        )

    def lost_row(item):
        return ft.GestureDetector(
            on_tap=lambda e, pk=item['id']: go(f"item_detail_lost_{pk}"),
            content=ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text(item.get('item_name', '—'), size=13,
                                weight=ft.FontWeight.W_500, color=DARK),
                        ft.Row([
                            ft.Text(item.get('category', '').replace('_',' ').title(),
                                    size=11, color=MUTED),
                            ft.Text('•', size=11, color='#c4bdb4'),
                            ft.Text(item.get('date_lost', '—'), size=11, color=MUTED),
                        ], spacing=4),
                    ], spacing=2, expand=True),
                    status_badge(item.get('status', '')),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT_ROUNDED, color='#c4bdb4', size=16),
                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.symmetric(vertical=12),
                border=ft.Border.only(bottom=ft.BorderSide(1, DIVIDER)),
            ),
        )

    def found_row(item):
        return ft.GestureDetector(
            on_tap=lambda e, pk=item['id']: go(f"item_detail_found_{pk}"),
            content=ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text(item.get('item_name', '—'), size=13,
                                weight=ft.FontWeight.W_500, color=DARK),
                        ft.Row([
                            ft.Text(item.get('category', '').replace('_',' ').title(),
                                    size=11, color=MUTED),
                            ft.Text('•', size=11, color='#c4bdb4'),
                            ft.Text(item.get('date_found', '—'), size=11, color=MUTED),
                        ], spacing=4),
                    ], spacing=2, expand=True),
                    status_badge(item.get('status', '')),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT_ROUNDED, color='#c4bdb4', size=16),
                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.symmetric(vertical=12),
                border=ft.Border.only(bottom=ft.BorderSide(1, DIVIDER)),
            ),
        )

    def claim_row(claim):
        item_name = claim.get('item_name', '—')
        item_type = claim.get('item_type', '')
        item_pk   = claim.get('lost_item') or claim.get('found_item')
        return ft.GestureDetector(
            on_tap=lambda e, t=item_type, pk=item_pk: go(f"item_detail_{t}_{pk}"),
            content=ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text(item_name, size=13, weight=ft.FontWeight.W_500, color=DARK),
                        ft.Row([
                            type_badge(item_type),
                            ft.Text(claim.get('created_at', '')[:10], size=11, color=MUTED),
                        ], spacing=6),
                    ], spacing=4, expand=True),
                    status_badge(claim.get('status', '')),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT_ROUNDED, color='#c4bdb4', size=16),
                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.symmetric(vertical=12),
                border=ft.Border.only(bottom=ft.BorderSide(1, DIVIDER)),
            ),
        )

    username_init = user.get('username', '?')[0].upper()

    return ft.Column([

        # Avatar + name
        ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text(username_init, size=28, weight=ft.FontWeight.BOLD,
                                    color='white'),
                    width=72, height=72, bgcolor=BROWN, border_radius=36,
                    alignment=ft.Alignment(0, 0),
                    shadow=ft.BoxShadow(blur_radius=12, color='#295c4f3a', offset=ft.Offset(0, 4)),
                ),
                ft.Text(user.get('username', ''), size=18, weight=ft.FontWeight.BOLD, color=DARK),
                ft.Container(
                    content=ft.Text(user.get('role', '').capitalize(), size=11,
                                    weight=ft.FontWeight.BOLD, color=BROWN),
                    bgcolor='#ede8e0',
                    padding=ft.padding.symmetric(horizontal=12, vertical=4),
                    border_radius=20,
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
            padding=ft.padding.symmetric(vertical=20),
            alignment=ft.Alignment(0, 0),
        ),

        # Stats strip
        ft.Container(
            content=ft.Row([
                _stat_col(str(len(lost_items)), 'Lost'),
                ft.VerticalDivider(width=1, color='#e8e2da'),
                _stat_col(str(len(found_items)), 'Found'),
                ft.VerticalDivider(width=1, color='#e8e2da'),
                _stat_col(str(len(claims)), 'Claims'),
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            bgcolor='white',
            border_radius=16,
            border=ft.Border.all(1, '#e8e2da'),
            padding=ft.padding.symmetric(vertical=16),
        ),

        # Account info
        card(
            card_header(ft.Icons.PERSON_OUTLINE_ROUNDED, 'Account Information'),
            ft.Container(height=12),
            info_row('Username',   user.get('username')),
            info_row('Email',      user.get('email')),
            info_row('First Name', user.get('first_name')),
            info_row('Last Name',  user.get('last_name')),
            info_row('Phone',      user.get('phone')),
            info_row('Student ID', user.get('student_id')),
        ),

        # Lost reports
        card(
            card_header(ft.Icons.SEARCH_ROUNDED, 'My Lost Reports', len(lost_items)),
            ft.Container(height=8),
            *(([lost_row(i) for i in lost_items]) if lost_items
              else [empty_msg("No lost item reports yet.")]),
        ),

        # Found reports
        card(
            card_header(ft.Icons.INVENTORY_2_OUTLINED, 'My Found Reports', len(found_items)),
            ft.Container(height=8),
            *(([found_row(i) for i in found_items]) if found_items
              else [empty_msg("No found item reports yet.")]),
        ),

        # Claims
        card(
            card_header(ft.Icons.TASK_ALT_OUTLINED, 'My Claims', len(claims)),
            ft.Container(height=8),
            *(([claim_row(c) for c in claims]) if claims
              else [empty_msg("No claims submitted yet.")]),
        ),

        # Actions
        ft.Row([
            ft.ElevatedButton(
                'Edit Profile',
                icon=ft.Icons.EDIT_OUTLINED,
                bgcolor=BROWN, color='white',
                height=48, expand=True,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=14)),
                on_click=lambda e: go('edit_profile'),
            ),
            ft.OutlinedButton(
                'Log Out',
                icon=ft.Icons.LOGOUT_ROUNDED,
                height=48, expand=True,
                style=ft.ButtonStyle(
                    color=BROWN,
                    side=ft.BorderSide(1.5, BROWN),
                    shape=ft.RoundedRectangleBorder(radius=14),
                ),
                on_click=do_logout,
            ),
        ], spacing=12),

        ft.Container(height=8),

    ], spacing=14, scroll=ft.ScrollMode.AUTO)


def _stat_col(value, label):
    return ft.Column([
        ft.Text(value, size=20, weight=ft.FontWeight.BOLD, color='#5c4f3a',
                text_align=ft.TextAlign.CENTER),
        ft.Text(label, size=11, color='#9a8f80', text_align=ft.TextAlign.CENTER),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2, expand=True)
