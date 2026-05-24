# Crochetial Mobile App Starter

Python/Kivy native Android starter for Crochetial.

## Screens included
- Home: branded moodboard-style landing
- Shop: crochet product categories
- Cafe: homemade coffee, cold coffee, bakes, savouries
- Contact: WhatsApp order CTA

## Desktop preview
```bash
pip install -r requirements.txt
python main.py
```

## Android APK build
Buildozer works best on Linux:
```bash
pip install buildozer
buildozer -v android debug
```
APK output will be in `bin/`.

## Next MVP steps
- Add full product list from website
- Product detail screens
- Cart and delivery location
- WhatsApp order summary
- Local storage for favourites/cart
