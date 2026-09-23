"""Local conservative reservations. Never modifies billing settings or buys credit."""
from __future__ import annotations
import json
import os
from pathlib import Path
from src.ml.common import write_json
from src.ml.forecast import CoreNotReady

RATES={"gpt-4.1-mini":(0.4,1.6),"gpt-4.1-mini-2025-04-14":(0.4,1.6)}
PRICE_SOURCE="https://developers.openai.com/api/docs/models/gpt-4.1-mini"
PRICE_DATE="2026-09-23"


class Reservation:
    def __init__(self,run_id,model):
        if model not in RATES: raise CoreNotReady("No verified price configured for selected OPENAI_MODEL")
        self.model=model; self.run_id=run_id; self.reserved=0.20
        self.path=Path(os.getenv("OPENAI_BUDGET_LEDGER","artifacts/openai-usage.json"))
        self.limit=min(50.0,float(os.getenv("OPENAI_SESSION_BUDGET_USD","1.0")))
        if not 0<self.limit<=50: raise CoreNotReady("Invalid API budget")
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.lock=self.path.with_suffix(".lock")
        try: self.handle=os.open(self.lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
        except FileExistsError as error: raise CoreNotReady("API budget ledger is locked by another run; no concurrent spending") from error
        try:
            self.ledger=json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else {"charged_or_reserved_usd":0,"runs":{}}
            if self.ledger["charged_or_reserved_usd"]+self.reserved>self.limit: raise CoreNotReady("Local API budget exhausted")
            self.ledger["charged_or_reserved_usd"]+=self.reserved
            self.ledger["runs"][run_id]={"model":model,"reserved_usd":self.reserved,"status":"running","price_source":PRICE_SOURCE,"price_checked":PRICE_DATE}
            write_json(self.path,self.ledger)
        except Exception:
            os.close(self.handle); self.lock.unlink(); raise

    def finish(self,usage,status):
        # A failed request without usage may still have been billed: retain reservation.
        charge=self.reserved if usage.get("uncertain_request") else usage["estimated_usd"]
        self.ledger["charged_or_reserved_usd"]+=charge-self.reserved
        self.ledger["runs"][self.run_id].update({"status":status,"usage":usage,"charged_or_reserved_usd":charge})
        try: write_json(self.path,self.ledger)
        finally: os.close(self.handle); self.lock.unlink()
