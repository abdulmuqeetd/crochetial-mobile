"""
Crochetial Mobile App - Reference Style UI
Python/Kivy native Android app.

Preview on Windows:
    .venv\Scripts\activate
    python main.py
"""

from functools import partial
from urllib.parse import quote
import webbrowser

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, RoundedRectangle

from data import CONFIG, PRODUCTS, CAFE_ITEMS


# Reference-inspired palette, adjusted to Crochetial's beige/rose identity
COLORS = {
    "bg": (0.961, 0.922, 0.878, 1),          # warm beige
    "peach": (0.925, 0.647, 0.545, 1),       # soft peach card tone
    "peach_light": (0.984, 0.858, 0.780, 1),
    "cream": (1.000, 0.930, 0.850, 1),
    "surface": (1, 0.965, 0.920, 0.96),
    "white": (1, 1, 1, 1),
    "text": (0.361, 0.290, 0.231, 1),        # #5C4A3B
    "muted": (0.608, 0.541, 0.478, 1),       # #9B8A7A
    "primary": (0.831, 0.647, 0.604, 1),     # #D4A59A
    "primary_dark": (0.630, 0.345, 0.315, 1),
    "deep": (0.420, 0.150, 0.235, 1),        # burgundy-ish CTA
    "soft_border": (0.831, 0.647, 0.604, 0.22),
    "danger": (0.65, 0.16, 0.20, 1),
}

CITY_OPTIONS = ["Karachi", "Other cities", "Global"]
CATEGORY_TABS = [
    ("flowers", "Flowers", "FL"),
    ("keychains", "Keychains", "KC"),
    ("handmade-bags", "Bags", "BG"),
    ("cardigans", "Wear", "WR"),
    ("accessories", "Accessories", "AC"),
    ("cafe", "Cafe", "CF"),
]


def currency(n):
    return f"{CONFIG.get('currency_symbol', 'Rs')} {int(round(n)):,}"


def adjusted_price(price, city):
    return int(price * 2) if city == "Global" else int(price)


def shipping_cost(city, has_items=True):
    if not has_items:
        return 0
    if city == "Karachi":
        return CONFIG.get("ship_karachi", 350)
    if city == "Global":
        return CONFIG.get("ship_global", 0)
    return CONFIG.get("ship_other", 450)


def open_whatsapp(message):
    webbrowser.open(f"https://wa.me/{CONFIG['whatsapp_number']}?text={quote(message)}")


def pretty_category(key):
    mapping = {
        "flowers": "Flowers",
        "keychains": "Keychains",
        "handmade-bags": "Handmade Bags",
        "cardigans": "Wearables",
        "accessories": "Accessories",
        "acrylic-yarn": "Acrylic Yarn",
        "kids-set": "Kids Set",
        "cafe": "Cafe",
    }
    return mapping.get(key, key.replace("-", " ").title())


class RoundPanel(BoxLayout):
    bg_color = ListProperty(COLORS["surface"])

    def __init__(self, radius=26, **kwargs):
        super().__init__(**kwargs)
        self.radius = dp(radius)
        self.padding = kwargs.get("padding", dp(14))
        self.spacing = kwargs.get("spacing", dp(10))
        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
        self.bind(pos=self._update, size=self._update, bg_color=self._redraw)

    def _update(self, *_):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def _redraw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])


