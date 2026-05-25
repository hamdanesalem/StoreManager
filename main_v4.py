"""
StoreManager v4.0 – Application complète de gestion de boutique
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fonctionnalités :
  • Mode Jour / Nuit avec toggle
  • Navigation par barre inférieure (style mobile)
  • Stock : recherche, tri, réapprovisionnement rapide
  • Ventes : remise, sélecteur recherchable
  • Historique : filtres par date/catégorie, export CSV
  • Tableau de bord : KPIs, graphique barres, top produits
  • Paramètres : langue, devise, PIN, sauvegarde JSON
  • Alertes stock faible avec badge rouge
  • Multi-langues : Français / English / عربي
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog, Canvas
import json, csv, os, hashlib
from datetime import datetime, timedelta
from collections import Counter, defaultdict

# ══════════════════════════════════════════════════════════════════════════════
#  PALETTES  –  Saphir & Or (nuit)   /   Ivoire & Émeraude (jour)
# ══════════════════════════════════════════════════════════════════════════════
PALETTES = {
    "dark": {
        "bg":          "#07091A",   # Bleu nuit absolu
        "bg_alt":      "#0D1020",   # Légèrement plus clair
        "card":        "#131729",   # Surface des cartes
        "card2":       "#1A1F35",   # Cartes surélevées
        "accent":      "#4F8EF7",   # Saphir électrique
        "accent_d":    "#3A72D8",   # Saphir foncé (hover)
        "gold":        "#F5A623",   # Or ambré
        "gold_d":      "#D4891A",
        "success":     "#00C896",   # Menthe
        "danger":      "#FF4365",   # Rose-rouge vif
        "warning":     "#FFB020",   # Ambre
        "text":        "#E8EDF5",   # Blanc bleuté
        "text2":       "#7A87A8",   # Gris-bleu doux
        "border":      "#1E2540",   # Bordure subtile
        "nav":         "#0D1020",   # Barre de navigation
        "sep":         "#252D4A",
    },
    "light": {
        "bg":          "#F4F6FB",   # Gris-bleu très pâle
        "bg_alt":      "#EAEEF6",
        "card":        "#FFFFFF",   # Blanc pur
        "card2":       "#F0F4FF",   # Bleu très pâle
        "accent":      "#2563EB",   # Bleu roi
        "accent_d":    "#1D4ED8",
        "gold":        "#D97706",   # Ambre foncé
        "gold_d":      "#B45309",
        "success":     "#059669",   # Émeraude
        "danger":      "#DC2626",   # Rouge
        "warning":     "#D97706",
        "text":        "#111827",   # Presque noir
        "text2":       "#6B7280",   # Gris neutre
        "border":      "#D1D8E8",
        "nav":         "#FFFFFF",
        "sep":         "#E5EAF3",
    },
}

_palette = PALETTES["dark"]

def c(key):
    """Raccourci pour obtenir une couleur du thème actuel."""
    return _palette[key]

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ══════════════════════════════════════════════════════════════════════════════
#  TRADUCTIONS  (fr / en / ar)
# ══════════════════════════════════════════════════════════════════════════════
TR = {
    "fr": {
        "app":        "StoreManager",
        "tagline":    "Votre boutique, toujours à portée de main.",
        "nav_stock":  "Stock",
        "nav_sales":  "Ventes",
        "nav_dash":   "Tableau",
        "nav_hist":   "Historique",
        "nav_settings":"Réglages",
        # Stock
        "stock_title":"Gestion du Stock",
        "add":        "+ Ajouter",
        "search_ph":  "🔍 Rechercher…",
        "sort_name":  "Trier : Nom",
        "sort_price": "Trier : Prix",
        "sort_qty":   "Trier : Qté",
        "col_name":   "Produit",
        "col_price":  "Prix",
        "col_qty":    "Qté",
        "no_products":"Aucun produit. Tapez '+ Ajouter'.",
        "restock":    "Réapprovisionner",
        "restock_qty":"Quantité à ajouter :",
        # Formulaire
        "add_product":"Nouveau produit",
        "edit_product":"Modifier",
        "name_lbl":   "Nom",
        "price_lbl":  "Prix",
        "qty_lbl":    "Quantité",
        "cat_lbl":    "Catégorie",
        "save":       "Enregistrer",
        "cancel":     "Annuler",
        "delete":     "Supprimer",
        "confirm_del":"Supprimer '{n}' ?",
        "irreversible":"Cette action est irréversible.",
        # Ventes
        "sales_title":"Ventes",
        "summary":    "Résumé global",
        "no_sales":   "Aucune vente enregistrée.",
        "pick_product":"Choisir un produit",
        "no_selected":"Aucun produit sélectionné",
        "qty_sell":   "Quantité à vendre",
        "discount":   "Remise (%)",
        "confirm_sale":"Confirmer la vente",
        "sale_ok":    "✓  {q}× {n}  →  {cur}{t:.2f}",
        "trans":      "Transactions",
        "units_sold": "Unités vendues",
        "revenue":    "Revenus totaux",
        # Historique
        "hist_title": "Historique des ventes",
        "export_csv": "Exporter CSV",
        "filter_all": "Tous",
        "filter_today":"Aujourd'hui",
        "filter_week":"Cette semaine",
        "date_col":   "Date",
        "total_col":  "Total",
        # Tableau de bord
        "dash_title": "Tableau de Bord",
        "inventory_val":"Valeur stock",
        "low_count":  "Alertes stock",
        "top5":       "🏆  Top 5 Produits",
        "no_data":    "Pas encore de données.",
        "chart_title":"Ventes (7 derniers jours)",
        "stock_alerts":"⚠  Alertes Stock",
        "stock_ok":   "✓  Tout le stock est suffisant.",
        # Paramètres
        "settings_title":"Paramètres",
        "theme":      "🌓  Thème",
        "dark":       "Mode Nuit",
        "light":      "Mode Jour",
        "lang":       "🌐  Langue",
        "currency":   "💱  Devise",
        "threshold":  "📊  Seuil alerte stock",
        "apply":      "✓",
        "pin":        "🔒  Code PIN",
        "pin_active": "Actif ••••",
        "pin_off":    "Désactivé",
        "change":     "Modifier",
        "remove":     "Retirer",
        "backup":     "🗄  Sauvegarde",
        "save_btn":   "💾 Sauvegarder",
        "load_btn":   "📂 Restaurer",
        "version":    "ℹ  Version",
        # PIN dialog
        "pin_enter":  "Entrez votre code PIN",
        "pin_new":    "Nouveau code (4 chiffres)",
        "pin_confirm":"Confirmer le code",
        "unlock":     "Déverrouiller",
        "pin_wrong":  "Code PIN incorrect",
        "pin_nomatch":"Les codes ne correspondent pas",
        "pin_invalid":"Le PIN doit contenir 4 chiffres",
        "pin_set":    "Code PIN activé avec succès",
        # Erreurs
        "err_name":   "⚠  Le nom est obligatoire.",
        "err_price":  "⚠  Prix invalide.",
        "err_qty":    "⚠  Quantité invalide.",
        "err_pick":   "⚠  Sélectionnez d'abord un produit.",
        "err_qty2":   "⚠  Quantité invalide (min. 1).",
        "err_stock":  "⚠  Stock insuffisant ({n} dispo).",
        # Misc
        "units":      "unités",
        "saved":      "Données sauvegardées.",
        "loaded":     "Données restaurées.",
        "cat_all":    "Toutes catégories",
    },
    "en": {
        "app":        "StoreManager",
        "tagline":    "Your store, always at hand.",
        "nav_stock":  "Stock",
        "nav_sales":  "Sales",
        "nav_dash":   "Dashboard",
        "nav_hist":   "History",
        "nav_settings":"Settings",
        "stock_title":"Stock Management",
        "add":        "+ Add",
        "search_ph":  "🔍 Search…",
        "sort_name":  "Sort: Name",
        "sort_price": "Sort: Price",
        "sort_qty":   "Sort: Qty",
        "col_name":   "Product",
        "col_price":  "Price",
        "col_qty":    "Qty",
        "no_products":"No products yet. Tap '+ Add'.",
        "restock":    "Restock",
        "restock_qty":"Quantity to add:",
        "add_product":"New product",
        "edit_product":"Edit",
        "name_lbl":   "Name",
        "price_lbl":  "Price",
        "qty_lbl":    "Quantity",
        "cat_lbl":    "Category",
        "save":       "Save",
        "cancel":     "Cancel",
        "delete":     "Delete",
        "confirm_del":"Delete '{n}'?",
        "irreversible":"This cannot be undone.",
        "sales_title":"Sales",
        "summary":    "Global Summary",
        "no_sales":   "No sales recorded.",
        "pick_product":"Choose a product",
        "no_selected":"No product selected",
        "qty_sell":   "Quantity to sell",
        "discount":   "Discount (%)",
        "confirm_sale":"Confirm Sale",
        "sale_ok":    "✓  {q}× {n}  →  {cur}{t:.2f}",
        "trans":      "Transactions",
        "units_sold": "Units sold",
        "revenue":    "Total revenue",
        "hist_title": "Sales History",
        "export_csv": "Export CSV",
        "filter_all": "All",
        "filter_today":"Today",
        "filter_week":"This week",
        "date_col":   "Date",
        "total_col":  "Total",
        "dash_title": "Dashboard",
        "inventory_val":"Stock value",
        "low_count":  "Stock alerts",
        "top5":       "🏆  Top 5 Products",
        "no_data":    "No data yet.",
        "chart_title":"Sales (last 7 days)",
        "stock_alerts":"⚠  Stock Alerts",
        "stock_ok":   "✓  All stock levels are fine.",
        "settings_title":"Settings",
        "theme":      "🌓  Theme",
        "dark":       "Dark Mode",
        "light":      "Light Mode",
        "lang":       "🌐  Language",
        "currency":   "💱  Currency",
        "threshold":  "📊  Low stock threshold",
        "apply":      "✓",
        "pin":        "🔒  PIN Code",
        "pin_active": "Active ••••",
        "pin_off":    "Disabled",
        "change":     "Change",
        "remove":     "Remove",
        "backup":     "🗄  Backup",
        "save_btn":   "💾 Save",
        "load_btn":   "📂 Restore",
        "version":    "ℹ  Version",
        "pin_enter":  "Enter your PIN code",
        "pin_new":    "New code (4 digits)",
        "pin_confirm":"Confirm code",
        "unlock":     "Unlock",
        "pin_wrong":  "Wrong PIN code",
        "pin_nomatch":"Codes do not match",
        "pin_invalid":"PIN must be 4 digits",
        "pin_set":    "PIN code activated",
        "err_name":   "⚠  Name is required.",
        "err_price":  "⚠  Invalid price.",
        "err_qty":    "⚠  Invalid quantity.",
        "err_pick":   "⚠  Please select a product first.",
        "err_qty2":   "⚠  Invalid quantity (min 1).",
        "err_stock":  "⚠  Not enough stock ({n} available).",
        "units":      "units",
        "saved":      "Data saved.",
        "loaded":     "Data restored.",
        "cat_all":    "All categories",
    },
    "ar": {
        "app":        "إدارة المتجر",
        "tagline":    "متجرك دائماً في متناول يدك.",
        "nav_stock":  "المخزون",
        "nav_sales":  "المبيعات",
        "nav_dash":   "لوحة",
        "nav_hist":   "السجل",
        "nav_settings":"إعدادات",
        "stock_title":"إدارة المخزون",
        "add":        "+ إضافة",
        "search_ph":  "🔍 بحث…",
        "sort_name":  "ترتيب: الاسم",
        "sort_price": "ترتيب: السعر",
        "sort_qty":   "ترتيب: الكمية",
        "col_name":   "المنتج",
        "col_price":  "السعر",
        "col_qty":    "الكمية",
        "no_products":"لا توجد منتجات. اضغط '+ إضافة'.",
        "restock":    "تجديد المخزون",
        "restock_qty":"الكمية المضافة:",
        "add_product":"منتج جديد",
        "edit_product":"تعديل",
        "name_lbl":   "الاسم",
        "price_lbl":  "السعر",
        "qty_lbl":    "الكمية",
        "cat_lbl":    "الفئة",
        "save":       "حفظ",
        "cancel":     "إلغاء",
        "delete":     "حذف",
        "confirm_del":"حذف '{n}'؟",
        "irreversible":"لا يمكن التراجع.",
        "sales_title":"المبيعات",
        "summary":    "الملخص العام",
        "no_sales":   "لا توجد مبيعات.",
        "pick_product":"اختر منتجاً",
        "no_selected":"لم يتم الاختيار",
        "qty_sell":   "الكمية للبيع",
        "discount":   "خصم (%)",
        "confirm_sale":"تأكيد البيع",
        "sale_ok":    "✓  {q}× {n}  ←  {cur}{t:.2f}",
        "trans":      "المعاملات",
        "units_sold": "الوحدات المباعة",
        "revenue":    "إجمالي الإيرادات",
        "hist_title": "سجل المبيعات",
        "export_csv": "تصدير CSV",
        "filter_all": "الكل",
        "filter_today":"اليوم",
        "filter_week":"هذا الأسبوع",
        "date_col":   "التاريخ",
        "total_col":  "المجموع",
        "dash_title": "لوحة التحكم",
        "inventory_val":"قيمة المخزون",
        "low_count":  "تنبيهات المخزون",
        "top5":       "🏆  أفضل 5 منتجات",
        "no_data":    "لا توجد بيانات بعد.",
        "chart_title":"المبيعات (7 أيام)",
        "stock_alerts":"⚠  تنبيهات المخزون",
        "stock_ok":   "✓  مستوى المخزون جيد.",
        "settings_title":"الإعدادات",
        "theme":      "🌓  المظهر",
        "dark":       "الوضع الليلي",
        "light":      "الوضع النهاري",
        "lang":       "🌐  اللغة",
        "currency":   "💱  العملة",
        "threshold":  "📊  حد تنبيه المخزون",
        "apply":      "✓",
        "pin":        "🔒  رمز PIN",
        "pin_active": "نشط ••••",
        "pin_off":    "معطّل",
        "change":     "تغيير",
        "remove":     "إزالة",
        "backup":     "🗄  النسخ الاحتياطي",
        "save_btn":   "💾 حفظ",
        "load_btn":   "📂 استعادة",
        "version":    "ℹ  الإصدار",
        "pin_enter":  "أدخل رمز PIN",
        "pin_new":    "رمز جديد (4 أرقام)",
        "pin_confirm":"تأكيد الرمز",
        "unlock":     "فتح",
        "pin_wrong":  "رمز PIN غير صحيح",
        "pin_nomatch":"الرموز غير متطابقة",
        "pin_invalid":"يجب أن يحتوي على 4 أرقام",
        "pin_set":    "تم تفعيل رمز PIN",
        "err_name":   "⚠  الاسم مطلوب.",
        "err_price":  "⚠  سعر غير صالح.",
        "err_qty":    "⚠  كمية غير صالحة.",
        "err_pick":   "⚠  اختر منتجاً أولاً.",
        "err_qty2":   "⚠  كمية غير صالحة (الحد الأدنى 1).",
        "err_stock":  "⚠  المخزون غير كافٍ ({n} متاح).",
        "units":      "وحدة",
        "saved":      "تم حفظ البيانات.",
        "loaded":     "تم استعادة البيانات.",
        "cat_all":    "جميع الفئات",
    },
}

CURRENCIES = {
    "USD ($)":   "$",
    "EUR (€)":   "€",
    "DZD (دج)":  "دج",
    "MAD (د.م)": "د.م",
    "GBP (£)":   "£",
    "SAR (ر.س)": "ر.س",
}

CATEGORIES = ["Général", "Électronique", "Vêtements",
               "Alimentation", "Cosmétique", "Autre"]

NAV_ICONS = ["📦", "💰", "📈", "🧾", "⚙"]


# ══════════════════════════════════════════════════════════════════════════════
#  PARAMÈTRES GLOBAUX
# ══════════════════════════════════════════════════════════════════════════════
class AppSettings:
    def __init__(self):
        self.lang          = "fr"
        self.currency      = "USD ($)"
        self.dark_mode     = True
        self.threshold     = 10
        self.pin_hash      = None
        self.categories    = list(CATEGORIES)

    @property
    def sym(self):
        return CURRENCIES.get(self.currency, "$")

    def t(self, key, **kw):
        txt = TR.get(self.lang, TR["fr"]).get(key, key)
        try:    return txt.format(**kw) if kw else txt
        except: return txt

    def toggle_theme(self):
        global _palette
        self.dark_mode = not self.dark_mode
        _palette = PALETTES["dark" if self.dark_mode else "light"]
        ctk.set_appearance_mode("dark" if self.dark_mode else "light")

    def set_pin(self, p):
        self.pin_hash = hashlib.sha256(p.encode()).hexdigest()

    def check_pin(self, p):
        if not self.pin_hash: return True
        return hashlib.sha256(p.encode()).hexdigest() == self.pin_hash

    def clear_pin(self):
        self.pin_hash = None


# ══════════════════════════════════════════════════════════════════════════════
#  BASE DE DONNÉES
# ══════════════════════════════════════════════════════════════════════════════
class Database:
    def __init__(self):
        self._nid = 5
        self._products = [
            {"id":1,"name":"Écouteurs Bluetooth","price":34.99,"qty":42,"cat":"Électronique"},
            {"id":2,"name":"Coque iPhone 15",    "price": 8.99,"qty":130,"cat":"Électronique"},
            {"id":3,"name":"Câble USB-C 2m",     "price": 6.49,"qty":7,  "cat":"Électronique"},
            {"id":4,"name":"Crème hydratante",   "price":12.50,"qty":55,  "cat":"Cosmétique"},
        ]
        self._sales = []

    # ── Produits ─────────────────────────────────────────────────────────────
    def products(self, cat=None, search="", sort="name"):
        ps = list(self._products)
        if cat and cat not in ("cat_all",):
            ps = [p for p in ps if p["cat"] == cat]
        if search:
            s = search.lower()
            ps = [p for p in ps if s in p["name"].lower()]
        key = {"name":"name","price":"price","qty":"qty"}.get(sort,"name")
        ps.sort(key=lambda p: p[key])
        return ps

    def add(self, name, price, qty, cat):
        p = {"id":self._nid,"name":name,"price":price,"qty":qty,"cat":cat}
        self._products.append(p); self._nid += 1; return p

    def update(self, pid, name, price, qty, cat):
        for p in self._products:
            if p["id"]==pid:
                p.update({"name":name,"price":price,"qty":qty,"cat":cat}); return True
        return False

    def restock(self, pid, add_qty):
        for p in self._products:
            if p["id"]==pid: p["qty"] += add_qty; return True
        return False

    def delete(self, pid):
        for i,p in enumerate(self._products):
            if p["id"]==pid: self._products.pop(i); return True
        return False

    def find(self, pid):
        for p in self._products:
            if p["id"]==pid: return p
        return None

    # ── Ventes ───────────────────────────────────────────────────────────────
    def sell(self, pid, qty, discount_pct=0):
        p = self.find(pid)
        if not p: return False, "notfound"
        if p["qty"] < qty: return False, str(p["qty"])
        p["qty"] -= qty
        gross = round(p["price"] * qty, 2)
        disc  = round(gross * discount_pct / 100, 2)
        total = round(gross - disc, 2)
        s = {"id":len(self._sales)+1, "pid":pid, "name":p["name"],
             "qty":qty, "gross":gross, "disc":disc, "total":total,
             "cat":p["cat"], "date":datetime.now().strftime("%Y-%m-%d %H:%M")}
        self._sales.append(s); return True, s

    def summary(self):
        return {
            "n":    len(self._sales),
            "units":sum(s["qty"]   for s in self._sales),
            "rev":  round(sum(s["total"] for s in self._sales),2),
        }

    def sales_by_day(self, days=7):
        result = {}
        today = datetime.now().date()
        for i in range(days):
            d = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            result[d] = 0
        for s in self._sales:
            d = s["date"][:10]
            if d in result: result[d] += s["total"]
        return dict(sorted(result.items()))

    def top_products(self, n=5):
        cnt = Counter()
        for s in self._sales: cnt[s["name"]] += s["qty"]
        return cnt.most_common(n)

    def low_stock(self, thr):
        return [p for p in self._products if p["qty"] < thr]

    def inventory_value(self):
        return round(sum(p["price"]*p["qty"] for p in self._products), 2)

    def filtered_sales(self, period="all"):
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        result = []
        for s in reversed(self._sales):
            d = datetime.strptime(s["date"][:10],"%Y-%m-%d").date()
            if period=="today" and d != today: continue
            if period=="week"  and d < week_start: continue
            result.append(s)
        return result

    def to_dict(self):
        return {"products":self._products,"sales":self._sales,"nid":self._nid}

    def from_dict(self, d):
        self._products = d.get("products",[])
        self._sales    = d.get("sales",[])
        self._nid      = d.get("nid",1)


# ══════════════════════════════════════════════════════════════════════════════
#  WIDGETS RÉUTILISABLES
# ══════════════════════════════════════════════════════════════════════════════
def F(parent, **kw):
    """Frame transparente."""
    kw.setdefault("fg_color","transparent")
    return ctk.CTkFrame(parent, **kw)

def Lbl(parent, text, size=14, bold=False, color=None, **kw):
    color = color or c("text")
    return ctk.CTkLabel(parent, text=text,
                        font=ctk.CTkFont(size=size, weight="bold" if bold else "normal"),
                        text_color=color, **kw)

def Entry(parent, **kw):
    kw.setdefault("height",     46)
    kw.setdefault("fg_color",   c("bg"))
    kw.setdefault("text_color", c("text"))
    kw.setdefault("border_color", c("border"))
    kw.setdefault("corner_radius", 10)
    return ctk.CTkEntry(parent, **kw)

def Btn(parent, text, mode="primary", icon="", w=None, h=50, cmd=None, **kw):
    STYLES = {
        "primary": (c("accent"),   c("accent_d"), "#FFFFFF"),
        "gold":    (c("gold"),     c("gold_d"),   "#FFFFFF"),
        "danger":  (c("danger"),   "#C8002F",     "#FFFFFF"),
        "neutral": (c("card2"),    c("sep"),       c("text")),
        "ghost":   ("transparent", c("card2"),     c("text")),
    }
    bg, hov, txt = STYLES.get(mode, STYLES["primary"])
    kw.setdefault("corner_radius", 12)
    kw.setdefault("font", ctk.CTkFont(size=14, weight="bold"))
    kw.setdefault("border_width", 1 if mode=="neutral" else 0)
    kw.setdefault("border_color", c("sep"))
    display = f"{icon}  {text}" if icon else text
    cfg = dict(text=display, fg_color=bg, hover_color=hov,
               text_color=txt, height=h, **kw)
    if w: cfg["width"] = w
    if cmd: cfg["command"] = cmd
    return ctk.CTkButton(parent, **cfg)

def Card(parent, **kw):
    kw.setdefault("fg_color",    c("card"))
    kw.setdefault("corner_radius", 14)
    kw.setdefault("border_width", 1)
    kw.setdefault("border_color", c("border"))
    return ctk.CTkFrame(parent, **kw)

def Sep(parent):
    return ctk.CTkFrame(parent, fg_color=c("sep"), height=1, corner_radius=0)

def OptionMenu(parent, values, cmd=None, w=None, **kw):
    kw.setdefault("fg_color",      c("card2"))
    kw.setdefault("button_color",  c("sep"))
    kw.setdefault("text_color",    c("text"))
    kw.setdefault("height",        44)
    kw.setdefault("corner_radius", 10)
    if w: kw["width"] = w
    if cmd: kw["command"] = cmd
    return ctk.CTkOptionMenu(parent, values=values, **kw)


# ══════════════════════════════════════════════════════════════════════════════
#  BARRE DE NAVIGATION INFÉRIEURE
# ══════════════════════════════════════════════════════════════════════════════
class BottomNav(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=c("nav"), height=68, corner_radius=0)
        self.pack_propagate(False)
        self.app = app
        self._btns = []
        self._badge = ctk.StringVar(value="")

        keys  = ["nav_stock","nav_sales","nav_dash","nav_hist","nav_settings"]
        views = ["StockView","SalesView","DashView","HistView","SettingsView"]

        for i, (key, view, icon) in enumerate(zip(keys, views, NAV_ICONS)):
            col = ctk.CTkFrame(self, fg_color="transparent")
            col.pack(side="left", expand=True, fill="both")
            
            icon_lbl = ctk.CTkLabel(col, text=icon,
                                     font=ctk.CTkFont(size=22))
            icon_lbl.pack(pady=(8,0))
            
            txt_lbl = ctk.CTkLabel(col, text=app.s.t(key),
                                    font=ctk.CTkFont(size=10),
                                    text_color=c("text2"))
            txt_lbl.pack(pady=(0,2))
            
            col.bind("<Button-1>", lambda e, v=view: app.show(v))
            icon_lbl.bind("<Button-1>", lambda e, v=view: app.show(v))
            txt_lbl.bind("<Button-1>",  lambda e, v=view: app.show(v))
            
            self._btns.append((col, icon_lbl, txt_lbl, view, key))

    def set_active(self, view_name):
        for col, icon_lbl, txt_lbl, v, key in self._btns:
            is_active = v == view_name
            icon_lbl.configure(text_color=c("accent") if is_active else c("text2"))
            txt_lbl.configure(text_color=c("accent") if is_active else c("text2"),
                              font=ctk.CTkFont(size=10,
                                               weight="bold" if is_active else "normal"))

    def refresh_labels(self):
        keys = ["nav_stock","nav_sales","nav_dash","nav_hist","nav_settings"]
        for (col, icon_lbl, txt_lbl, v, key), k in zip(self._btns, keys):
            txt_lbl.configure(text=self.app.s.t(k))


# ══════════════════════════════════════════════════════════════════════════════
#  HEADER BAR
# ══════════════════════════════════════════════════════════════════════════════
class HeaderBar(ctk.CTkFrame):
    def __init__(self, parent, title, app,
                 show_back=False, back_view="MainMenu",
                 show_theme=False):
        super().__init__(parent, fg_color=c("card"), height=62, corner_radius=0)
        self.pack_propagate(False)

        if show_back:
            Btn(self, text="← Retour", mode="ghost", h=42, w=115,
                cmd=lambda: app.show(back_view)
                ).pack(side="left", padx=10, pady=10)

        Lbl(self, title, size=18, bold=True).pack(
            side="left", padx=(16 if not show_back else 4), pady=10)

        if show_theme:
            Btn(self, text="🌓", mode="ghost", h=42, w=48,
                cmd=lambda: (app.s.toggle_theme(), app.rebuild())
                ).pack(side="right", padx=10, pady=10)


# ══════════════════════════════════════════════════════════════════════════════
#  APPLICATION PRINCIPALE
# ══════════════════════════════════════════════════════════════════════════════
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.s  = AppSettings()
        self.db = Database()

        self.title("StoreManager")
        self.geometry("420x760")
        self.resizable(False, False)
        self.configure(fg_color=c("bg"))
        self._build()

    def _build(self):
        # Conteneur principal
        self._main = ctk.CTkFrame(self, fg_color=c("bg"), corner_radius=0)
        self._main.pack(fill="both", expand=True)
        self._main.grid_rowconfigure(0, weight=1)
        self._main.grid_columnconfigure(0, weight=1)

        # Vues
        self._views = {}
        for Cls in (StockView, SalesView, DashView, HistView, SettingsView):
            v = Cls(self._main, self)
            self._views[Cls.__name__] = v
            v.grid(row=0, column=0, sticky="nsew")

        # Barre de navigation inférieure
        self._nav = BottomNav(self._main, self)
        self._nav.grid(row=1, column=0, sticky="ew")

        # Afficher la vue par défaut
        if self.s.pin_hash:
            self._show_pin_lock()
        else:
            self.show("StockView")

    def show(self, name):
        v = self._views.get(name)
        if not v: return
        v.tkraise()
        self._nav.set_active(name)
        if hasattr(v, "refresh"): v.refresh()

    def rebuild(self):
        """Reconstruit tout l'UI après changement de thème ou langue."""
        self.configure(fg_color=c("bg"))
        for w in self.winfo_children(): w.destroy()
        self._build()

    def _show_pin_lock(self):
        s = self.s
        dlg = ctk.CTkToplevel(self)
        dlg.title(s.t("pin_enter"))
        dlg.geometry("340x240")
        dlg.configure(fg_color=c("card"))
        dlg.grab_set()
        dlg.protocol("WM_DELETE_WINDOW", self.destroy)

        Lbl(dlg, "🔒  " + s.t("pin_enter"), size=16, bold=True
            ).pack(pady=(26,10), padx=24, anchor="w")
        inp = Entry(dlg, show="●"); inp.pack(fill="x", padx=24, pady=4)
        err = Lbl(dlg, "", size=13, color=c("danger")); err.pack(pady=4)

        def check():
            if s.check_pin(inp.get()): dlg.destroy(); self.show("StockView")
            else: err.configure(text=s.t("pin_wrong")); inp.delete(0,"end")

        Btn(dlg, text=s.t("unlock"), cmd=check).pack(fill="x", padx=24, pady=12)
        inp.bind("<Return>", lambda e: check())


