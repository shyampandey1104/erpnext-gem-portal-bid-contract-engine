import unittest
from gem_portal_bid.engine import GeMBidDocument, GeMPublicProcurementEngine

class TestGeMPublicProcurementEngine(unittest.TestCase):
    def setUp(self):
        self.engine = GeMPublicProcurementEngine(vendor_gstin="07AAAAA0000A1Z5")

    def test_bid_registration_and_emd(self):
        bid = GeMBidDocument(
            bid_number="GEM/2026/B/889210", ministry="Ministry of Defence",
            department="Military Engineer Services", category="GOODS",
            item_description="Industrial Grade Ruggedized Switches",
            quantity=100, published_date="2026-03-01", closing_date="2026-03-25",
            estimated_budget=5000000.0, emd_amount_required=100000.0
        )
        reg = self.engine.register_bid(bid)
        self.assertEqual(reg["bid_number"], "GEM/2026/B/889210")
        
        emd_res = self.engine.issue_emd_guarantee(
            bid_number="GEM/2026/B/889210", bg_number="BG/HDFC/2026/991",
            bank="HDFC Bank", amount=100000.0, expiry="2026-09-30"
        )
        self.assertEqual(emd_res["status"], "EMD_ATTACHED")

    def test_l1_ranking_simulation(self):
        quotes = [
            {"vendor_name": "Supplier A", "quote_price_per_unit": 48500.0, "gem_seller_rating": 4.8},
            {"vendor_name": "Supplier B", "quote_price_per_unit": 46200.0, "gem_seller_rating": 4.5},
            {"vendor_name": "Supplier C", "quote_price_per_unit": 49000.0, "gem_seller_rating": 4.9}
        ]
        res = self.engine.simulate_l1_pricing("GEM/2026/B/889210", quotes)
        self.assertEqual(res["l1_bidder"], "Supplier B")
        self.assertEqual(res["l1_unit_price"], 46200.0)

    def test_crac_milestone_invoice(self):
        inv = self.engine.generate_crac_milestone_invoice(
            contract_number="GEMC-51168772390", crac_id="CRAC-2026-00441",
            accepted_qty=100, unit_price=46200.0, gst_rate_pct=18.0
        )
        self.assertEqual(inv["taxable_value"], 4620000.0)
        self.assertEqual(inv["total_invoice_amount"], 5451600.0)
        self.assertEqual(inv["invoice_status"], "READY_FOR_PFMS_DISBURSEMENT")

if __name__ == "__main__":
    unittest.main()
