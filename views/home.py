import flet as ft
from api import get_lost_items, get_found_items, get_reviews, get_user
from storage import load_tokens

BROWN    = '#5c4f3a'
BROWN_LT = '#ede9e3'
GREEN    = '#3b5c38'
GREEN_LT = '#eef4ee'
GOLD     = '#c8920a'
GOLD_LT  = '#fef3d0'
BG       = '#f5f2ee'
WHITE    = '#ffffff'
DARK     = '#2c2c2a'
MUTED    = '#7a7670'
BORDER   = '#d6d1c8'


# Helpers
def _section_hdr(title, action_label=None, on_action=None):
    controls = [
        ft.Text(title, size=15, weight=ft.FontWeight.W_600, color=DARK),
        ft.Container(expand=True),
    ]
    if action_label and on_action:
        controls.append(
            ft.GestureDetector(
                on_tap=on_action,
                content=ft.Text(action_label, size=13, color=MUTED,
                                weight=ft.FontWeight.W_500),
            )
        )
    return ft.Row(controls=controls,
                  vertical_alignment=ft.CrossAxisAlignment.CENTER)


# Quick action tile
def _action_tile(icon, line1, line2, icon_color, bg_color, on_tap):
    return ft.GestureDetector(
        on_tap=on_tap,
        content=ft.Container(
            content=ft.Row([
                # Big icon left
                ft.Icon(icon, size=40, color=icon_color),
                ft.Container(width=12),
                # Label + arrow column
                ft.Column([
                    ft.Text(line1, size=13, weight=ft.FontWeight.W_600,
                            color=DARK),
                    ft.Text(line2, size=13, weight=ft.FontWeight.W_600,
                            color=DARK),
                    ft.Container(height=8),
                    ft.Text('→', size=18, color=icon_color,
                            weight=ft.FontWeight.W_500),
                ], spacing=1, expand=True),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(horizontal=14, vertical=16),
            bgcolor=bg_color,
            border_radius=16,
            border=ft.border.all(1, BORDER),
            shadow=ft.BoxShadow(blur_radius=6, color='#0e000000',
                                offset=ft.Offset(0, 2)),
            expand=True,
            height=100,
        ),
    )


# Recent item card 
def _recent_card(item, go):
    is_found  = item['type'] == 'found'
    item_id   = item.get('id')
    item_type = item['type']
    photo_url = item.get('photo_url')

    accent   = GREEN if is_found else BROWN
    badge_bg = GREEN_LT if is_found else BROWN_LT
    badge_fg = GREEN    if is_found else BROWN
    badge_t  = 'Found'  if is_found else 'Lost'

    if photo_url:
        img = ft.Image(src=photo_url, width=110, height=100,
                       fit=ft.BoxFit.COVER,
                       border_radius=ft.border_radius.only(top_left=12, top_right=12))
    else:
        img = ft.Container(
            content=ft.Icon(ft.Icons.IMAGE_OUTLINED, color='#b4b2a9', size=28),
            width=110, height=100, bgcolor='#e2ddd8',
            alignment=ft.Alignment(0, 0),
            border_radius=ft.border_radius.only(top_left=12, top_right=12),
        )

    return ft.GestureDetector(
        on_tap=lambda e: go(f'item_detail_{item_type}_{item_id}'),
        content=ft.Container(
            content=ft.Column([
                img,
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Text(badge_t, size=9, color=badge_fg,
                                            weight=ft.FontWeight.BOLD),
                            bgcolor=badge_bg,
                            padding=ft.padding.symmetric(horizontal=6, vertical=2),
                            border_radius=20,
                        ),
                        ft.Text(item.get('item_name', ''), size=11,
                                weight=ft.FontWeight.W_500, color=DARK,
                                max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ], spacing=4),
                    padding=ft.padding.symmetric(horizontal=8, vertical=7),
                ),
            ], spacing=0),
            width=110,
            bgcolor=WHITE,
            border_radius=12,
            border=ft.border.all(1, BORDER),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            shadow=ft.BoxShadow(blur_radius=4, color='#0c000000',
                                offset=ft.Offset(0, 2)),
        ),
    )


# Review card 
def _review_card(review):
    rating  = review.get('rating', 0)
    comment = review.get('comment', '')

    stars = ft.Row([
        ft.Icon(
            ft.Icons.STAR_ROUNDED if i <= rating else ft.Icons.STAR_BORDER_ROUNDED,
            color=GOLD if i <= rating else '#d6d1c8',
            size=16,
        )
        for i in range(1, 6)
    ], spacing=1)

    return ft.Container(
        content=ft.Column([
            stars,
            ft.Text(
                comment[:120] + ('…' if len(comment) > 120 else ''),
                size=12, color='#4a4a47',
            ),
        ], spacing=8),
        width=200,
        padding=ft.padding.symmetric(horizontal=14, vertical=14),
        bgcolor=GOLD_LT,
        border_radius=14,
        border=ft.border.all(1, '#e8d88a'),
        shadow=ft.BoxShadow(blur_radius=4, color='#0c000000', offset=ft.Offset(0, 2)),
    )