# ══════════════════════════════════════════════════════════════════════════════
#  VUE – STOCK
# ══════════════════════════════════════════════════════════════════════════════
class StockView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=c("bg"), corner_radius=0)
        self.app  = app
        self.db   = app.db
        self._sort = "name"
        self._cat  = None
        self._q    = ""

    def refresh(self):
        for w in self.winfo_children(): w.destroy()
        s = self.app.s

        HeaderBar(self, s.t("stock_title"), self.app, show_theme=True).pack(fill="x")

        # Barre recherche + tri
        ctrl = F(self); ctrl.pack(fill="x", padx=14, pady=8)

        self._search_var = ctk.StringVar(value=self._q)
        srch = ctk.CTkEntry(ctrl, textvariable=self._search_var,
                             placeholder_text=s.t("search_ph"),
                             height=42, fg_color=c("card2"),
                             text_color=c("text"), border_color=c("border"),
                             corner_radius=10)
        srch.pack(side="left", fill="x", expand=True, padx=(0,8))
        srch.bind("<KeyRelease>", self._on_search)

        sort_var = ctk.StringVar(value=s.t(f"sort_{self._sort}"))
        sort_vals = [s.t("sort_name"), s.t("sort_price"), s.t("sort_qty")]
        om = OptionMenu(ctrl, sort_vals, cmd=self._on_sort, w=140)
        om.set(sort_var.get()); om.pack(side="right")

        # Catégorie + bouton ajouter
        row2 = F(self); row2.pack(fill="x", padx=14, pady=(0,8))
        cats = [s.t("cat_all")] + s.categories
        self._cat_var = ctk.StringVar(value=cats[0] if not self._cat else self._cat)
        cm = OptionMenu(row2, cats, cmd=self._on_cat, w=190)
        cm.set(self._cat_var.get()); cm.pack(side="left")
        Btn(row2, text=s.t("add"), icon="📦", h=44,
            cmd=self._add_dlg).pack(side="right")

        # Headers
        hdr = Card(self, corner_radius=8, border_width=0,
                   fg_color=c("bg_alt"), height=36)
        hdr.pack(fill="x", padx=14)
        hdr.pack_propagate(False)
        for txt, w in [(s.t("col_name"),170),(s.t("col_price"),80),
                       (s.t("col_qty"),55),("",90)]:
            Lbl(hdr, txt, size=12, bold=True, color=c("text2"),
                anchor="w", width=w).pack(side="left", padx=6)

        # Liste scrollable
        self._scroll = ctk.CTkScrollableFrame(self, fg_color=c("bg"),
                                               corner_radius=0)
        self._scroll.pack(fill="both", expand=True, padx=10)
        self._draw_list()

    def _draw_list(self):
        for w in self._scroll.winfo_children(): w.destroy()
        s    = self.app.s
        cat  = self._cat if self._cat and self._cat != s.t("cat_all") else None
        prods = self.db.products(cat=cat, search=self._q, sort=self._sort)

        if not prods:
            Lbl(self._scroll, s.t("no_products"), size=14,
                color=c("text2")).pack(pady=36)
            return

        for p in prods:
            row = Card(self._scroll, height=58)
            row.pack(fill="x", pady=3)
            row.pack_propagate(False)

            Lbl(row, p["name"], size=13, bold=True,
                anchor="w", width=170).pack(side="left", padx=10)
            Lbl(row, f"{s.sym}{p['price']:.2f}", size=13,
                color=c("gold"), anchor="w", width=80).pack(side="left")
            qty_c = c("danger") if p["qty"] < s.threshold else c("success")
            Lbl(row, str(p["qty"]), size=14, bold=True,
                color=qty_c, anchor="w", width=55).pack(side="left")

            ctk.CTkButton(row, text="+", width=36, height=36,
                          fg_color=c("sep"), hover_color=c("success"),
                          text_color=c("success"), font=ctk.CTkFont(size=18, weight="bold"),
                          command=lambda pr=p: self._restock_dlg(pr)
                          ).pack(side="left", padx=2)
            ctk.CTkButton(row, text="✎", width=36, height=36,
                          fg_color=c("sep"), hover_color=c("accent"),
                          text_color=c("accent"), font=ctk.CTkFont(size=15),
                          command=lambda pr=p: self._edit_dlg(pr)
                          ).pack(side="left", padx=2)
            ctk.CTkButton(row, text="✕", width=36, height=36,
                          fg_color=c("sep"), hover_color=c("danger"),
                          text_color=c("danger"), font=ctk.CTkFont(size=14),
                          command=lambda pr=p: self._del_confirm(pr)
                          ).pack(side="left", padx=2)

    def _on_search(self, e=None):
        self._q = self._search_var.get(); self._draw_list()

    def _on_sort(self, val):
        m = {self.app.s.t("sort_name"):"name",
             self.app.s.t("sort_price"):"price",
             self.app.s.t("sort_qty"):"qty"}
        self._sort = m.get(val,"name"); self._draw_list()

    def _on_cat(self, val):
        self._cat = val; self._draw_list()

    def _add_dlg(self):
        ProductDlg(self, self.app,
                   on_save=lambda n,p,q,cat: (self.db.add(n,p,q,cat), self._draw_list()))

    def _edit_dlg(self, pr):
        ProductDlg(self, self.app, product=pr,
                   on_save=lambda n,p,q,cat: (
                       self.db.update(pr["id"],n,p,q,cat), self._draw_list()))

    def _restock_dlg(self, pr):
        s = self.app.s
        dlg = ctk.CTkToplevel(self)
        dlg.title(s.t("restock")); dlg.geometry("320x200")
        dlg.configure(fg_color=c("card")); dlg.grab_set()

        Lbl(dlg, f"📦  {pr['name']}", size=15, bold=True
            ).pack(pady=(20,6), padx=20, anchor="w")
        Lbl(dlg, s.t("restock_qty"), size=13, color=c("text2")
            ).pack(padx=20, anchor="w")
        inp = Entry(dlg); inp.insert(0,"10"); inp.pack(fill="x", padx=20, pady=8)

        def ok():
            try:
                n = int(inp.get())
                if n<=0: raise ValueError
            except: return
            self.db.restock(pr["id"], n)
            dlg.destroy(); self._draw_list()

        Btn(dlg, text=s.t("save"), icon="✓", cmd=ok).pack(fill="x", padx=20, pady=8)

    def _del_confirm(self, pr):
        s = self.app.s
        ok = messagebox.askyesno(
            s.t("confirm_del", n=pr["name"]), s.t("irreversible"))
        if ok: self.db.delete(pr["id"]); self._draw_list()


