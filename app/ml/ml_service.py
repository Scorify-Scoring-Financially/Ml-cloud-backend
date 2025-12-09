# app/services/ml_service.py
import joblib
import logging
import uuid
from datetime import datetime
import pandas as pd 
from sqlalchemy.exc import SQLAlchemyError
from app.backend.models import LeadScore
from app.backend.db import SessionLocal
from app.backend.models import Customer, Campaign, MacroData


#monitoring
from app.monitoring.metrics import (
    push_leads_processed,
    push_leads_skipped,
    push_batch_duration,
    push_batch_errors
)

from time import perf_counter

# timezone
from datetime import datetime
from zoneinfo import ZoneInfo

# Load model & preprocessor lokal
model = joblib.load("best_bank_model_xgb.pkl")
preprocessor = joblib.load("preprocessor.pkl")

logging.basicConfig(level=logging.INFO)


# Define timezone Jakarta
JAKARTA_TZ = ZoneInfo("Asia/Jakarta")  

# Payload preparation
def prepare_input(customer, campaign, macro_dict):
    """Gabungkan data customer, campaign, dan macro untuk prediksi"""
    month_macro = macro_dict.get(campaign.month, {})
    return {
        "age": customer.age,
        "job": customer.job,
        "marital": customer.marital,
        "education": customer.education,
        "default": customer.default,
        "housing": customer.housing,
        "loan": customer.loan,
        "contact": campaign.contact,
        "month": campaign.month,
        "day_of_week": campaign.day_of_week,
        "campaign": campaign.campaign,
        "pdays": campaign.pdays,
        "previous": campaign.previous,
        "poutcome": campaign.poutcome,
        "emp.var.rate": month_macro.get("emp_var_rate"),
        "cons.price.idx": month_macro.get("cons_price_idx"),
        "cons.conf.idx": month_macro.get("cons_conf_idx"),
        "euribor3m": month_macro.get("euribor3m"),
        "nr.employed": month_macro.get("nr_employed"),
    }


# Batch prediciton function
def batch_predict(db, customers, campaigns, macro_dict):
    """Generate LeadScore, SKIP data yang sudah pernah diprediksi"""

    results = []
    skipped = 0

    # Batch config
    batch_id = str(uuid.uuid4())
    model_version = "v1.0"
    threshold = 0.5

    try:
        for customer in customers:
            for campaign in campaigns:

                if campaign.customerId != customer.id:
                    continue

                # Check if LeadScore alreadu exists
                exists = db.query(LeadScore).filter_by(
                    customerId=customer.id,
                    campaignId=campaign.id
                ).first()

                if exists:
                    skipped += 1
                    continue

                payload = prepare_input(customer, campaign, macro_dict)

                X = pd.DataFrame([payload])
                X = preprocessor.transform(X)

                pred_prob = model.predict_proba(X)[0][1]
                pred_label = "yes" if pred_prob >= threshold else "no"

                new_lead = LeadScore(
                    customerId=customer.id,
                    campaignId=campaign.id,
                    predicted_y=pred_label,
                    score=float(pred_prob),
                    batch_id=batch_id,          #per batch
                    model_version=model_version,
                    threshold=threshold,
                    createdAt=datetime.utcnow()
                )

                db.add(new_lead)
                results.append(new_lead)

        # If no new data
        if len(results) == 0:
            print(f"⚠️ Batch {batch_id} → NO NEW DATA")
            return {
                "status": "no new data",
                "batch_id": batch_id,
                "created": 0,
                "skipped": skipped
            }

        # If there are new data, commit to DB
        db.commit()

    except SQLAlchemyError as e:
        db.rollback()
        print(f"❌ Database error: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "batch_id": batch_id
        }

    print(f"✅ Batch ID: {batch_id}")
    print(f"✅ Created: {len(results)} new LeadScore")
    print(f"⏭️ Skipped: {skipped} existing LeadScore")

    return {
        "status": "success",
        "batch_id": batch_id,
        "model_version": model_version,
        "created": len(results),
        "skipped": skipped
    }



