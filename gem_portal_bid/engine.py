"""GeM 4.0 Public Procurement, Bid Tracking & CRAC Invoice Engine."""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Dict, Any, Optional

@dataclass
class GeMBidDocument:
    bid_number: str
    ministry: str
    department: str
    category: str  # GOODS, SERVICES
    item_description: str
    quantity: int
    published_date: str
    closing_date: str
    estimated_budget: float
    emd_amount_required: float
    status: str = "PUBLISHED"  # PUBLISHED, PREPARED, SUBMITTED, WON, LOST, CRAC_PENDING

@dataclass
class EMDGuaranteeRecord:
    bg_number: str
    issuing_bank: str
    amount: float
    issue_date: str
    expiry_date: str
    status: str = "ACTIVE"  # ACTIVE, RELEASED, FORFEITED

class GeMPublicProcurementEngine:
    def __init__(self, vendor_gstin: str):
        self.vendor_gstin = vendor_gstin
        self.bids: Dict[str, GeMBidDocument] = {}
        self.emd_records: Dict[str, EMDGuaranteeRecord] = {}
        self.contracts: Dict[str, Dict[str, Any]] = {}

    def register_bid(self, doc: GeMBidDocument) -> Dict[str, Any]:
        self.bids[doc.bid_number] = doc
        return {"bid_number": doc.bid_number, "status": doc.status, "emd_required": doc.emd_amount_required}

    def issue_emd_guarantee(self, bid_number: str, bg_number: str, bank: str, amount: float, expiry: str) -> Dict[str, Any]:
        if bid_number not in self.bids:
            raise ValueError(f"Bid {bid_number} not found.")
        bid = self.bids[bid_number]
        if amount < bid.emd_amount_required:
            raise ValueError(f"EMD amount ₹{amount} is less than required ₹{bid.emd_amount_required}")
        rec = EMDGuaranteeRecord(
            bg_number=bg_number, issuing_bank=bank, amount=amount,
            issue_date=date.today().isoformat(), expiry_date=expiry, status="ACTIVE"
        )
        self.emd_records[bid_number] = rec
        bid.status = "PREPARED"
        return {"bid_number": bid_number, "bg_number": bg_number, "status": "EMD_ATTACHED"}

    def simulate_l1_pricing(self, bid_number: str, vendor_quotes: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not vendor_quotes:
            raise ValueError("No quotes provided for L1 ranking.")
        ranked = sorted(vendor_quotes, key=lambda q: (q["quote_price_per_unit"], -q.get("gem_seller_rating", 0)))
        l1_winner = ranked[0]
        return {
            "bid_number": bid_number,
            "l1_bidder": l1_winner["vendor_name"],
            "l1_unit_price": l1_winner["quote_price_per_unit"],
            "ranked_quotes": ranked
        }

    def generate_crac_milestone_invoice(self, contract_number: str, crac_id: str, accepted_qty: int, unit_price: float, gst_rate_pct: float = 18.0) -> Dict[str, Any]:
        if accepted_qty <= 0:
            raise ValueError("CRAC accepted quantity must be strictly greater than 0.")
        taxable_value = round(accepted_qty * unit_price, 2)
        gst_amount = round(taxable_value * (gst_rate_pct / 100.0), 2)
        total_invoice_amount = round(taxable_value + gst_amount, 2)
        contract = {
            "contract_number": contract_number,
            "crac_id": crac_id,
            "accepted_qty": accepted_qty,
            "taxable_value": taxable_value,
            "gst_amount": gst_amount,
            "total_invoice_amount": total_invoice_amount,
            "invoice_status": "READY_FOR_PFMS_DISBURSEMENT"
        }
        self.contracts[contract_number] = contract
        return contract