# ══════════════════════════════════════════════════════════════════════════════
#  DIALOG – FORMULAIRE PRODUIT
# ══════════════════════════════════════════════════════════════════════════════
class ProductDlg(ctk.CTkToplevel):
    def __init__(self, parent, app, on_save, product=None):
        super().__init__(parent)
        s = app.s
        is_edit = product is not None
        self.title(s.t("edit_product" if is_edit else "add_product"))
        self.geometry("380x440")
        self.resizable(False, False)
        self.configure(fg_color=c("card"))
        self.grab_set()
        self._save_cb = on_save
        self._pr = product
        self._app = app

        pad = {"padx": 22, "pady": 5}
        inputs = [("name_lbl","_n",None), ("price_lbl","_p",None),
                  ("qty_lbl","_q",None)]

        for lk, attr, _ in inputs:
            Lbl(self, s.t(lk), size=13, color=c("text2"),
                anchor="w").pack(fill="x", **pad)
            e = Entry(self)
            e.pack(fill="x", **pad)
            setattr(self, attr, e)
            if product:
                val = product.get({"_n":"name","_p":"price","_q":"qty"}[attr],"")
                e.insert(0, str(val))

        Lbl(self, s.t("cat_lbl"), size=13, color=c("text2"),
            anchor="w").pack(fill="x", **pad)
        self._cat = ctk.StringVar(
            value=product.get("cat", s.categories[0]) if product else s.categories[0])
        OptionMenu(self, s.categories, w=None).pack(fill="x", **pad)
        # re-create with variable
        for w in self.winfo_children():
            if isinstance(w, ctk.CTkOptionMenu): w.destroy()
        om = ctk.CTkOptionMenu(self, values=s.categories, variable=self._cat,
                               fg_color=c("card2"), button_color=c("sep"),
                               text_color=c("text"), height=44, corner_radius=10)
        om.pack(fill="x", **pad)

        self._err = Lbl(self, "", size=13, color=c("danger"))
        self._err.pack(pady=4)

        brow = F(self); brow.pack(fill="x", padx=22, pady=10)
        if is_edit:
            Btn(brow, text=s.t("delete"), mode="danger",
                cmd=self._delete).pack(side="left", expand=True, padx=(0,4))
        Btn(brow, text=s.t("cancel"), mode="neutral",
            cmd=self.destroy).pack(side="left", expand=True, padx=(0,4))
        Btn(brow, text=s.t("save"),
            cmd=self._save).pack(side="left", expand=True)

    def _save(self):
        name = self._n.get().strip()
        if not name: self._err.configure(text=self._app.s.t("err_name")); return
        try:
            p = round(float(self._p.get()), 2)
            if p < 0: raise ValueError
        except: self._err.configure(text=self._app.s.t("err_price")); return
        try:
            q = int(self._q.get())
            if q < 0: raise ValueError
        except: self._err.configure(text=self._app.s.t("err_qty")); return

        self._save_cb(name, p, q, self._cat.get())
        self.destroy()

    def _delete(self):
        if self._pr:
            s = self._app.s
            if messagebox.askyesno(s.t("confirm_del",n=self._pr["name"]),
                                   s.t("irreversible")):
                self._app.db.delete(self._pr["id"])
                self.destroy()
                # refresh stock view
                sv = self._app._views.get("StockView")
                if sv: sv._draw_list()


