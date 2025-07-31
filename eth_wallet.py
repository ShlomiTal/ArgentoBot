import os
from eth_account import Account

# הפעלת תמיכה ב-HD Wallet דרך Mnemonic
Account.enable_unaudited_hdwallet_features()

# טעינת המנמוניק (Seed) מהסביבה
MNEMONIC = os.getenv("ETH_MNEMONIC")

def generate_eth_address(index: int):
    """
    יוצר כתובת ETH ייחודית לפי index מתוך ה-HD Wallet שלך.
    index שונה לכל משתמש, ומאפשר ליצור עבורם כתובת ייחודית שנשלטת על ידי הארנק הראשי שלך.
    """
    if not MNEMONIC:
        raise ValueError("❌ לא נמצא ETH_MNEMONIC. ודא שהוא מוגדר בסביבת Railway.")

    acct = Account.from_mnemonic(MNEMONIC, account_path=f"m/44'/60'/0'/0/{index}")
    return {
        "address": acct.address,
        "private_key": acct.key.hex()  # אל תשתמש בזה בפרודקשן! לא לחשוף!
    }
