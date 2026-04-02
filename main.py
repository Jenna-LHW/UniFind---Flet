import flet as ft
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
from storage            import load_tokens

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
    page.title          = 'UniFind'
    page.bgcolor        = LIGHT
    page.padding        = 0
    page.theme_mode     = ft.ThemeMode.LIGHT
    page.window_width   = 420
    page.window_height  = 800

    current_route = {'name': None}

    def go(route_name):
        current_route['name'] = route_name
        render()

    def render():
        route = current_route['name']
        page.controls.clear()

        # Build content
        view_fn = ROUTES.get(route, home_view)
        content = view_fn(page, go)

        # Nav bar (hide on login/register)
        show_nav = route not in ('login', 'register')
        access, _ = load_tokens()
        is_auth = bool(access)

        nav = ft.NavigationBar(
            bgcolor=NAV_BG,
            indicator_color='#d6cfc4',
            selected_index=_nav_index(route),
            on_change=lambda e: _on_nav(e, go, is_auth),
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED,     selected_icon=ft.Icons.HOME,          label='Home'),
                ft.NavigationBarDestination(icon=ft.Icons.SEARCH_OUTLINED,   selected_icon=ft.Icons.SEARCH,        label='Lost'),
                ft.NavigationBarDestination(icon=ft.Icons.INVENTORY_2_OUTLINED, selected_icon=ft.Icons.INVENTORY_2, label='Found'),
                ft.NavigationBarDestination(icon=ft.Icons.STAR_OUTLINE,      selected_icon=ft.Icons.STAR,          label='Reviews'),
                ft.NavigationBarDestination(icon=ft.Icons.PERSON_OUTLINE,    selected_icon=ft.Icons.PERSON,        label='Profile'),
            ],
        ) if show_nav else None

        # Top app bar
        appbar = ft.AppBar(
            leading=ft.Container(
                content=ft.Image(
                    src='assets/logo.png',
                    fit="contain",
                ),
                width=48,
                height=48,
                padding=4,
            ),
            leading_width=56,
            title=ft.Column([
                ft.Text('UniFind', size=16, weight=ft.FontWeight.BOLD, color='#2c2c2a'),
                ft.Text('University of Mauritius', size=10, color='#7a7670'),
            ], spacing=0),
            bgcolor=NAV_BG,
            actions=[
                ft.IconButton(ft.Icons.MAIL_OUTLINE, icon_color=BROWN,
                            tooltip='Contact', on_click=lambda e: go('contact')),
                ft.IconButton(
                    ft.Icons.LOGOUT if is_auth else ft.Icons.LOGIN,
                    icon_color=BROWN,
                    tooltip='Logout' if is_auth else 'Login',
                    on_click=lambda e: go('login'),
                ),
            ],
        ) if show_nav else None

        page.appbar = appbar

        page.add(
            ft.Container(
                content=content,
                padding=ft.Padding.all(16),
                expand=True,
            )
        )

        if nav:
            page.navigation_bar = nav

        page.update()

    # Decide start route
    access, _ = load_tokens()
    go('home' if access else 'login')


def _nav_index(route):
    mapping = {
        'home':         0,
        'browse_lost':  1,
        'browse_found': 2,
        'reviews':      3,
        'profile':      4,
    }
    return mapping.get(route, 0)


def _on_nav(e, go, is_auth):
    routes = ['home', 'browse_lost', 'browse_found', 'reviews', 'profile']
    target = routes[e.control.selected_index]
    if target in ('reviews', 'profile') and not is_auth:
        go('login')
    else:
        go(target)


ft.app(target=main, assets_dir='assets')