# ══════════════════════════════════════════════════════════════════════════════
#  VUE – VENTES
# ══════════════════════════════════════════════════════════════════════════════
class SalesView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=c("bg"), corner_radius=0)
        self.app = app
        self.db  = app.db
        self._sel = None

    def refresh(self):
        for w in self.winfo_children(): w.destroy()
        s = self.app.s

        HeaderBar(self, s.t("sales_title"), self.app).pack(fill="x")

        body = ctk.CTkScrollableFrame(self, fg_color=c("bg"), corner_radius=0)
        body.pack(fill="both", expand=True, padx=16, pady=10)

        # Résumé
        sm = self.db.summary()
        sum_card = Card(body); sum_card.pack(fill="x", pady=(0,16))
        inner = F(sum_card); inner.pack(fill="x", padx=16, pady=14)
        inner.columnconfigure((0,1,2), weight=1)

        for i,(lbl,val,col) in enumerate([
            (s.t("trans"),    str(sm["n"]),           c("accent")),
            (s.t("units_sold"),str(sm["units"]),       c("gold")),
            (f"{s.t('revenue')}",f"{s.sym}{sm['rev']:.2f}", c("success")),
        ]):
            cell = F(inner); cell.grid(row=0, column=i, padx=6, sticky="nsew")
            Lbl(cell, val,  size=20, bold=True, color=col).pack()
            Lbl(cell, lbl,  size=11, color=c("text2")).pack()

        Sep(body).pack(fill="x", pady=8)

        # Produit sélectionné
        Lbl(body, s.t("pick_product"), size=13, bold=True,
            color=c("text2"), anchor="w").pack(anchor="w", pady=(4,6))

        sel_card = Card(body, height=58)
        sel_card.pack(fill="x", pady=(0,8))
        sel_card.pack_propagate(False)
        self._sel_lbl = Lbl(sel_card, s.t("no_selected"),
                             size=14, color=c("text2"))
        self._sel_lbl.place(relx=0.5, rely=0.5, anchor="center")

        Btn(body, text=s.t("pick_product"), icon="🛍",
            mode="neutral", h=48,
            cmd=self._pick_dlg).pack(fill="x", pady=4)

        Sep(body).pack(fill="x", pady=10)

        # Quantité & Remise côte à côte
        row2 = F(body); row2.pack(fill="x", pady=4)
        c1 = F(row2); c1.pack(side="left", expand=True, padx=(0,6))
        c2 = F(row2); c2.pack(side="right", expand=True, padx=(6,0))

        Lbl(c1, s.t("qty_sell"), size=13, color=c("text2"),
            anchor="w").pack(anchor="w")
        self._qty = Entry(c1, placeholder_text="1"); self._qty.pack(fill="x", pady=4)

        Lbl(c2, s.t("discount"), size=13, color=c("text2"),
            anchor="w").pack(anchor="w")
        self._disc = Entry(c2, placeholder_text="0"); self._disc.pack(fill="x", pady=4)

        # Bouton confirmer
        Btn(body, text=s.t("confirm_sale"), icon="✓", h=58,
            cmd=self._sell).pack(fill="x", pady=14)

        self._fb = Lbl(body, "", size=14); self._fb.pack(pady=4)

        # Historique rapide (3 dernières ventes)
        recent = self.db.filtered_sales("all")[:3]
        if recent:
            Sep(body).pack(fill="x", pady=8)
            Lbl(body, "Dernières ventes", size=13, bold=True,
                color=c("text2"), anchor="w").pack(anchor="w", pady=(0,6))
            for sl in recent:
                r = Card(body, height=46); r.pack(fill="x", pady=2)
                r.pack_propagate(False)
                Lbl(r, sl["name"], size=12, anchor="w"
                    ).pack(side="left", padx=10)
                Lbl(r, f"{s.sym}{sl['total']:.2f}", size=12,
                    bold=True, color=c("gold"), anchor="e"
                    ).pack(side="right", padx=10)
                Lbl(r, sl["date"][-5:], size=11, color=c("text2")
                    ).pack(side="right", padx=6)

    def _pick_dlg(self):
        s = self.app.s
        prods = self.db.products()
        if not prods: return

        dlg = ctk.CTkToplevel(self)
        dlg.title(s.t("pick_product"))
        dlg.geometry("380x480")
        dlg.configure(fg_color=c("card"))
        dlg.grab_set()

        srch_var = ctk.StringVar()
        srch = ctk.CTkEntry(dlg, textvariable=srch_var,
                             placeholder_text=s.t("search_ph"),
                             height=44, fg_color=c("bg"),
                             text_color=c("text"), border_color=c("border"),
                             corner_radius=10)
        srch.pack(fill="x", padx=12, pady=10)

        scroll = ctk.CTkScrollableFrame(dlg, fg_color=c("card"))
        scroll.pack(fill="both", expand=True, padx=10, pady=(0,10))

        def draw(q=""):
            for w in scroll.winfo_children(): w.destroy()
            for p in self.db.products(search=q):
                qty_c = c("danger") if p["qty"]<s.threshold else c("success")
                r = Card(scroll, height=54)
                r.pack(fill="x", pady=3)
                r.pack_propagate(False)
                Lbl(r, p["name"], size=13, bold=True,
                    anchor="w").pack(side="left", padx=10)
                Lbl(r, f"{s.sym}{p['price']:.2f}", size=12,
                    color=c("gold"), anchor="w").pack(side="left", padx=6)
                Lbl(r, str(p["qty"]), size=12,
                    color=qty_c, anchor="e").pack(side="right", padx=16)
                r.bind("<Button-1>", lambda e, pr=p: (
                    self._select(pr), dlg.destroy()))

        draw()
        srch.bind("<KeyRelease>", lambda e: draw(srch_var.get()))

    def _select(self, p):
        self._sel = p
        self._sel_lbl.configure(
            text=f"✓  {p['name']}   {self.app.s.sym}{p['price']:.2f}",
            text_color=c("success"))

    def _sell(self):
        s = self.app.s
        if not self._sel:
            self._show_fb(s.t("err_pick"), True); return
        try:
            qty = int(self._qty.get() or "1")
            if qty <= 0: raise ValueError
        except: self._show_fb(s.t("err_qty2"), True); return
        try:
            disc = float(self._disc.get() or "0")
            disc = max(0, min(100, disc))
        except: disc = 0

        ok, res = self.db.sell(self._sel["id"], qty, disc)
        if ok:
            msg = s.t("sale_ok", q=res["qty"], n=res["name"],
                       cur=s.sym, t=res["total"])
            if disc > 0: msg += f"  (remise {disc:.0f}%)"
            self._show_fb(msg, False)
            self._sel = None
            self._sel_lbl.configure(text=s.t("no_selected"), text_color=c("text2"))
            self._qty.delete(0,"end")
            self._disc.delete(0,"end")
            self.after(100, lambda: self.refresh())
        else:
            self._show_fb(s.t("err_stock", n=res), True)

    def _show_fb(self, msg, err):
        self._fb.configure(text=msg,
                           text_color=c("danger") if err else c("success"))
        self.after(4000, lambda: self._fb.configure(text=""))


