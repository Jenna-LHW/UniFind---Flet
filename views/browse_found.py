import flet as ft
from api import get_found_items

CATEGORIES = ['', 'electronics', 'clothing', 'accessories', 'books_stationery', 'id_cards', 'bags', 'keys', 'other']
CAT_LABELS  = ['All Categories', 'Electronics', 'Clothing', 'Accessories', 'Books & Stationery', 'ID & Cards', 'Bags', 'Keys', 'Other']

def browse_found_view(page: ft.Page, go):
    page.title = 'Browse Found Items'

    keyword_field  = ft.TextField(label='Search', prefix_icon=ft.Icons.SEARCH, expand=True)
    category_field = ft.Dropdown(label='Category', width=200,
        options=[ft.dropdown.Option(CATEGORIES[i], CAT_LABELS[i]) for i in range(len(CATEGORIES))])
    results    = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO)
    loading    = ft.ProgressRing(visible=False)
    error_text = ft.Text('', color=ft.Colors.RED_600)

    def load(keyword='', category=''):
        loading.visible = True
        results.controls.clear()
        page.update()

        status, data = get_found_items(keyword=keyword, category=category)
        loading.visible = False

        if status != 200:
            error_text.value = 'Failed to load items.'
            page.update()
            return

        items = data if isinstance(data, list) else data.get('results', [])

        if not items:
            results.controls.append(ft.Text('No found items reported.', color='#7a7670'))
        else:
            for item in items:
                results.controls.append(_item_card(item, go))

        page.update()

    def do_search(e):
        load(keyword=keyword_field.value.strip(), category=category_field.value or '')

    category_field.on_change = do_search
    load()

    return ft.Column([
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.INVENTORY_2, color='white', size=24),
                ft.Column([
                    ft.Text('Browse Found Items', size=18, weight=ft.FontWeight.BOLD, color='#2c2c2a'),
                    ft.Text('Items found and reported on campus', size=12, color='#7a7670'),
                ], spacing=2),
                ft.Container(expand=True),
                ft.ElevatedButton('Report Found', bgcolor='#3b5c38', color='white',
                                  on_click=lambda e: go('report_found'), icon=ft.Icons.ADD),
            ]),
            padding=20, bgcolor='white', border_radius=12,
            border=ft.Border.all(1, '#d6d1c8'),
        ),
        ft.Container(
            content=ft.Row([
                keyword_field,
                category_field,
                ft.IconButton(ft.Icons.SEARCH, on_click=do_search,
                              bgcolor='#3b5c38', icon_color='white'),
            ], spacing=10),
            padding=16, bgcolor='white', border_radius=12,
            border=ft.Border.all(1, '#d6d1c8'),
        ),
        error_text,
        loading,
        results,
    ], spacing=16, scroll=ft.ScrollMode.AUTO)


def _item_card(item, go):
    photo_url = item.get('photo_url')
    item_id   = item.get('id')

    if photo_url:
        photo = ft.Image(src=photo_url, width=72, height=72, fit='cover', border_radius=8)
    else:
        photo = ft.Container(
            content=ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED, color='#b4b2a9', size=24),
            width=72, height=72, bgcolor='#f5f2ee', border_radius=8,
            alignment=ft.Alignment(0, 0),
        )

    return ft.GestureDetector(
        on_tap=lambda e: go(f'item_detail_found_{item_id}'),
        content=ft.Container(
            content=ft.Row([
                photo,
                ft.Container(width=4),
                ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Text(item.get('category', 'other').upper()[:3],
                                            color='white', size=11, weight=ft.FontWeight.BOLD),
                            bgcolor='#3b5c38',
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            border_radius=6,
                        ),
                        ft.Container(expand=True),
                        ft.Container(
                            content=ft.Text(item.get('status', '').capitalize(),
                                            size=11, weight=ft.FontWeight.BOLD, color='#3b6d11'),
                            bgcolor='#eaf3de',
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            border_radius=20,
                        ),
                    ]),
                    ft.Text(item.get('item_name', ''), size=15, weight=ft.FontWeight.W_600,
                            color='#2c2c2a', max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(f"📍 {item.get('found_at', '')[:40]}", size=12, color='#7a7670'),
                    ft.Text(f"📅 {item.get('date_found', '')}", size=11, color='#7a7670'),
                ], spacing=4, expand=True),
                ft.Icon(ft.Icons.CHEVRON_RIGHT, color='#b4b2a9', size=18),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=16, bgcolor='white', border_radius=12,
            border=ft.border.all(1, '#d6d1c8'),
        ),
    )