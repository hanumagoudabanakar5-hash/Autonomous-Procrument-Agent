from algopy import ARC4Contract, itxn, String, arc4, Account, UInt64
class ProcurementEscrow(ARC4Contract):
    @arc4.abimethod
    def release_payment(self, supplier: Account, amount: UInt64, qr_is_genuine: bool) -> String:
        assert qr_is_genuine, "Payment Locked: QR scan failed!"
        itxn.Payment(
            receiver=supplier,
            amount=amount,
            fee=UInt64(0)
        ).submit()
        return String("Success: Payment released.")