# ══════════════════════════════════════════════════════════════════════════════
#  VUE – TABLEAU DE BORD
# ══════════════════════════════════════════════════════════════════════════════
class DashView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=c("bg"), corner_radius=0)
        self.app = app
        self.db  = app.db

    def refresh(self):
        for w in self.winfo_children(): w.destroy()
        s  = self.app.s
        db = self.db

        HeaderBar(self, s.t("dash_title"), self.app).pack(fill="x")

        scroll = ctk.CTkScrollableFrame(self, fg_color=c("bg"), corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=14, pady=10)

        sm  = db.summary()
        low = db.low_stock(s.threshold)
        inv = db.inventory_value()

        # KPI row
        kpi = F(scroll); kpi.pack(fill="x", pady=(0,14))
        kpi.columnconfigure((0,1,2,3), weight=1)
        kpis = [
            (str(sm["n"]),     s.t("trans"),        c("accent"),  "📋"),
            (str(sm["units"]), s.t("units_sold"),   c("gold"),    "📦"),
            (f"{s.sym}{sm['rev']:.0f}", s.t("revenue"), c("success"), "💵"),
            (f"{s.sym}{inv:.0f}", s.t("inventory_val"), c("text2"), "🏪"),
        ]
        for i,(val,lbl,col,icon) in enumerate(kpis):
            cell = Card(kpi)
            cell.grid(row=0, column=i, padx=4, pady=4, sticky="nsew")
            Lbl(cell, icon, size=18).pack(pady=(10,2))
            Lbl(cell, val,  size=18, bold=True, color=col).pack()
            Lbl(cell, lbl,  size=10, color=c("text2")).pack(pady=(0,10))

        # Graphique barres 7 jours
        Lbl(scroll, s.t("chart_title"), size=14, bold=True,
            color=c("text"), anchor="w").pack(anchor="w", pady=(8,6))
        chart_card = Card(scroll, height=170)
        chart_card.pack(fill="x", pady=(0,14))
        self._draw_chart(chart_card, db.sales_by_day(7))

        # Top 5 produits
        Lbl(scroll, s.t("top5"), size=14, bold=True,
            color=c("text"), anchor="w").pack(anchor="w", pady=(8,6))
        top = db.top_products(5)
        if not top:
            Lbl(scroll, s.t("no_data"), size=13, color=c("text2")).pack(anchor="w")
        else:
            max_qty = max(q for _,q in top) if top else 1
            for rank,(name,qty) in enumerate(top,1):
                row = Card(scroll, height=52)
                row.pack(fill="x", pady=3)
                row.pack_propagate(False)
                # badge couleur selon rang
                badge_c = [c("gold"),c("text2"),c("text2"),c("text2"),c("text2")][rank-1]
                Lbl(row, f"#{rank}", size=14, bold=True, color=badge_c,
                    width=36).pack(side="left", padx=8)
                inner = F(row); inner.pack(side="left", fill="both", expand=True, pady=6)
                Lbl(inner, name, size=13, bold=True, anchor="w").pack(anchor="w")
                # mini barre de progression
                bar_w = max(int(170 * qty / max_qty), 6)
                prog = ctk.CTkFrame(inner, fg_color=c("accent"),
                                    height=4, corner_radius=2, width=bar_w)
                prog.pack(anchor="w")
                Lbl(row, f"{qty} {s.t('units')}", size=13,
                    color=c("gold"), bold=True).pack(side="right", padx=14)

        # Alertes stock
        Lbl(scroll, s.t("stock_alerts"), size=14, bold=True,
            color=c("text"), anchor="w").pack(anchor="w", pady=(16,6))
        if not low:
            r = Card(scroll, height=46); r.pack(fill="x", pady=3)
            r.pack_propagate(False)
            Lbl(r, s.t("stock_ok"), size=13, color=c("success")
                ).place(relx=0.5, rely=0.5, anchor="center")
        else:
            for p in low:
                row = Card(scroll, height=50, fg_color=c("card2"))
                row.pack(fill="x", pady=3)
                row.pack_propagate(False)
                Lbl(row, "⚠", size=18, color=c("danger"), width=40
                    ).pack(side="left", padx=8)
                Lbl(row, p["name"], size=13, bold=True
                    ).pack(side="left", expand=True, padx=4)
                Lbl(row, f"{p['qty']} {s.t('units')}", size=13,
                    bold=True, color=c("danger")).pack(side="right", padx=12)

    def _draw_chart(self, parent, data):
        """Graphique en barres dessiné avec tkinter Canvas."""
        canvas = Canvas(parent, bg=_palette["card"], highlightthickness=0,
                        height=160, relief="flat")
        canvas.pack(fill="both", expand=True, padx=12, pady=8)
        
        parent.update_idletasks()
        W = canvas.winfo_width() or 370
        H = 140
        
        if not data or all(v==0 for v in data.values()):
            canvas.create_text(W//2, H//2, text=self.app.s.t("no_data"),
                               fill=_palette["text2"], font=("Arial",12))
            return

        items = list(data.items())
        max_v = max(v for _,v in items) or 1
        n     = len(items)
        gap   = 8
        bar_w = (W - (n+1)*gap) // n
        colors = [_palette["accent"], _palette["gold"]]

        for i, (date, val) in enumerate(items):
            x1 = gap + i*(bar_w+gap)
            x2 = x1 + bar_w
            bh = int((val / max_v) * (H - 30))
            y2 = H - 20
            y1 = y2 - bh

            # Barre dégradée (simulated)
            canvas.create_rectangle(x1, y1, x2, y2,
                                     fill=colors[i%2],
                                     outline="", width=0)
            if val > 0:
                canvas.create_text((x1+x2)//2, y1-8,
                                    text=f"{self.app.s.sym}{val:.0f}",
                                    fill=_palette["text"], font=("Arial",9))
            # Label date court
            canvas.create_text((x1+x2)//2, H-8,
                                 text=date[-5:],
                                 fill=_palette["text2"], font=("Arial",8))


