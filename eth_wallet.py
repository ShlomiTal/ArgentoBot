import os
from eth_account import Account

# מאפשר שימוש בפיצ'ר של יצירת ארנקים ממנמוניק
Account.enable_unaudited_hdwallet_features()

# טוען את המנמוניק מהסביבה
MNEMONIC = os.getenv("ETH_MNEMONIC")

def generate_eth_address(index: int) -> dict:
    """
    יוצר ארנק ETH לפי index מתוך mnemonic.
    """
    if not MNEMONIC:
        raise ValueError("Missing ETH_MNEMONIC in environment variables.")

    try:
        acct = Account.from_mnemonic(
            MNEMONIC,
            account_path=f"m/44'/60'/0'/0/{index}"
        )
        return {
            "address": acct.address,
            "private_key": acct.key.hex()
        }
    except Exception as e:
        print(f"⚠️ Failed to generate wallet for index {index}: {e}")
        return {
            "address": None,
            "private_key": None
        }