class PillButton(Button):
    def __init__(self, filled=False, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = COLORS["deep"] if filled else COLORS["surface"]
        self.color = COLORS["white"] if filled else COLORS["text"]
        self.bold = True
        self.font_size = kwargs.pop("font_size", dp(12))
        self.size_hint_y = kwargs.pop("size_hint_y", None)
        self.height = kwargs.pop("height", dp(44))


class AppLabel(Label):
    def __init__(self, role="body", **kwargs):
        super().__init__(**kwargs)
        if role == "title":
            self.color = COLORS["text"]
            self.bold = True
            self.font_size = kwargs.pop("font_size", dp(28))
        elif role == "price":
            self.color = COLORS["deep"]
            self.bold = True
            self.font_size = kwargs.pop("font_size", dp(17))
        elif role == "mini":
            self.color = COLORS["muted"]
            self.bold = True
            self.font_size = kwargs.pop("font_size", dp(10))
        else:
            self.color = COLORS["muted"]
            self.font_size = kwargs.pop("font_size", dp(13))
        self.halign = kwargs.pop("halign", "left")
        self.valign = kwargs.pop("valign", "middle")
        self.bind(size=lambda *_: setattr(self, "text_size", self.size))


class BaseScreen(Screen):
    @property
    def app(self):
        return App.get_running_app()

    def scroll_content(self, bottom=94):
        scroll = ScrollView(do_scroll_x=False, bar_width=dp(3))
        content = BoxLayout(orientation="vertical", spacing=dp(16), padding=[dp(18), dp(18), dp(18), dp(bottom)])
        content.size_hint_y = None
        content.bind(minimum_height=content.setter("height"))
        scroll.add_widget(content)
        self.add_widget(scroll)
        return content


class TopBar(RoundPanel):
    def __init__(self, title="Crochetial", **kwargs):
        super().__init__(orientation="horizontal", radius=0, padding=[dp(18), dp(8), dp(18), dp(8)], spacing=dp(10), **kwargs)
        self.bg_color = (0.961, 0.922, 0.878, 0.98)
        self.size_hint_y = None
        self.height = dp(64)
        menu = Button(text="=", size_hint_x=None, width=dp(42), background_normal="", background_color=(0,0,0,0), color=COLORS["text"], bold=True, font_size=dp(20))
        self.add_widget(menu)
        label = AppLabel(text=title, role="title", font_size=dp(19))
        self.add_widget(label)
        cart = PillButton(text="Cart", size_hint_x=None, width=dp(76), height=dp(40))
        cart.bind(on_release=lambda *_: setattr(App.get_running_app().root_widget.sm, "current", "cart"))
        self.add_widget(cart)


class HomeScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        content = self.scroll_content()

        header = RoundPanel(orientation="vertical", radius=30, padding=dp(18), spacing=dp(12))
        header.bg_color = COLORS["peach_light"]
        header.size_hint_y = None
        header.height = dp(260)
        content.add_widget(header)

        header.add_widget(AppLabel(text="Crochetial", role="title", font_size=dp(36), size_hint_y=None, height=dp(48)))
        header.add_widget(AppLabel(text="Handmade crochet, gifts, and homemade cafe treats.", role="body", font_size=dp(15), size_hint_y=None, height=dp(54)))
        buttons = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(48))
        b1 = PillButton(text="Shop Now", filled=True)
        b2 = PillButton(text="Cafe Menu")
        b1.bind(on_release=lambda *_: setattr(self.manager, "current", "shop"))
        b2.bind(on_release=lambda *_: setattr(self.manager, "current", "cafe"))
        buttons.add_widget(b1); buttons.add_widget(b2)
        header.add_widget(buttons)

        content.add_widget(section_title("Explore Categories"))
        content.add_widget(CategoryScroller())

        content.add_widget(section_title("Popular Items"))
        product_scroller = HorizontalProducts(PRODUCTS[:8])
        content.add_widget(product_scroller)

        content.add_widget(section_title("Cafe Specials"))
        cafe_row = GridLayout(cols=2, spacing=dp(12), size_hint_y=None, height=dp(176))
        for item in CAFE_ITEMS[:2]:
            cafe_row.add_widget(CafeMiniCard(item))
        content.add_widget(cafe_row)