# ══════════════════════════════════════════════════════════════════════════════
#  VUE – HISTORIQUE
# ══════════════════════════════════════════════════════════════════════════════
class HistView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=c("bg"), corner_radius=0)
        self.app    = app
        self.db     = app.db
        self._period = "all"

    def refresh(self):
        for w in self.winfo_children(): w.destroy()
        s = self.app.s

        HeaderBar(self, s.t("hist_title"), self.app).pack(fill="x")

        # Filtres + export
        ctrl = F(self); ctrl.pack(fill="x", padx=14, pady=8)

        filters = [("all","filter_all"),("today","filter_today"),("week","filter_week")]
        for period, key in filters:
            active = (period == self._period)
            b = ctk.CTkButton(ctrl, text=s.t(key), width=110, height=38,
                              fg_color=c("accent") if active else c("card2"),
                              hover_color=c("accent_d"),
                              text_color="#FFFFFF" if active else c("text"),
                              font=ctk.CTkFont(size=13, weight="bold"),
                              corner_radius=10,
                              command=lambda p=period: self._set_period(p))
            b.pack(side="left", padx=3)

        Btn(ctrl, text=s.t("export_csv"), icon="📥", mode="gold",
            h=38, w=136, cmd=self._export).pack(side="right")

        # Headers
        hdr = Card(self, fg_color=c("bg_alt"), corner_radius=8,
                   border_width=0, height=34)
        hdr.pack(fill="x", padx=14, pady=(4,0))
        hdr.pack_propagate(False)
        for txt, w in [(s.t("col_name"),150),(s.t("col_qty"),46),
                       (s.t("total_col"),80),(s.t("date_col"),105)]:
            Lbl(hdr, txt, size=11, bold=True, color=c("text2"),
                anchor="w", width=w).pack(side="left", padx=6)

        # Liste
        scroll = ctk.CTkScrollableFrame(self, fg_color=c("bg"),
                                         corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=10)

        sales = self.db.filtered_sales(self._period)
        if not sales:
            Lbl(scroll, s.t("no_sales"), size=14, color=c("text2")
                ).pack(pady=40)
            return

        for sl in sales:
            row = Card(scroll, height=50); row.pack(fill="x", pady=3)
            row.pack_propagate(False)
            Lbl(row, sl["name"], size=12, bold=True,
                anchor="w", width=150).pack(side="left", padx=8)
            Lbl(row, f"×{sl['qty']}", size=12, color=c("accent2"),
                width=46, anchor="w").pack(side="left")
            Lbl(row, f"{s.sym}{sl['total']:.2f}", size=13, bold=True,
                color=c("gold"), width=80, anchor="w").pack(side="left")
            Lbl(row, sl["date"][-11:], size=10, color=c("text2"),
                width=105).pack(side="left")
            if sl.get("disc",0) > 0:
                Lbl(row, f"-{sl['disc']:.2f}", size=10,
                    color=c("success")).pack(side="right", padx=8)

    def _set_period(self, p):
        self._period = p; self.refresh()

    def _export(self):
        s = self.app.s
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV","*.csv")],
            initialfile=f"ventes_{datetime.now().strftime('%Y%m%d')}.csv")
        if not path: return
        with open(path,"w",newline="",encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["name","qty","gross","disc","total","date","cat"])
            writer.writeheader()
            writer.writerows(self.db._sales)
        messagebox.showinfo("Export CSV", s.t("saved"))


