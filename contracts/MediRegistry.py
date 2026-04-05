from algopy import ARC4Contract, itxn, String, arc4, Global, UInt64
class MediRegistry(ARC4Contract):
    @arc4.abimethod
    def mint_medicine_batch(self, batch_name: String, ipfs_metadata_url: String) -> arc4.UInt64:
        mint_tx = itxn.AssetConfig(
            asset_name=batch_name,
            unit_name=String("MED"),
            url=ipfs_metadata_url,
            total=UInt64(100),
            decimals=UInt64(0),
            manager=Global.current_application_address,
            freeze=Global.current_application_address,
        ).submit()
        return arc4.UInt64(mint_tx.created_asset.id)