# Main view 
def home_view(page: ft.Page, go):
    page.title = 'UniFind — Home'
    access, _ = load_tokens()
    is_auth   = bool(access)

    username = None
    if is_auth:
        s, ud = get_user()
        if s == 200:
            username = ud.get('first_name') or ud.get('username') or None

    # Items
    _, lr = get_lost_items()
    lost_items  = lr if isinstance(lr, list) else lr.get('results', [])
    _, fr = get_found_items()
    found_items = fr if isinstance(fr, list) else fr.get('results', [])

    from itertools import chain
    recent = sorted(
        chain(
            [{'type': 'lost',  **i} for i in lost_items],
            [{'type': 'found', **i} for i in found_items],
        ),
        key=lambda x: x.get('submitted_at', ''),
        reverse=True,
    )[:10]

    # Reviews
    _, rv = get_reviews()
    reviews = (rv if isinstance(rv, list)
               else rv.get('results', []) if isinstance(rv, dict)
               else [])[:6]

    # Hero: avatar left + greeting right
    if username:
        greeting = ft.Text(spans=[
            ft.TextSpan('Welcome, ',
                        style=ft.TextStyle(size=20, weight=ft.FontWeight.BOLD,
                                           color=DARK)),
            ft.TextSpan(f'{username}!',
                        style=ft.TextStyle(size=20, weight=ft.FontWeight.BOLD,
                                           italic=True, color=DARK)),
        ])
    else:
        greeting = ft.Text('Welcome to UniFind!', size=20,
                           weight=ft.FontWeight.BOLD, color=DARK)

    # Avatar circle (initial or generic icon)
    avatar_letter = (username[0].upper() if username else None)
    if avatar_letter:
        avatar_inner = ft.Text(avatar_letter, size=22, weight=ft.FontWeight.BOLD,
                                color=BROWN)
    else:
        avatar_inner = ft.Icon(ft.Icons.PERSON_OUTLINE, size=28, color=BROWN)

    avatar = ft.Container(
        content=avatar_inner,
        width=56, height=56,
        bgcolor=BROWN_LT,
        border_radius=28,
        alignment=ft.Alignment(0, 0),
        border=ft.border.all(2, BORDER),
    )

    hero = ft.Container(
        content=ft.Row([
            avatar,
            ft.Container(width=14),
            ft.Column([
                greeting,
                ft.Text('Help the UoM community reunite their belongings',
                        size=12, color=MUTED),
            ], spacing=4, expand=True),
        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.padding.symmetric(horizontal=18, vertical=18),
        bgcolor=BROWN_LT,
        border_radius=18,
        border=ft.border.all(1, BORDER),
    )

    # Quick actions
    def _guard(route):
        """Require login for report actions."""
        return lambda e: go('login') if not is_auth else go(route)

    col_left = ft.Column([
        # Report Lost 
        _action_tile(ft.Icons.EDIT_LOCATION_ALT_ROUNDED,
                     'Report', 'Lost',
                     BROWN, BROWN_LT, _guard('report_lost')),
        # Browse Lost
        _action_tile(ft.Icons.SEARCH_ROUNDED,
                     'Browse', 'Lost',
                     BROWN, BROWN_LT, lambda e: go('browse_lost')),
    ], spacing=10, expand=True)

    col_right = ft.Column([
        # Report Found 
        _action_tile(ft.Icons.VOLUNTEER_ACTIVISM_ROUNDED,
                     'Report', 'Found',
                     GREEN, GREEN_LT, _guard('report_found')),
        # Browse Found 
        _action_tile(ft.Icons.INVENTORY_2_ROUNDED,
                     'Browse', 'Found',
                     GREEN, GREEN_LT, lambda e: go('browse_found')),
    ], spacing=10, expand=True)

    grid = ft.Row([col_left, col_right], spacing=10,
                  vertical_alignment=ft.CrossAxisAlignment.START)

    # Recent items row
    if recent:
        recent_row = ft.Row(
            [_recent_card(i, go) for i in recent],
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
        )
    else:
        recent_row = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.INBOX_OUTLINED, color='#c4bdb4', size=36),
                ft.Text('No items yet', color=MUTED, size=12),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
            padding=ft.padding.symmetric(vertical=24),
            alignment=ft.Alignment(0, 0),
        )

    # Reviews row
    if reviews:
        review_row = ft.Row(
            [_review_card(r) for r in reviews],
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
        )
    else:
        review_row = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.RATE_REVIEW_OUTLINED, color='#c4bdb4', size=20),
                ft.Text('No reviews yet', color=MUTED, size=12),
            ], spacing=8),
            padding=ft.padding.symmetric(vertical=16),
        )

    return ft.Column([
        hero,

        _section_hdr('Quick Actions'),
        grid,

        _section_hdr('Recent Items'),
        recent_row,

        _section_hdr('Reviews', 'See All', lambda e: go('reviews')),
        review_row,

        ft.Container(height=16),
    ], spacing=14, scroll=ft.ScrollMode.AUTO)