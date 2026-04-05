import os
import base64
from pathlib import Path
from dotenv import load_dotenv
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import ApplicationCreateTxn, StateSchema, wait_for_confirmation

print("--- 🏁 STARTING MANUAL TEAL DEPLOYMENT ---")

# 1. Load environment
load_dotenv()
passphrase = os.getenv("MNEMONIC") or os.getenv("DEPLOYER_MNEMONIC")
algod_url = "https://testnet-api.algonode.cloud"

if not passphrase:
    print("❌ ERROR: MNEMONIC not found in .env")
    exit()

# 2. Setup Client
algod_client = algod.AlgodClient("", algod_url)
private_key = mnemonic.to_private_key(passphrase)
sender_address = account.address_from_private_key(private_key)
print(f"✅ Wallet: {sender_address}")

def compile_program(client, source_code):
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response['result'])

# 3. List of contracts
contracts = ["MediRegistry", "ProcurementEscrow", "CounterfeitAlert"]

for name in contracts:
    print(f"\n--- 🚀 Deploying: {name} ---")
    
    # We use the TEAL files your compiler already made!
    approval_path = Path(f"./contracts/artifacts/{name}.approval.teal")
    clear_path = Path(f"./contracts/artifacts/{name}.clear.teal")

    if not approval_path.exists():
        print(f"⚠️  Missing TEAL files for {name}")
        continue

    try:
        # Read and Compile
        approval_source = approval_path.read_text()
        clear_source = clear_path.read_text()
        
        approval_program = compile_program(algod_client, approval_source)
        clear_program = compile_program(algod_client, clear_source)

        # Get network params
        params = algod_client.suggested_params()

        # Create the transaction (Over-allocating schema 8/8 to be safe)
        txn = ApplicationCreateTxn(
            sender=sender_address,
            sp=params,
            on_complete=0,
            approval_program=approval_program,
            clear_program=clear_program,
            global_schema=StateSchema(num_uints=8, num_byte_slices=8),
            local_schema=StateSchema(num_uints=8, num_byte_slices=8)
        )

        # Sign and Send
        signed_txn = txn.sign(private_key)
        txid = algod_client.send_transaction(signed_txn)
        print(f"Transaction sent: {txid}")
        
        # Wait for it to hit the blockchain
        wait_for_confirmation(algod_client, txid, 4)
        transaction_info = algod_client.pending_transaction_info(txid)
        app_id = transaction_info['application-index']
        
        print(f"🎉 SUCCESS! {name} is LIVE.")
        print(f"   App ID: {app_id}")
        print(f"   Explorer: https://lora.algo.xyz/testnet/app/{app_id}")

    except Exception as e:
        print(f"❌ Failed {name}: {e}")

print("\n--- ✅ ALL TASKS FINISHED ---")
