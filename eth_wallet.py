import os
from eth_account import Account

# אפשרות ליצירת ארנקים ממנמוניק
Account.enable_unaudited_hdwallet_features()

# טען מנמוניק מהסביבה
MNEMONIC = os.getenv("ETH_MNEMONIC")

if not MNEMONIC:
    raise ValueError("❌ Missing ETH_MNEMONIC environment variable!")

def generate_eth_address(index: int) -> dict:
    """
    מחזיר כתובת ETH ו־Private Key לפי אינדקס במנמוניק.
    """
    try:
        acct = Account.from_mnemonic(MNEMONIC, account_path=f"m/44'/60'/0'/0/{index}")
        return {
            "address": acct.address,
            "private_key": acct.key.hex()
        }
    except Exception as e:
        print(f"⚠️ Failed to generate wallet for index {index}: {e}")
        raise
