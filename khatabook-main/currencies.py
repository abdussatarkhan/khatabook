# ISO 4217 code -> (symbol, display name, JS locale used for number formatting)
# Covers the currencies of the countries Khatabook-style ledger apps are most
# commonly used in, plus the other major world currencies.
CURRENCIES = {
    "INR": ("₹", "Indian Rupee", "en-IN"),
    "PKR": ("₨", "Pakistani Rupee", "en-PK"),
    "BDT": ("৳", "Bangladeshi Taka", "en-BD"),
    "LKR": ("₨", "Sri Lankan Rupee", "en-LK"),
    "NPR": ("₨", "Nepalese Rupee", "en-NP"),
    "USD": ("$", "US Dollar", "en-US"),
    "EUR": ("€", "Euro", "de-DE"),
    "GBP": ("£", "British Pound", "en-GB"),
    "AED": ("د.إ", "UAE Dirham", "ar-AE"),
    "SAR": ("﷼", "Saudi Riyal", "ar-SA"),
    "QAR": ("﷼", "Qatari Riyal", "ar-QA"),
    "KWD": ("د.ك", "Kuwaiti Dinar", "ar-KW"),
    "OMR": ("﷼", "Omani Rial", "ar-OM"),
    "BHD": (".د.ب", "Bahraini Dinar", "ar-BH"),
    "AUD": ("$", "Australian Dollar", "en-AU"),
    "CAD": ("$", "Canadian Dollar", "en-CA"),
    "NZD": ("$", "New Zealand Dollar", "en-NZ"),
    "JPY": ("¥", "Japanese Yen", "ja-JP"),
    "CNY": ("¥", "Chinese Yuan", "zh-CN"),
    "KRW": ("₩", "South Korean Won", "ko-KR"),
    "SGD": ("$", "Singapore Dollar", "en-SG"),
    "MYR": ("RM", "Malaysian Ringgit", "ms-MY"),
    "IDR": ("Rp", "Indonesian Rupiah", "id-ID"),
    "THB": ("฿", "Thai Baht", "th-TH"),
    "PHP": ("₱", "Philippine Peso", "en-PH"),
    "VND": ("₫", "Vietnamese Dong", "vi-VN"),
    "TRY": ("₺", "Turkish Lira", "tr-TR"),
    "ZAR": ("R", "South African Rand", "en-ZA"),
    "NGN": ("₦", "Nigerian Naira", "en-NG"),
    "KES": ("KSh", "Kenyan Shilling", "en-KE"),
    "EGP": ("E£", "Egyptian Pound", "ar-EG"),
    "GHS": ("₵", "Ghanaian Cedi", "en-GH"),
    "AFN": ("؋", "Afghan Afghani", "fa-AF"),
    "RUB": ("₽", "Russian Ruble", "ru-RU"),
    "BRL": ("R$", "Brazilian Real", "pt-BR"),
    "MXN": ("$", "Mexican Peso", "es-MX"),
    "CHF": ("Fr", "Swiss Franc", "de-CH"),
    "SEK": ("kr", "Swedish Krona", "sv-SE"),
    "NOK": ("kr", "Norwegian Krone", "nb-NO"),
    "PLN": ("zł", "Polish Zloty", "pl-PL"),
    "ILS": ("₪", "Israeli Shekel", "he-IL"),
    "HKD": ("$", "Hong Kong Dollar", "en-HK"),
}

DEFAULT_CURRENCY = "INR"


def currency_symbol(code):
    return CURRENCIES.get(code, CURRENCIES[DEFAULT_CURRENCY])[0]


def currency_locale(code):
    return CURRENCIES.get(code, CURRENCIES[DEFAULT_CURRENCY])[2]
