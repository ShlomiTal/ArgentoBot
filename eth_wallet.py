import os
from eth_account import Account

# Load mnemonic from Railway environment variable
MNEMONIC = os.getenv("ETH_MNEMONIC")

def generate_eth_address(index: int):
    """
    Generate a unique ETH address from an HD wallet using the user's index.
    You must store the private key securely (if needed).
    """
    if not MNEMONIC:
        raise ValueError("Mnemonic not found. Set ETH_MNEMONIC in Railway.")

    acct = Account.from_mnemonic(MNEMONIC, account_path=f"m/44'/60'/0'/0/{index}")
    return {
        "address": acct.address,
        "private_key": acct.key.hex()  # DO NOT expose this publicly
    }
