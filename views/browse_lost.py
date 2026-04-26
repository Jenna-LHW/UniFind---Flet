import flet as ft
from api import get_lost_items

CATEGORIES = ['', 'electronics', 'clothing', 'accessories', 'books_stationery', 'id_cards', 'bags', 'keys', 'other']
CAT_LABELS  = ['All', 'Electronics', 'Clothing', 'Accessories', 'Books', 'ID & Cards', 'Bags', 'Keys', 'Other']
BROWN = '#5c4f3a'

def browse_lost_view(page: ft.Page, go):
    page.title = 'Browse Lost Items'

    keyword_field = ft.TextField(
        hint_text='Search lost items...',
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        border_radius=24,
        filled=True,
        bgcolor='white',
        border_color='transparent',
        focused_border_color=BROWN,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        expand=True,
    )
    selected_cat = {'v': ''}
    results  = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
    loading  = ft.ProgressRing(visible=False, color=BROWN, width=24, height=24)
    error_text = ft.Text('', color=ft.Colors.RED_600, size=13)

    cat_buttons = ft.Ref[ft.Row]()

    def load(keyword='', category=''):
        loading.visible = True
        results.controls.clear()
        page.update()
        status, data = get_lost_items(keyword=keyword, category=category)
        loading.visible = False
        if status != 200:
            error_text.value = 'Failed to load items.'
            page.update(); return
        items = data if isinstance(data, list) else data.get('results', [])
        if not items:
            results.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SEARCH_OFF_ROUNDED, color='#c4bdb4', size=48),
                        ft.Text('No lost items found', color='#9a8f80', size=14),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=ft.padding.symmetric(vertical=40),
                    alignment=ft.Alignment(0, 0),
                )
            )
        else:
            for item in items:
                results.controls.append(_item_card(item, go))
        page.update()

    def do_search(e):
        load(keyword=keyword_field.value.strip(), category=selected_cat['v'])

    def select_cat(cat_val, btn_row):
        selected_cat['v'] = cat_val
        for btn in btn_row.controls:
            is_sel = btn.data == cat_val
            btn.style = ft.ButtonStyle(
                color='white' if is_sel else BROWN,
                bgcolor=BROWN if is_sel else 'white',
                side=ft.BorderSide(1, '#d6d1c8'),
                shape=ft.RoundedRectangleBorder(radius=20),
                padding=ft.padding.symmetric(horizontal=14, vertical=6),
            )
        page.update()
        load(keyword=keyword_field.value.strip(), category=cat_val)

    # Build category chips
    cat_row = ft.Row(spacing=6, scroll=ft.ScrollMode.AUTO)
    for i, (val, label) in enumerate(zip(CATEGORIES, CAT_LABELS)):
        is_sel = val == ''
        btn = ft.ElevatedButton(
            label,
            data=val,
            style=ft.ButtonStyle(
                color='white' if is_sel else BROWN,
                bgcolor=BROWN if is_sel else 'white',
                side=ft.BorderSide(1, '#d6d1c8'),
                shape=ft.RoundedRectangleBorder(radius=20),
                padding=ft.padding.symmetric(horizontal=14, vertical=6),
            ),
            on_click=lambda e, v=val, r=cat_row: select_cat(v, r),
        )
        cat_row.controls.append(btn)

    load()

    return ft.Column([
        # Search bar
        ft.Container(
            content=ft.Row([
                keyword_field,
                ft.IconButton(ft.Icons.SEARCH_ROUNDED, on_click=do_search,
                              bgcolor=BROWN, icon_color='white', icon_size=20),
            ], spacing=8),
            padding=ft.padding.symmetric(horizontal=0, vertical=4),
        ),

        # Category chips
        cat_row,

        # Report CTA
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED, color='white', size=18),
                ft.Text('Report a Lost Item', size=13, color='white', weight=ft.FontWeight.W_500),
                ft.Container(expand=True),
                ft.Icon(ft.Icons.ARROW_FORWARD_IOS_ROUNDED, color='white', size=12),
            ], spacing=10),
            padding=ft.padding.symmetric(horizontal=18, vertical=14),
            bgcolor=BROWN,
            border_radius=14,
            on_click=lambda e: go('report_lost'),
        ),

        error_text,
        ft.Container(content=loading, alignment=ft.Alignment(0, 0)),
        results,
    ], spacing=12, scroll=ft.ScrollMode.AUTO)


def _item_card(item, go):
    photo_url = item.get('photo_url')
    item_id   = item.get('id')

    if photo_url:
        photo = ft.Image(src=photo_url, width=70, height=70, fit='cover', border_radius=10)
    else:
        photo = ft.Container(
            content=ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED_OUTLINED, color='#c4bdb4', size=22),
            width=70, height=70, bgcolor='#f5f2ee', border_radius=10,
            alignment=ft.Alignment(0, 0),
        )

    cat_text = item.get('category', 'other').replace('_', ' ').title()
    status_val = item.get('status', '')

    return ft.GestureDetector(
        on_tap=lambda e: go(f'item_detail_lost_{item_id}'),
        content=ft.Container(
            content=ft.Row([
                photo,
                ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Text(cat_text[:10], color='white', size=10,
                                            weight=ft.FontWeight.BOLD),
                            bgcolor='#5c4f3a',
                            padding=ft.padding.symmetric(horizontal=8, vertical=3),
                            border_radius=20,
                        ),
                        ft.Container(expand=True),
                        ft.Container(
                            content=ft.Text(status_val.capitalize(), size=10,
                                            weight=ft.FontWeight.BOLD, color='#854f0b'),
                            bgcolor='#faeeda',
                            padding=ft.padding.symmetric(horizontal=8, vertical=3),
                            border_radius=20,
                        ),
                    ]),
                    ft.Text(item.get('item_name', ''), size=15, weight=ft.FontWeight.W_600,
                            color='#2c2c2a', max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Row([
                        ft.Icon(ft.Icons.LOCATION_ON_OUTLINED, size=12, color='#9a8f80'),
                        ft.Text(item.get('last_seen', '')[:35], size=11, color='#7a7670',
                                overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                    ], spacing=2),
                    ft.Row([
                        ft.Icon(ft.Icons.CALENDAR_TODAY_OUTLINED, size=11, color='#9a8f80'),
                        ft.Text(str(item.get('date_lost', '')), size=11, color='#9a8f80'),
                    ], spacing=2),
                ], spacing=4, expand=True),
                ft.Icon(ft.Icons.CHEVRON_RIGHT_ROUNDED, color='#c4bdb4', size=18),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=14,
            bgcolor='white',
            border_radius=14,
            border=ft.border.all(1, '#e8e2da'),
            shadow=ft.BoxShadow(blur_radius=4, color='#0a000000'),
        ),
    )