class CategoryScroller(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(do_scroll_y=False, bar_width=0, size_hint_y=None, height=dp(96), **kwargs)
        row = BoxLayout(orientation="horizontal", spacing=dp(12), padding=[0, dp(4), 0, dp(4)])
        row.size_hint_x = None
        row.bind(minimum_width=row.setter("width"))
        for key, label, initials in CATEGORY_TABS:
            item = CategoryBubble(key, label, initials)
            row.add_widget(item)
        self.add_widget(row)


class CategoryBubble(BoxLayout):
    def __init__(self, key, label, initials, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(5), size_hint_x=None, width=dp(78), **kwargs)
        btn = Button(text=initials, size_hint=(None, None), size=(dp(58), dp(58)), background_normal="", background_color=COLORS["surface"], color=COLORS["deep"], bold=True, font_size=dp(15))
        btn.bind(on_release=lambda *_: self.open_category(key))
        self.add_widget(btn)
        self.add_widget(AppLabel(text=label, role="mini", halign="center", size_hint_y=None, height=dp(24)))

    def open_category(self, key):
        app = App.get_running_app()
        if key == "cafe":
            app.root_widget.sm.current = "cafe"
        else:
            shop = app.root_widget.sm.get_screen("shop")
            shop.set_filter(key)
            app.root_widget.sm.current = "shop"


class HorizontalProducts(ScrollView):
    def __init__(self, products, **kwargs):
        super().__init__(do_scroll_y=False, bar_width=0, size_hint_y=None, height=dp(255), **kwargs)
        row = BoxLayout(orientation="horizontal", spacing=dp(14))
        row.size_hint_x = None
        row.bind(minimum_width=row.setter("width"))
        for product in products:
            row.add_widget(ProductCard(product, width=dp(166)))
        self.add_widget(row)


class ProductCard(RoundPanel):
    def __init__(self, product, width=None, **kwargs):
        super().__init__(orientation="vertical", radius=28, padding=dp(10), spacing=dp(7), **kwargs)
        self.product = product
        self.bg_color = COLORS["peach_light"]
        self.size_hint_y = None
        self.height = dp(240)
        if width:
            self.size_hint_x = None
            self.width = width

        img_holder = RoundPanel(orientation="vertical", radius=24, padding=dp(4))
        img_holder.bg_color = (1, 1, 1, 0.72)
        img_holder.size_hint_y = None
        img_holder.height = dp(124)
        img_holder.add_widget(AsyncImage(source=product.get("image", ""), allow_stretch=True, keep_ratio=True))
        self.add_widget(img_holder)

        self.add_widget(AppLabel(text=product["name"], role="title", font_size=dp(15), size_hint_y=None, height=dp(38)))
        self.add_widget(AppLabel(text=pretty_category(product["category"]), role="mini", size_hint_y=None, height=dp(18)))
        bottom = BoxLayout(orientation="horizontal", spacing=dp(6), size_hint_y=None, height=dp(38))
        bottom.add_widget(AppLabel(text=currency(adjusted_price(product["price"], App.get_running_app().city)), role="price"))
        view = PillButton(text="View", filled=True, size_hint_x=None, width=dp(64), height=dp(36), font_size=dp(11))
        view.bind(on_release=lambda *_: App.get_running_app().open_product(product))
        bottom.add_widget(view)
        self.add_widget(bottom)


class ShopScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content = self.scroll_content()
        self.content.add_widget(section_title("Shop"))

        search_box = RoundPanel(orientation="vertical", radius=26, padding=dp(12), spacing=dp(10))
        search_box.size_hint_y = None
        search_box.height = dp(130)
        self.search = TextInput(hint_text="Search products", multiline=False, size_hint_y=None, height=dp(42), background_color=(1,1,1,0.86), foreground_color=COLORS["text"], cursor_color=COLORS["primary"])
        self.search.bind(text=lambda *_: self.render())
        self.spinner = Spinner(text="All", values=["All"] + [x[1] for x in CATEGORY_TABS if x[0] != "cafe"] + ["Acrylic Yarn", "Kids Set"], size_hint_y=None, height=dp(42), background_color=COLORS["deep"], color=COLORS["white"])
        self.spinner.bind(text=lambda *_: self.render())
        search_box.add_widget(self.search)
        search_box.add_widget(self.spinner)
        self.content.add_widget(search_box)

        self.grid = GridLayout(cols=2, spacing=dp(12), size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        self.content.add_widget(self.grid)
        self.render()

    def set_filter(self, category_key):
        mapping = {k: label for k, label, _ in CATEGORY_TABS}
        mapping.update({"acrylic-yarn": "Acrylic Yarn", "kids-set": "Kids Set"})
        self.spinner.text = mapping.get(category_key, "All")
        self.render()

    def category_key(self):
        label = self.spinner.text
        reverse = {v: k for k, v, _ in CATEGORY_TABS}
        reverse.update({"Acrylic Yarn": "acrylic-yarn", "Kids Set": "kids-set", "All": "all"})
        return reverse.get(label, "all")

    def render(self):
        if not hasattr(self, "grid"):
            return
        self.grid.clear_widgets()
        q = (self.search.text or "").strip().lower()
        cat = self.category_key()
        items = []
        for p in PRODUCTS:
            if cat != "all" and p["category"] != cat:
                continue
            hay = " ".join([p["name"], p["category"], " ".join(p.get("tags", []))]).lower()
            if q and q not in hay:
                continue
            items.append(p)
        if not items:
            empty = RoundPanel(orientation="vertical", padding=dp(16), radius=26)
            empty.size_hint_y = None
            empty.height = dp(100)
            empty.add_widget(AppLabel(text="No products found.", role="body"))
            self.grid.add_widget(empty)
            return
        for p in items:
            self.grid.add_widget(ProductCard(p))


class ProductDetailScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.product = None
        self.content = self.scroll_content(bottom=34)

    def set_product(self, product):
        self.product = product
        self.content.clear_widgets()

        top = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(8))
        back = PillButton(text="Back", size_hint_x=None, width=dp(86), height=dp(42))
        back.bind(on_release=lambda *_: setattr(self.manager, "current", "shop"))
        top.add_widget(back)
        top.add_widget(AppLabel(text="Product Detail", role="mini", halign="right"))
        self.content.add_widget(top)

        image_card = RoundPanel(orientation="vertical", radius=34, padding=dp(12), spacing=dp(6))
        image_card.bg_color = COLORS["peach"]
        image_card.size_hint_y = None
        image_card.height = dp(300)
        image_card.add_widget(AsyncImage(source=product.get("image", ""), allow_stretch=True, keep_ratio=True))
        self.content.add_widget(image_card)

        info = RoundPanel(orientation="vertical", radius=32, padding=dp(18), spacing=dp(10))
        info.size_hint_y = None
        info.height = dp(465)
        info.add_widget(AppLabel(text=product["name"], role="title", font_size=dp(28), size_hint_y=None, height=dp(62)))
        info.add_widget(AppLabel(text=pretty_category(product["category"]), role="mini", size_hint_y=None, height=dp(22)))
        info.add_widget(AppLabel(text=currency(adjusted_price(product["price"], self.app.city)), role="price", font_size=dp(22), size_hint_y=None, height=dp(38)))
        info.add_widget(AppLabel(text=product.get("desc", ""), role="body", font_size=dp(13)))

        self.size_spinner = Spinner(text=(product.get("sizes") or ["One Size"])[0], values=product.get("sizes") or ["One Size"], size_hint_y=None, height=dp(42), background_color=COLORS["surface"], color=COLORS["text"])
        self.color_spinner = Spinner(text=(product.get("colors") or ["Default"])[0], values=product.get("colors") or ["Default"], size_hint_y=None, height=dp(42), background_color=COLORS["surface"], color=COLORS["text"])
        info.add_widget(self.size_spinner)
        info.add_widget(self.color_spinner)
        save_btn = PillButton(text="Save Item", height=dp(42))
        save_btn.bind(on_release=lambda *_: self.app.toggle_favorite(product))
        info.add_widget(save_btn)

        actions = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(48))
        add = PillButton(text="Add to Cart", filled=True)
        buy = PillButton(text="Buy Now")
        add.bind(on_release=lambda *_: self.app.add_to_cart(product, self.size_spinner.text, self.color_spinner.text))
        buy.bind(on_release=lambda *_: self.buy_now())
        actions.add_widget(add)
        actions.add_widget(buy)
        info.add_widget(actions)
        self.content.add_widget(info)

    def buy_now(self):
        self.app.add_to_cart(self.product, self.size_spinner.text, self.color_spinner.text)
        self.manager.current = "cart"


class CafeScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        content = self.scroll_content()
        hero = RoundPanel(orientation="vertical", radius=30, padding=dp(20), spacing=dp(12))
        hero.bg_color = COLORS["peach_light"]
        hero.size_hint_y = None
        hero.height = dp(255)
        hero.add_widget(AppLabel(text="HOMEMADE CAFE MENU", role="mini", size_hint_y=None, height=dp(24)))
        hero.add_widget(AppLabel(text="Fresh coffee, cold coffee, bakes and savouries.", role="title", font_size=dp(27)))
        hero.add_widget(AppLabel(text="Prepared fresh on pre-order. Share quantity, date, and delivery or pickup preference on WhatsApp.", role="body"))
        order = PillButton(text="Order Cafe Items", filled=True)
        order.bind(on_release=lambda *_: open_whatsapp("Hi! I would like to order from the Crochetial Cafe menu."))
        hero.add_widget(order)
        content.add_widget(hero)

        content.add_widget(section_title("Cafe Items"))
        grid = GridLayout(cols=2, spacing=dp(12), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))
        for item in CAFE_ITEMS:
            grid.add_widget(CafeMiniCard(item))
        content.add_widget(grid)


class CafeMiniCard(RoundPanel):
    def __init__(self, item, **kwargs):
        super().__init__(orientation="vertical", radius=28, padding=dp(14), spacing=dp(8), **kwargs)
        self.bg_color = COLORS["surface"]
        self.size_hint_y = None
        self.height = dp(170)
        self.add_widget(AppLabel(text=item["title"], role="title", font_size=dp(18), size_hint_y=None, height=dp(44)))
        self.add_widget(AppLabel(text=item["description"], role="body", font_size=dp(12)))
        self.add_widget(AppLabel(text=item["price"], role="price", font_size=dp(13), size_hint_y=None, height=dp(28)))


class CartScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content = self.scroll_content()

    def on_pre_enter(self, *_):
        self.render()

    def render(self):
        self.content.clear_widgets()
        self.content.add_widget(section_title("Cart"))

        city_box = RoundPanel(orientation="vertical", radius=26, padding=dp(12), spacing=dp(8))
        city_box.size_hint_y = None
        city_box.height = dp(100)
        city_box.add_widget(AppLabel(text="Delivery Location", role="mini", size_hint_y=None, height=dp(24)))
        city = Spinner(text=self.app.city, values=CITY_OPTIONS, size_hint_y=None, height=dp(42), background_color=COLORS["deep"], color=COLORS["white"])
        city.bind(text=self.change_city)
        city_box.add_widget(city)
        self.content.add_widget(city_box)

        if not self.app.cart:
            empty = RoundPanel(orientation="vertical", padding=dp(18), radius=28)
            empty.size_hint_y = None
            empty.height = dp(120)
            empty.add_widget(AppLabel(text="Your cart is empty. Add products from the Shop page.", role="body"))
            self.content.add_widget(empty)
            return

        for idx, item in enumerate(self.app.cart):
            self.content.add_widget(CartItem(item, idx))

        totals = self.app.cart_totals()
        summary = RoundPanel(orientation="vertical", padding=dp(16), spacing=dp(8), radius=28)
        summary.size_hint_y = None
        summary.height = dp(185)
        summary.add_widget(AppLabel(text=f"Subtotal: {currency(totals['subtotal'])}", role="body", size_hint_y=None, height=dp(28)))
        summary.add_widget(AppLabel(text=f"Shipping: {currency(totals['shipping'])}", role="body", size_hint_y=None, height=dp(28)))
        summary.add_widget(AppLabel(text=f"Total: {currency(totals['total'])}", role="price", font_size=dp(20), size_hint_y=None, height=dp(38)))
        checkout = PillButton(text="Order via WhatsApp", filled=True)
        checkout.bind(on_release=lambda *_: self.app.checkout_whatsapp())
        summary.add_widget(checkout)
        self.content.add_widget(summary)

    def change_city(self, spinner, value):
        self.app.city = value
        self.render()


