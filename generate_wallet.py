from algosdk import account, mnemonic
pk, addr = account.generate_account()
m = mnemonic.from_private_key(pk)
print(f"\n🚀 WALLET GENERATED!")
print(f"ADDRESS: {addr}")
print(f"MNEMONIC: {m}\n")
with open('.env', 'w') as f:
    f.write(f'DEPLOYER_MNEMONIC="{m}"\n')
