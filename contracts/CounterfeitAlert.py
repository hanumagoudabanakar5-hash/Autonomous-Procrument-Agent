from algopy import ARC4Contract, itxn, String, arc4, Asset, Account, Bytes, log

class CounterfeitAlert(ARC4Contract):
    @arc4.abimethod
    def verify_and_freeze(self, med_asset: Asset, holder: Account, scanned_hash: Bytes, true_hash: Bytes) -> String:
        if scanned_hash != true_hash:
            itxn.AssetFreeze(
                freeze_asset=med_asset,
                freeze_account=holder,
                frozen=True
            ).submit()
            log("ALERT: Counterfeit detected! Asset frozen.")
            return String("COUNTERFEIT_DETECTED")
        return String("BATCH_GENUINE")
