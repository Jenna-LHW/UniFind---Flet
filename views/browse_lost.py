import flet as ft
from api import get_lost_items

CATEGORIES = ['', 'electronics', 'clothing', 'accessories', 'books_stationery', 'id_cards', 'bags', 'keys', 'other']
CAT_LABELS  = ['All Categories', 'Electronics', 'Clothing', 'Accessories', 'Books & Stationery', 'ID & Cards', 'Bags', 'Keys', 'Other']

def browse_lost_view(page: ft.Page, go):
    page.title = 'Browse Lost Items'

    keyword_field  = ft.TextField(label='Search', prefix_icon=ft.Icons.SEARCH, expand=True)
    category_field = ft.Dropdown(label='Category', width=200,
        options=[ft.dropdown.Option(CATEGORIES[i], CAT_LABELS[i]) for i in range(len(CATEGORIES))])
    results        = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO)
    loading        = ft.ProgressRing(visible=False)
    error_text     = ft.Text('', color=ft.Colors.RED_600)

    def load(keyword='', category=''):
        loading.visible = True
        results.controls.clear()
        page.update()

        status, data = get_lost_items(keyword=keyword, category=category)
        loading.visible = False

        if status != 200:
            error_text.value = 'Failed to load items.'
            page.update()
            return

        items = data if isinstance(data, list) else data.get('results', [])

        if not items:
            results.controls.append(ft.Text('No lost items found.', color='#7a7670'))
        else:
            for item in items:
                results.controls.append(_item_card(item, go))

        page.update()

    def do_search(e):
        load(
            keyword=keyword_field.value.strip(),
            category=category_field.value or '',
        )

    category_field.on_change = do_search
    load()

    return ft.Column([
        # Header
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.SEARCH, color='white', size=24),
                ft.Column([
                    ft.Text('Browse Lost Items', size=18, weight=ft.FontWeight.BOLD, color='#2c2c2a'),
                    ft.Text('Find lost items reported on campus', size=12, color='#7a7670'),
                ], spacing=2),
                ft.Container(expand=True),
                ft.ElevatedButton('Report Lost', bgcolor='#5c4f3a', color='white',
                                  on_click=lambda e: go('report_lost'),
                                  icon=ft.Icons.ADD),
            ]),
            padding=20,
            bgcolor='white',
            border_radius=12,
            border=ft.Border.all(1, '#d6d1c8'),
        ),

        # Filters
        ft.Container(
            content=ft.Row([
                keyword_field,
                category_field,
                ft.IconButton(ft.Icons.SEARCH, on_click=do_search, bgcolor='#5c4f3a', icon_color='white'),
            ], spacing=10),
            padding=16,
            bgcolor='white',
            border_radius=12,
            border=ft.Border.all(1, '#d6d1c8'),
        ),

        error_text,
        loading,
        results,
    ], spacing=16, scroll=ft.ScrollMode.AUTO)


def _item_card(item, go):
    return ft.Container(
        content=ft.Row([
            ft.Container(
                content=ft.Text(item.get('category', 'other').upper()[:3],
                                color='white', size=11, weight=ft.FontWeight.BOLD),
                bgcolor='#5c4f3a',
                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                border_radius=6,
                width=48,
                alignment=ft.Alignment(0, 0),
            ),
            ft.Column([
                ft.Text(item.get('item_name', ''), size=15, weight=ft.FontWeight.W_600, color='#2c2c2a'),
                ft.Text(f"📍 {item.get('last_seen', '')[:40]}", size=12, color='#7a7670'),
                ft.Text(f"📅 {item.get('date_lost', '')}", size=11, color='#7a7670'),
            ], spacing=3, expand=True),
            ft.Container(
                content=ft.Text(item.get('status', '').capitalize(), size=11, weight=ft.FontWeight.BOLD,
                                color='#854f0b'),
                bgcolor='#faeeda',
                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                border_radius=20,
            ),
        ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        padding=16,
        bgcolor='white',
        border_radius=12,
        border=ft.Border.all(1, '#d6d1c8'),
    )