class CartItem(RoundPanel):
    def __init__(self, item, idx, **kwargs):
        super().__init__(orientation="horizontal", radius=26, padding=dp(10), spacing=dp(10), **kwargs)
        self.size_hint_y = None
        self.height = dp(128)
        app = App.get_running_app()
        product = item["product"]
        img_box = RoundPanel(orientation="vertical", radius=22, padding=dp(3))
        img_box.bg_color = COLORS["peach_light"]
        img_box.size_hint_x = None
        img_box.width = dp(96)
        img_box.add_widget(AsyncImage(source=product.get("image", ""), allow_stretch=True, keep_ratio=True))
        self.add_widget(img_box)

        box = BoxLayout(orientation="vertical", spacing=dp(4))
        box.add_widget(AppLabel(text=product["name"], role="title", font_size=dp(15), size_hint_y=None, height=dp(30)))
        box.add_widget(AppLabel(text=f"{item.get('size')} / {item.get('color')}", role="mini", size_hint_y=None, height=dp(22)))
        unit = adjusted_price(product["price"], app.city)
        box.add_widget(AppLabel(text=f"Qty {item['qty']} | {currency(unit * item['qty'])}", role="price", font_size=dp(13), size_hint_y=None, height=dp(26)))
        controls = GridLayout(cols=3, spacing=dp(6), size_hint_y=None, height=dp(34))
        minus = PillButton(text="-", height=dp(34))
        plus = PillButton(text="+", height=dp(34))
        remove = PillButton(text="Remove", height=dp(34))
        minus.bind(on_release=lambda *_: app.change_qty(idx, -1))
        plus.bind(on_release=lambda *_: app.change_qty(idx, 1))
        remove.bind(on_release=lambda *_: app.remove_from_cart(idx))
        controls.add_widget(minus); controls.add_widget(plus); controls.add_widget(remove)
        box.add_widget(controls)
        self.add_widget(box)


class ContactScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        content = self.scroll_content()
        content.add_widget(section_title("Contact"))
        card = RoundPanel(orientation="vertical", radius=30, padding=dp(20), spacing=dp(12))
        card.size_hint_y = None
        card.height = dp(280)
        card.add_widget(AppLabel(text="Need help placing an order?", role="title", font_size=dp(27)))
        card.add_widget(AppLabel(text=f"WhatsApp: {CONFIG['whatsapp_display']}\nEmail: {CONFIG['email']}\n\nFor cafe items, custom crochet orders, gifting, and delivery details, message us directly.", role="body"))
        btn = PillButton(text="Open WhatsApp", filled=True)
        btn.bind(on_release=lambda *_: open_whatsapp("Hi! I am interested in Crochetial products."))
        card.add_widget(btn)
        content.add_widget(card)


def section_title(text):
    row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(42))
    row.add_widget(AppLabel(text=text, role="title", font_size=dp(22)))
    return row


class MoreScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content = self.scroll_content()

    def on_pre_enter(self, *_):
        self.render()

    def render(self):
        self.content.clear_widgets()
        self.content.add_widget(section_title("More"))

        intro = RoundPanel(orientation="vertical", radius=30, padding=dp(20), spacing=dp(10))
        intro.size_hint_y = None
        intro.height = dp(155)
        intro.add_widget(AppLabel(text="Crochetial Services", role="title", font_size=dp(26)))
        intro.add_widget(AppLabel(text="Custom orders, gifting, tutoring, cafe requests and direct contact in one place.", role="body"))
        self.content.add_widget(intro)

        actions = GridLayout(cols=1, spacing=dp(12), size_hint_y=None)
        actions.bind(minimum_height=actions.setter("height"))
        buttons = [
            ("Custom Crochet Order", "Hi! I would like to place a custom crochet order."),
            ("Gift Basket Help", "Hi! I need help choosing a Crochetial gift basket."),
            ("Tutoring Session", "Hi! I am interested in crochet tutoring. Please share details."),
            ("Cafe Pre-Order", "Hi! I would like to pre-order from the Crochetial Cafe menu."),
            ("Contact Crochetial", "Hi! I have a question about Crochetial."),
        ]
        for title, message in buttons:
            btn = PillButton(text=title, filled=True, height=dp(48))
            btn.bind(on_release=lambda _, m=message: open_whatsapp(m))
            actions.add_widget(btn)
        self.content.add_widget(actions)

        self.content.add_widget(section_title("Saved Items"))
        if not self.app.favorites:
            empty = RoundPanel(orientation="vertical", radius=28, padding=dp(16))
            empty.size_hint_y = None
            empty.height = dp(96)
            empty.add_widget(AppLabel(text="No saved items yet. Open a product and tap Save Item.", role="body"))
            self.content.add_widget(empty)
        else:
            fav_grid = GridLayout(cols=2, spacing=dp(12), size_hint_y=None)
            fav_grid.bind(minimum_height=fav_grid.setter("height"))
            for product in self.app.favorites:
                fav_grid.add_widget(ProductCard(product))
            self.content.add_widget(fav_grid)


