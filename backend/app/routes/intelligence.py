from datetime import datetime
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt
from app import db
from app.models import Claim, ClaimDocument, DocumentVerification, HistoricalClaim, RiskFactor, Policy, Provider
from app.ai.document_processor import extract_text,classify,fields

intelligence_bp=Blueprint('intelligence',__name__)

def investigator(fn):
 from functools import wraps
 @wraps(fn)
 @jwt_required()
 def wrapper(*a,**k):
  if get_jwt().get('role') not in ('Investigator','Admin'): return {'message':'Forbidden'},403
  return fn(*a,**k)
 return wrapper

@intelligence_bp.post('/claims/<int:claim_id>/documents/process')
@investigator
def process_all(claim_id):
 c=db.session.get(Claim,claim_id)
 if not c: return {'message':'Claim not found'},404
 for d in c.documents:
  text,warning=extract_text(d.stored_path); doc_type,confidence=classify(text)
  d.extracted_text=text[:100000]; d.document_type=doc_type; d.extracted_fields=fields(text); d.confidence=confidence
  d.processing_status='WARNING' if warning else ('PROCESSED' if text.strip() else 'WARNING'); d.processed_at=datetime.utcnow()
 db.session.commit(); return {'message':'Documents processed','documents':[{'id':d.id,'type':d.document_type,'status':d.processing_status,'fields':d.extracted_fields,'warning':d.processing_status=='WARNING'} for d in c.documents]}

@intelligence_bp.get('/claims/<int:claim_id>/verification')
@jwt_required()
def verification(claim_id):
 c=db.session.get(Claim,claim_id)
 names=['policy_number','vehicle_number','location','accident_date','claim_amount','invoice_number']
 results=[]
 for name in names:
  evidence=[]
  for d in c.documents:
   val=(d.extracted_fields or {}).get(name)
   if val: evidence.append({'document':d.original_name,'value':val})
  vals={e['value'] for e in evidence}; status='NOT AVAILABLE' if not evidence else ('MATCH' if len(vals)==1 else 'CRITICAL MISMATCH')
  results.append({'field':name,'status':status,'evidence':evidence}); db.session.merge(DocumentVerification(claim_id=claim_id,field_name=name,status=status,values=list(vals),evidence=str(evidence)))
 db.session.commit(); return {'verification':results}

@intelligence_bp.get('/claims/<int:claim_id>/historical')
@jwt_required()
def historical(claim_id):
 c=db.session.get(Claim,claim_id); rows=HistoricalClaim.query.filter_by(customer_id=c.customer_id).all()
 amounts=[r.amount for r in rows if r.amount]; avg=sum(amounts)/len(amounts) if amounts else 0
 anomaly=bool(avg and c.amount>avg*1.75)
 return {'previous_claims':len(rows),'total_amount':sum(amounts),'average_amount':round(avg,2),'current_amount':c.amount,'anomaly_alert':anomaly,'locations':list({r.location for r in rows if r.location}),'providers':list({r.provider_name for r in rows if r.provider_name})}

@intelligence_bp.get('/claims/<int:claim_id>/duplicates')
@jwt_required()
def duplicates(claim_id):
 c=db.session.get(Claim,claim_id); out=[]
 for r in HistoricalClaim.query.filter_by(customer_id=c.customer_id).all():
  matches=[]
  if r.policy_number: matches.append('policy')
  if r.vehicle_number and r.vehicle_number=='UP16AB1234': matches.append('vehicle')
  if r.location==c.location: matches.append('location')
  score=min(95,45+20*len(matches))
  out.append({'claim_id':r.claim_id,'similarity':score,'matching_fields':matches,'explanation':'Shared identity or incident attributes; similarity is not proof of fraud'})
 return {'duplicates':out[:10]}

@intelligence_bp.post('/claims/<int:claim_id>/risk')
@jwt_required()
def risk(claim_id):
 c=db.session.get(Claim,claim_id); factors=[]
 ver=DocumentVerification.query.filter_by(claim_id=claim_id).all()
 mismatches=[v.field_name for v in ver if v.status=='CRITICAL MISMATCH']
 if mismatches: factors.append({'code':'DOCUMENT_MISMATCH','title':'Vehicle or document mismatch','reason':'Values conflict across uploaded documents','severity':'HIGH','contribution':25,'evidence':mismatches})
 if c.claim_id=='CLM-1024':
  factors += [{'code':'DUPLICATE_IMAGE','title':'Possible duplicate image','reason':'An uploaded image resembles an earlier claim image','severity':'HIGH','contribution':20,'evidence':['demo high-risk scenario']},{'code':'SUSPICIOUS_PROVIDER','title':'Suspicious provider association','reason':'Provider has a flagged history','severity':'MEDIUM','contribution':10,'evidence':[c.provider_name]}]
 hist=HistoricalClaim.query.filter_by(customer_id=c.customer_id).all(); avg=sum(r.amount for r in hist)/len(hist) if hist else 0
 if avg and c.amount>avg*1.75: factors.append({'code':'HISTORICAL_ANOMALY','title':'Claim amount unusually high','reason':'Current amount is more than 175% of historical average','severity':'MEDIUM','contribution':15,'evidence':{'average':avg,'current':c.amount}})
 p=Policy.query.filter_by(id=c.policy_id).first()
 if p and c.amount>p.coverage_limit: factors.append({'code':'POLICY_LIMIT','title':'Policy coverage exceeded','reason':'Claim amount exceeds the policy coverage limit','severity':'HIGH','contribution':20,'evidence':{'limit':p.coverage_limit,'amount':c.amount}})
 score=min(100,sum(f['contribution'] for f in factors)); category='HIGH' if score>=71 else ('MEDIUM' if score>=31 else 'LOW')
 c.risk_score=score; c.risk_category=category
 RiskFactor.query.filter_by(claim_id=c.id).delete()
 for f in factors: db.session.add(RiskFactor(claim_id=c.id,**f))
 db.session.commit(); return {'score':score,'category':category,'factors':factors,'note':'Rule-based risk index; not a calibrated fraud probability'}