# Scheduler job function
def run_batch_job():
    """Fungsi yang dijalankan scheduler"""
    db = SessionLocal()
    start_time = perf_counter()
    batch_errors = 0

    try:
        print(f"\n⏰ Scheduler running at {datetime.now(JAKARTA_TZ)}")

        customers = db.query(Customer).all()
        campaigns = db.query(Campaign).all()
        macro_data = db.query(MacroData).all()

        macro_dict = {m.month: {
            "emp_var_rate": m.emp_var_rate,
            "cons_price_idx": m.cons_price_idx,
            "cons_conf_idx": m.cons_conf_idx,
            "euribor3m": m.euribor3m,
            "nr_employed": m.nr_employed
        } for m in macro_data}

        updated = batch_predict(db, customers, campaigns, macro_dict)

        # Push metrics to Cloud Monitoring
        push_leads_processed(updated.get("created", 0))
        push_leads_skipped(updated.get("skipped", 0))

    except Exception as e:
        logging.error(f"[Scheduler ERROR]: {str(e)}")
        batch_errors = 1
        push_batch_errors(batch_errors)  # Push error metric

    finally:
        db.close()
        duration = perf_counter() - start_time
        push_batch_duration(duration)  # push duration metric
        logging.info(f"[Scheduler] Batch duration: {duration:.2f}s")
        logging.info(f"[Scheduler] Result: {updated if 'updated' in locals() else 'ERROR'}")

#json
# def batch_predict_local(db, customers, campaigns, macro_dict):
#     """
#     Generate LeadScore ===> SIMPAN KE FILE JSON (BUKAN KE DATABASE)
#     Data yang sudah ada di DB tetap dicek untuk di-skip.
#     """

#     results = []
#     skipped = 0

#     # Batch config
#     batch_id = str(uuid.uuid4())
#     model_version = "v1.0"
#     threshold = 0.5

#     print(f"\n🚀 Starting batch: {batch_id}")

#     for customer in customers:
#         for campaign in campaigns:

#             if campaign.customerId != customer.id:
#                 continue

#             exists = db.query(LeadScore).filter_by(
#                 customerId=customer.id,
#                 campaignId=campaign.id
#             ).first()

#             if exists:
#                 skipped += 1
#                 continue

#             payload = prepare_input(customer, campaign, macro_dict)

#             X = pd.DataFrame([payload])
#             X = preprocessor.transform(X)

#             pred_prob = model.predict_proba(X)[0][1]
#             pred_label = "yes" if pred_prob >= threshold else "no"

#             # ✅ SIMPAN KE DICT (BUKAN ORM)
#             new_lead = {
#                 "customerId": customer.id,
#                 "campaignId": campaign.id,
#                 "predicted_y": pred_label,
#                 "score": float(pred_prob),

#                 # Batch info
#                 "batch_id": batch_id,
#                 "model_version": model_version,
#                 "threshold": threshold,

#                 "createdAt": datetime.utcnow().isoformat()
#             }

#             results.append(new_lead)

#     # ✅ KALO TIDAK ADA DATA BARU
#     if len(results) == 0:
#         print(f"⚠️ Batch {batch_id} → NO NEW DATA")
#         return {
#             "status": "no new data",
#             "batch_id": batch_id,
#             "created": 0,
#             "skipped": skipped
#         }

#     # ✅ SIMPAN KE FILE JSON
#     os.makedirs("batches", exist_ok=True)

#     filename = f"batches/leads_{batch_id}.json"

#     with open(filename, "w") as f:
#         json.dump(results, f, indent=4)

#     print(f"✅ Batch ID: {batch_id}")
#     print(f"✅ Saved: {len(results)} new LeadScore → {filename}")
#     print(f"⏭️ Skipped: {skipped} existing LeadScore")

#     return {
#         "status": "success",
#         "batch_id": batch_id,
#         "model_version": model_version,
#         "saved_to": filename,
#         "created": len(results),
#         "skipped": skipped
#     }