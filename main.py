import flet as ft
import threading, time
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from views.login         import login_view
from views.register      import register_view
from views.home          import home_view
from views.browse_lost   import browse_lost_view
from views.browse_found  import browse_found_view
from views.report_lost   import report_lost_view
from views.report_found  import report_found_view
from views.profile       import profile_view
from views.edit_profile  import edit_profile_view
from views.reviews       import reviews_view
from views.contact       import contact_view
from views.about         import about_view
from views.item_detail   import item_detail_view
from views.submit_claim  import submit_claim_view
from storage            import load_tokens
from api import get_notifications, mark_notification_read, mark_all_notifications_read

ROUTES = {
    'login':        login_view,
    'register':     register_view,
    'home':         home_view,
    'browse_lost':  browse_lost_view,
    'browse_found': browse_found_view,
    'report_lost':  report_lost_view,
    'report_found': report_found_view,
    'profile':      profile_view,
    'edit_profile': edit_profile_view,
    'reviews':      reviews_view,
    'contact':      contact_view,
    'about':        about_view,
}

BROWN  = '#5c4f3a'
LIGHT  = '#f5f2ee'
NAV_BG = '#ede9e3'


def main(page: ft.Page):
    page.title        = 'UniFind'
    page.bgcolor      = LIGHT
    page.padding      = 0
    page.theme_mode   = ft.ThemeMode.LIGHT
    page.window_width  = 390
    page.window_height = 844

    current_route = {'name': None}
    notif_list    = []
    panel_open    = {'v': False}

    badge = ft.Container(
        content=ft.Text('0', size=8, color='white', weight=ft.FontWeight.BOLD),
        bgcolor='red',
        border_radius=8,
        padding=ft.Padding.symmetric(horizontal=3, vertical=1),
        visible=False,
        width=16,
        height=16,
    )

    def build_notif_panel():
        unread = [n for n in notif_list if not n['is_read']]
        rows   = []

        if not notif_list:
            rows.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.NOTIFICATIONS_OFF_OUTLINED, color='#c4bdb4', size=36),
                        ft.Text('No notifications yet', color='#9a8f80', size=13, italic=True),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=ft.padding.symmetric(vertical=24),
                    alignment=ft.Alignment(0, 0),
                )
            )
        else:
            for n in notif_list[:20]:
                is_read   = n['is_read']
                is_match  = n.get('notification_type') == 'match'
                if is_match and not is_read:
                    row_bg = '#fff8e7'; dot_color = '#e67e22'; border_color = '#f5d98a'
                elif not is_read:
                    row_bg = '#fdfaf6'; dot_color = 'red'; border_color = '#f0ece6'
                else:
                    row_bg = 'white'; dot_color = 'transparent'; border_color = '#f0ece6'

                leading_icon = ft.Icon(ft.Icons.COMPARE_ARROWS_ROUNDED, size=14, color='#e67e22') \
                    if is_match else ft.Container(width=6, height=6, border_radius=3, bgcolor=dot_color)

                rows.append(
                    ft.Container(
                        content=ft.Row([
                            leading_icon,
                            ft.Column([
                                ft.Text(n['title'], size=13,
                                        weight=ft.FontWeight.BOLD if not is_read else ft.FontWeight.NORMAL,
                                        color='#2c2c2a'),
                                ft.Text(n['body'][:80] + ('...' if len(n['body']) > 80 else ''),
                                        size=11, color='#7a7670'),
                            ], spacing=2, expand=True),
                        ], spacing=8),
                        padding=10,
                        bgcolor=row_bg,
                        border=ft.Border.only(bottom=ft.BorderSide(1, border_color)),
                        on_click=lambda e, n=n: on_notif_tap(n),
                    )
                )

        actions = []
        if unread:
            actions.append(ft.Container(
                content=ft.TextButton('Mark all read', on_click=on_mark_all,
                                      style=ft.ButtonStyle(color=BROWN)),
                alignment=ft.Alignment(1, 0),
                padding=ft.padding.only(right=8),
            ))

        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Text('Notifications', size=15, weight=ft.FontWeight.BOLD, color=BROWN),
                        ft.IconButton(ft.Icons.CLOSE, icon_size=18, icon_color='#9a8f80',
                                      on_click=lambda e: close_panel()),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.only(left=16, right=8, top=12, bottom=0),
                ),
                ft.Divider(height=1, color='#e8e2da'),
                ft.Column(rows, spacing=0, scroll=ft.ScrollMode.AUTO, height=260),
                *actions,
            ], spacing=0),
            width=320,
            bgcolor='white',
            border_radius=16,
            border=ft.Border.all(1, '#d6d1c8'),
            shadow=ft.BoxShadow(blur_radius=24, color='#33000000', offset=ft.Offset(0, 6)),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

    notif_overlay = ft.Container(visible=False)

    def open_panel(e):
        panel_open['v'] = True
        notif_overlay.content = build_notif_panel()
        notif_overlay.visible = True
        if notif_overlay not in page.overlay:
            page.overlay.append(notif_overlay)
        page.update()

    def close_panel():
        panel_open['v'] = False
        notif_overlay.visible = False
        page.update()

    def on_notif_tap(n):
        mark_notification_read(n['id'])
        n['is_read'] = True
        close_panel()
        if n.get('item_type') and n.get('item_id'):
            go(f"item_detail_{n['item_type']}_{n['item_id']}")

    def on_mark_all(e):
        mark_all_notifications_read()
        for n in notif_list:
            n['is_read'] = True
        refresh_badge()
        close_panel()

    def refresh_badge():
        unread       = [n for n in notif_list if not n['is_read']]
        unread_count = len(unread)
        has_match    = any(n.get('notification_type') == 'match' for n in unread)
        badge.content = ft.Text(str(unread_count), size=8, color='white', weight=ft.FontWeight.BOLD)
        badge.bgcolor  = '#e67e22' if has_match else 'red'
        badge.visible  = unread_count > 0
        page.update()

    def poll_notifications():
        while True:
            access, _ = load_tokens()
            if access:
                s, data = get_notifications()
                if s == 200 and isinstance(data, list):
                    notif_list.clear()
                    notif_list.extend(data)
                    refresh_badge()
            time.sleep(15)

    bell_btn = ft.Stack([
        ft.IconButton(ft.Icons.NOTIFICATIONS_OUTLINED, icon_color=BROWN,
                      icon_size=22, tooltip='Notifications', on_click=open_panel),
        ft.Container(badge, right=6, top=6),
    ])

    threading.Thread(target=poll_notifications, daemon=True).start()

    def go(route_name):
        current_route['name'] = route_name
        render()

    def render():
        route = current_route['name']
        page.controls.clear()

        access, _ = load_tokens()
        is_auth   = bool(access)
        content   = None

        if route and route.startswith('item_detail_'):
            parts     = route.split('_')
            item_type = parts[2]
            item_id   = int(parts[3])
            content   = item_detail_view(page, go, item_type, item_id)

        elif route and route.startswith('submit_claim_'):
            if not is_auth:
                go('login'); return
            parts     = route.split('_')
            item_type = parts[2]
            item_id   = int(parts[3])
            content   = submit_claim_view(page, go, item_type, item_id)

        else:
            view_fn = ROUTES.get(route, home_view)
            content = view_fn(page, go)

        show_nav = route not in ('login', 'register')

        if show_nav:
            # Routes where we show logo + "UniFind / University of Mauritius"
            primary_routes = {'home', 'browse_lost', 'browse_found', 'reviews', 'contact'}
            show_back = route not in primary_routes and route is not None

            # Sub-page title mapping
            sub_titles = {
                'browse_lost':  'Lost Items',
                'browse_found': 'Found Items',
                'report_lost':  'Report Lost',
                'report_found': 'Report Found',
                'profile':      'My Profile',
                'edit_profile': 'Edit Profile',
                'reviews':      'Reviews',
                'contact':      'Contact Us',
                'about':        'About',
            }
            if route and route.startswith('item_detail_'):
                page_title = 'Item Details'
            elif route and route.startswith('submit_claim_'):
                page_title = 'Submit Claim'
            else:
                page_title = sub_titles.get(route, 'UniFind')

            if show_back:
                # Sub-page: back arrow + page title
                leading_content = ft.IconButton(
                    ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
                    icon_color=BROWN, icon_size=18,
                    on_click=lambda e: go('home'),
                )
                appbar_title = ft.Text(
                    page_title, size=17, weight=ft.FontWeight.BOLD, color='#2c2c2a',
                )
            else:
                # Primary tabs: logo image + "UniFind\nUniversity of Mauritius"
                leading_content = ft.Container(
                    content=ft.Image(src='logo.png', fit='contain'),
                    width=36, height=36,
                    border_radius=8,
                )
                appbar_title = ft.Column([
                    ft.Text('UniFind', size=16, weight=ft.FontWeight.BOLD,
                            color='#2c2c2a', height=1.15),
                    ft.Text('University of Mauritius', size=10, color='#9a8f80'),
                ], spacing=0)

            appbar = ft.AppBar(
                leading=ft.Container(
                    content=leading_content,
                    padding=ft.padding.only(left=6),
                ),
                leading_width=52,
                title=appbar_title,
                bgcolor=NAV_BG,
                actions=[
                    ft.IconButton(ft.Icons.INFO_OUTLINE, icon_color=BROWN, icon_size=22,
                                  tooltip='About', on_click=lambda e: go('about')),
                    ft.IconButton(ft.Icons.PERSON_OUTLINE, icon_color=BROWN, icon_size=22,
                                  tooltip='Profile', on_click=lambda e: go('profile')),
                    bell_btn,
                ],
                toolbar_height=58,
            )
        else:
            appbar = None

        nav = ft.NavigationBar(
            bgcolor=NAV_BG,
            indicator_color='#d6cfc4',
            height=64,
            selected_index=_nav_index(route),
            on_change=lambda e: _on_nav(e, go, is_auth),
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED,
                                            selected_icon=ft.Icons.HOME_ROUNDED, label='Home'),
                ft.NavigationBarDestination(icon=ft.Icons.SEARCH_OUTLINED,
                                            selected_icon=ft.Icons.SEARCH_ROUNDED, label='Lost'),
                ft.NavigationBarDestination(icon=ft.Icons.INVENTORY_2_OUTLINED,
                                            selected_icon=ft.Icons.INVENTORY_2_ROUNDED, label='Found'),
                ft.NavigationBarDestination(icon=ft.Icons.STAR_BORDER_ROUNDED,
                                            selected_icon=ft.Icons.STAR_ROUNDED, label='Reviews'),
                ft.NavigationBarDestination(icon=ft.Icons.MAIL_OUTLINE_ROUNDED,
                                            selected_icon=ft.Icons.MAIL_ROUNDED, label='Contact'),
            ],
        ) if show_nav else None

        page.appbar = appbar
        page.add(
            ft.Container(
                content=content,
                padding=ft.padding.symmetric(horizontal=14, vertical=10),
                expand=True,
            )
        )
        if nav:
            page.navigation_bar = nav
        page.update()

    access, _ = load_tokens()
    go('home' if access else 'login')


def _nav_index(route):
    return {'home': 0, 'browse_lost': 1, 'browse_found': 2, 'reviews': 3, 'contact': 4}.get(route, 0)


def _on_nav(e, go, is_auth):
    routes = ['home', 'browse_lost', 'browse_found', 'reviews', 'contact']
    target = routes[e.control.selected_index]
    if target == 'reviews' and not is_auth:
        go('login')
    else:
        go(target)


ft.run(main, assets_dir='assets')