# ══════════════════════════════════════════════════════════════════════════════
#  VUE – PARAMÈTRES
# ══════════════════════════════════════════════════════════════════════════════
class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=c("bg"), corner_radius=0)
        self.app = app

    def refresh(self):
        for w in self.winfo_children(): w.destroy()
        s = self.app.s

        HeaderBar(self, s.t("settings_title"), self.app).pack(fill="x")

        sc = ctk.CTkScrollableFrame(self, fg_color=c("bg"), corner_radius=0)
        sc.pack(fill="both", expand=True, padx=16, pady=10)

        def row_card(parent, label):
            r = Card(parent, height=62); r.pack(fill="x", pady=5)
            r.pack_propagate(False)
            Lbl(r, label, size=15, anchor="w").pack(side="left", padx=16)
            return r

        # Thème
        r = row_card(sc, s.t("theme"))
        sw = ctk.CTkSwitch(r,
            text=s.t("dark") if s.dark_mode else s.t("light"),
            command=lambda: (s.toggle_theme(), self.app.rebuild()),
            fg_color=c("accent"), progress_color=c("accent_d"),
            font=ctk.CTkFont(size=13), text_color=c("text2"))
        if s.dark_mode: sw.select()
        else:           sw.deselect()
        sw.pack(side="right", padx=16)

        # Langue
        r = row_card(sc, s.t("lang"))
        lang_vals = ["fr – Français","en – English","ar – العربية"]
        lang_map  = {"fr":"fr – Français","en":"en – English","ar":"ar – العربية"}
        lm = OptionMenu(r, lang_vals, cmd=self._change_lang, w=190)
        lm.set(lang_map.get(s.lang, "fr – Français"))
        lm.pack(side="right", padx=16)

        # Devise
        r = row_card(sc, s.t("currency"))
        cm = OptionMenu(r, list(CURRENCIES.keys()),
                         cmd=lambda v: setattr(s,"currency",v), w=150)
        cm.set(s.currency); cm.pack(side="right", padx=16)

        # Seuil
        r = row_card(sc, s.t("threshold"))
        bf = F(r); bf.pack(side="right", padx=16)
        self._thr = Entry(bf, width=68, height=40); self._thr.insert(0, str(s.threshold))
        self._thr.pack(side="left", padx=(0,6))
        Btn(bf, text="✓", w=40, h=40, cmd=self._save_thr).pack(side="left")

        Sep(sc).pack(fill="x", pady=12)

        # PIN
        Lbl(sc, s.t("pin"), size=13, bold=True, color=c("text2"),
            anchor="w").pack(anchor="w", pady=(0,6))
        pin_row = F(sc); pin_row.pack(fill="x", pady=4)
        Lbl(pin_row, s.t("pin_active") if s.pin_hash else s.t("pin_off"),
            size=14, color=c("accent") if s.pin_hash else c("text2")
            ).pack(side="left")
        Btn(pin_row, text=s.t("change"), mode="neutral",
            w=110, h=40, cmd=self._set_pin).pack(side="right")
        if s.pin_hash:
            Btn(pin_row, text=s.t("remove"), mode="danger",
                w=100, h=40, cmd=self._rm_pin).pack(side="right", padx=(0,8))

        Sep(sc).pack(fill="x", pady=12)

        # Backup
        Lbl(sc, s.t("backup"), size=13, bold=True, color=c("text2"),
            anchor="w").pack(anchor="w", pady=(0,6))
        brow = F(sc); brow.pack(fill="x", pady=4)
        Btn(brow, text=s.t("save_btn"), icon="💾",
            h=50, cmd=self._save_json).pack(side="left", expand=True, padx=(0,6))
        Btn(brow, text=s.t("load_btn"), icon="📂",
            mode="neutral", h=50, cmd=self._load_json).pack(side="left", expand=True)

        Sep(sc).pack(fill="x", pady=12)

        # Version
        Lbl(sc, "StoreManager v4.0", size=14, bold=True,
            color=c("text2")).pack(pady=(4,2))
        Lbl(sc, "Built with CustomTkinter  •  Python",
            size=11, color=c("sep")).pack()

    def _change_lang(self, v):
        self.app.s.lang = v.split(" – ")[0].strip()
        self.app.rebuild()

    def _save_thr(self):
        try:
            v = int(self._thr.get())
            if v >= 0: self.app.s.threshold = v
        except: pass

    def _set_pin(self):
        s = self.app.s
        dlg = ctk.CTkToplevel(self)
        dlg.title(s.t("pin")); dlg.geometry("340x290")
        dlg.configure(fg_color=c("card")); dlg.grab_set()

        Lbl(dlg, s.t("pin_new"), size=14, bold=True
            ).pack(pady=(22,6), padx=22, anchor="w")
        e1 = Entry(dlg, show="●"); e1.pack(fill="x", padx=22, pady=4)
        Lbl(dlg, s.t("pin_confirm"), size=14, bold=True
            ).pack(pady=(10,6), padx=22, anchor="w")
        e2 = Entry(dlg, show="●"); e2.pack(fill="x", padx=22, pady=4)
        err = Lbl(dlg, "", size=13, color=c("danger")); err.pack(pady=4)

        def ok():
            p1,p2 = e1.get(), e2.get()
            if not p1.isdigit() or len(p1)!=4:
                err.configure(text=s.t("pin_invalid")); return
            if p1!=p2:
                err.configure(text=s.t("pin_nomatch")); return
            s.set_pin(p1); dlg.destroy()
            messagebox.showinfo("PIN", s.t("pin_set"))
            self.refresh()

        Btn(dlg, text=s.t("save"), icon="✓", cmd=ok
            ).pack(fill="x", padx=22, pady=10)

    def _rm_pin(self):
        self.app.s.clear_pin(); self.refresh()

    def _save_json(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON","*.json")],
            initialfile="storemanager_backup.json")
        if not path: return
        with open(path,"w",encoding="utf-8") as f:
            json.dump(self.app.db.to_dict(), f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Sauvegarde", self.app.s.t("saved"))

    def _load_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON","*.json")])
        if not path: return
        with open(path,"r",encoding="utf-8") as f:
            self.app.db.from_dict(json.load(f))
        messagebox.showinfo("Restauration", self.app.s.t("loaded"))


# ══════════════════════════════════════════════════════════════════════════════
#  POINT D'ENTRÉE
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = App()
    app.mainloop()