class BottomNav(BoxLayout):
    def __init__(self, sm, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=dp(72), padding=[dp(10), dp(8), dp(10), dp(10)], spacing=dp(8), **kwargs)
        self.sm = sm
        for label, screen in [("Home", "home"), ("Shop", "shop"), ("Cafe", "cafe"), ("Cart", "cart"), ("More", "more")]:
            btn = PillButton(text=label, height=dp(46))
            btn.bind(on_release=partial(self.switch_screen, screen))
            self.add_widget(btn)

    def switch_screen(self, screen, *_):
        self.sm.current = screen


class Root(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        with self.canvas.before:
            Color(*COLORS["bg"])
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[0])
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.add_widget(TopBar())
        self.sm = ScreenManager(transition=FadeTransition(duration=0.18))
        self.sm.add_widget(HomeScreen(name="home"))
        self.sm.add_widget(ShopScreen(name="shop"))
        self.sm.add_widget(ProductDetailScreen(name="product"))
        self.sm.add_widget(CafeScreen(name="cafe"))
        self.sm.add_widget(CartScreen(name="cart"))
        self.sm.add_widget(ContactScreen(name="contact"))
        self.sm.add_widget(MoreScreen(name="more"))
        self.add_widget(self.sm)
        self.add_widget(BottomNav(self.sm))

    def _update_bg(self, *_):
        self.bg.pos = self.pos
        self.bg.size = self.size


class CrochetialApp(App):
    title = "Crochetial"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart = []
        self.favorites = []
        self.city = "Karachi"

    def build(self):
        Window.clearcolor = COLORS["bg"]
        self.root_widget = Root()
        return self.root_widget

    def open_product(self, product):
        screen = self.root_widget.sm.get_screen("product")
        screen.set_product(product)
        self.root_widget.sm.current = "product"

    def add_to_cart(self, product, size=None, color=None):
        size = size or (product.get("sizes") or ["One Size"])[0]
        color = color or (product.get("colors") or ["Default"])[0]
        for item in self.cart:
            if item["product"]["id"] == product["id"] and item.get("size") == size and item.get("color") == color:
                item["qty"] += 1
                return
        self.cart.append({"product": product, "size": size, "color": color, "qty": 1})

    def change_qty(self, idx, delta):
        if 0 <= idx < len(self.cart):
            self.cart[idx]["qty"] += delta
            if self.cart[idx]["qty"] <= 0:
                self.cart.pop(idx)
        self.root_widget.sm.get_screen("cart").render()

    def remove_from_cart(self, idx):
        if 0 <= idx < len(self.cart):
            self.cart.pop(idx)
        self.root_widget.sm.get_screen("cart").render()

    def cart_totals(self):
        subtotal = sum(adjusted_price(i["product"]["price"], self.city) * i["qty"] for i in self.cart)
        shipping = shipping_cost(self.city, bool(self.cart))
        return {"subtotal": subtotal, "shipping": shipping, "total": subtotal + shipping}


    def toggle_favorite(self, product):
        for idx, item in enumerate(self.favorites):
            if item["id"] == product["id"]:
                self.favorites.pop(idx)
                return
        self.favorites.append(product)

    def checkout_whatsapp(self):
        if not self.cart:
            return
        totals = self.cart_totals()
        lines = [f"{CONFIG['store_name']} - Mobile App Order", "", f"Delivery: {self.city}", "", "Items:"]
        for item in self.cart:
            p = item["product"]
            unit = adjusted_price(p["price"], self.city)
            lines.append(f"- {item['qty']} x {p['name']} ({item.get('size')}, {item.get('color')}) @ {currency(unit)} = {currency(unit * item['qty'])}")
        lines += ["", f"Subtotal: {currency(totals['subtotal'])}", f"Shipping: {currency(totals['shipping'])}", f"Total: {currency(totals['total'])}"]
        open_whatsapp("\n".join(lines))


if __name__ == "__main__":
    CrochetialApp().run()
