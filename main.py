import flet as ft
import threading, time
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from views.login        import login_view
from views.register     import register_view
from views.home         import home_view
from views.browse_lost  import browse_lost_view
from views.browse_found import browse_found_view
from views.report_lost  import report_lost_view
from views.report_found import report_found_view
from views.profile      import profile_view
from views.reviews      import reviews_view
from views.contact      import contact_view
from views.item_detail  import item_detail_view
from views.submit_claim import submit_claim_view
from storage            import load_tokens
from api import get_notifications, mark_notification_read, mark_all_notifications_read

# Static routes
ROUTES = {
    'login':        login_view,
    'register':     register_view,
    'home':         home_view,
    'browse_lost':  browse_lost_view,
    'browse_found': browse_found_view,
    'report_lost':  report_lost_view,
    'report_found': report_found_view,
    'profile':      profile_view,
    'reviews':      reviews_view,
    'contact':      contact_view,
}

BROWN  = '#5c4f3a'
LIGHT  = '#f5f2ee'
NAV_BG = '#ede9e3'


def main(page: ft.Page):
    page.title        = 'UniFind'
    page.bgcolor      = LIGHT
    page.padding      = 0
    page.theme_mode   = ft.ThemeMode.LIGHT
    page.window_width  = 420
    page.window_height = 800

    current_route = {'name': None}

    notif_list  = []          # full list fetched from API
    panel_open  = {'v': False}

    badge = ft.Container(
        content=ft.Text('0', size=9, color='white', weight=ft.FontWeight.BOLD),
        bgcolor='red',
        border_radius=10,
        padding=ft.Padding.symmetric(horizontal=4, vertical=1),
        visible=False,
    )

    def build_notif_panel():
        unread = [n for n in notif_list if not n['is_read']]
        rows   = []

        if not notif_list:
            rows.append(ft.Text('No notifications yet.', color='#7a7670',
                                size=13, italic=True))
        else:
            for n in notif_list[:20]:               # cap at 20
                is_read = n['is_read']
                rows.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Container(width=6, height=6, border_radius=3,
                                         bgcolor='red' if not is_read else 'transparent'),
                            ft.Column([
                                ft.Text(n['title'], size=13,
                                        weight=ft.FontWeight.BOLD if not is_read
                                               else ft.FontWeight.NORMAL,
                                        color='#2c2c2a'),
                                ft.Text(n['body'][:80] + ('…' if len(n['body']) > 80 else ''),
                                        size=11, color='#7a7670'),
                            ], spacing=2, expand=True),
                        ], spacing=8),
                        padding=10,
                        bgcolor='#fdfaf6' if not is_read else 'white',
                        border=ft.Border.only(bottom=ft.BorderSide(1, '#f0ece6')),
                        on_click=lambda e, n=n: on_notif_tap(n),
                        border_radius=8,
                    )
                )

        actions = []
        if unread:
            actions.append(
                ft.TextButton('Mark all read', on_click=on_mark_all)
            )

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text('Notifications', size=14,
                            weight=ft.FontWeight.BOLD, color=BROWN),
                    ft.IconButton(ft.Icons.CLOSE, icon_size=16,
                                  on_click=lambda e: close_panel()),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=1),
                ft.Column(rows, spacing=4, scroll=ft.ScrollMode.AUTO,
                          height=300),
                *actions,
            ], spacing=8),
            width=320,
            padding=16,
            bgcolor='white',
            border_radius=12,
            border=ft.Border.all(1, '#d6d1c8'),
            shadow=ft.BoxShadow(blur_radius=16, color='#22000000',
                                offset=ft.Offset(0, 4)),
        )

    notif_overlay = ft.Container(visible=False)   # placeholder, replaced on open

    def open_panel(e):
        panel_open['v'] = True
        notif_overlay.content = build_notif_panel()
        notif_overlay.visible = True
        page.overlay.append(notif_overlay) if notif_overlay not in page.overlay else None
        page.update()

    def close_panel():
        panel_open['v'] = False
        notif_overlay.visible = False
        page.update()

    def on_notif_tap(n):
        mark_notification_read(n['id'])
        n['is_read'] = True          # update local copy immediately
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
        unread = sum(1 for n in notif_list if not n['is_read'])
        badge.content = ft.Text(str(unread), size=9, color='white',
                                weight=ft.FontWeight.BOLD)
        badge.visible = unread > 0
        page.update()

    def poll_notifications():
        """Background thread — polls every 15 s."""
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
        ft.IconButton(
            ft.Icons.NOTIFICATIONS_OUTLINED,
            icon_color=BROWN,
            tooltip='Notifications',
            on_click=open_panel,
        ),
        ft.Container(badge, right=4, top=4),   # badge sits top-right of bell
    ])

    # Start polling thread (daemon so it dies with the app)
    threading.Thread(target=poll_notifications, daemon=True).start()

    def go(route_name):
        current_route['name'] = route_name
        render()

    def render():
        route = current_route['name']
        page.controls.clear()

        access, _ = load_tokens()
        is_auth   = bool(access)

        # ── Dynamic routes ──────────────────────────────────
        # item_detail_lost_<pk>  →  item_detail_view(lost, pk)
        # item_detail_found_<pk> →  item_detail_view(found, pk)
        # submit_claim_lost_<pk> →  submit_claim_view(lost, pk)
        # submit_claim_found_<pk>→  submit_claim_view(found, pk)
        content = None

        if route and route.startswith('item_detail_'):
            parts     = route.split('_')   # ['item','detail','lost/found','pk']
            item_type = parts[2]
            item_id   = int(parts[3])
            content   = item_detail_view(page, go, item_type, item_id)

        elif route and route.startswith('submit_claim_'):
            if route == 'profile' and not is_auth:
                go('login')
                return
            parts     = route.split('_')   # ['submit','claim','lost/found','pk']
            item_type = parts[2]
            item_id   = int(parts[3])
            content   = submit_claim_view(page, go, item_type, item_id)

        else:
            view_fn = ROUTES.get(route, home_view)
            content = view_fn(page, go)

        # ── Nav bar ─────────────────────────────────────────
        show_nav = route not in ('login', 'register')

        nav = ft.NavigationBar(
            bgcolor=NAV_BG,
            indicator_color='#d6cfc4',
            selected_index=_nav_index(route),
            on_change=lambda e: _on_nav(e, go, is_auth),
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED,        selected_icon=ft.Icons.HOME,        label='Home'),
                ft.NavigationBarDestination(icon=ft.Icons.SEARCH_OUTLINED,      selected_icon=ft.Icons.SEARCH,      label='Lost'),
                ft.NavigationBarDestination(icon=ft.Icons.INVENTORY_2_OUTLINED, selected_icon=ft.Icons.INVENTORY_2, label='Found'),
                ft.NavigationBarDestination(icon=ft.Icons.STAR_OUTLINE,         selected_icon=ft.Icons.STAR,        label='Reviews'),
                ft.NavigationBarDestination(icon=ft.Icons.MAIL_OUTLINE,         selected_icon=ft.Icons.MAIL,        label='Contact'),
            ],
        ) if show_nav else None

        appbar = ft.AppBar(
            leading=ft.Container(
                content=ft.Image(src='assets/logo.png', fit='contain'),
                width=48, height=48, padding=4,
            ),
            leading_width=56,
            title=ft.Column([
                ft.Text('UniFind', size=16, weight=ft.FontWeight.BOLD, color='#2c2c2a'),
                ft.Text('University of Mauritius', size=10, color='#7a7670'),
            ], spacing=0),
            bgcolor=NAV_BG,
            actions=[
                ft.IconButton(ft.Icons.PERSON_OUTLINE, icon_color=BROWN, tooltip='Profile', on_click=lambda e: go('profile')),
                bell_btn
            ],
        ) if show_nav else None

        page.appbar = appbar
        page.add(
            ft.Container(content=content, padding=ft.Padding.all(16), expand=True)
        )
        if nav:
            page.navigation_bar = nav
        page.update()

    access, _ = load_tokens()
    go('home' if access else 'login')


def _nav_index(route):
    mapping = {
        'home':         0,
        'browse_lost':  1,
        'browse_found': 2,
        'reviews':      3,
        'contact':      4,
    }
    return mapping.get(route, 0)


def _on_nav(e, go, is_auth): 
    routes = ['home', 'browse_lost', 'browse_found', 'reviews', 'contact']
    target = routes[e.control.selected_index]
 
    if target == 'reviews' and not is_auth:
        go('login')
    else:
        go(target)


ft.app(main, assets_dir='assets')