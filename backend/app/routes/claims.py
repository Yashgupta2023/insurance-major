import os, uuid
from datetime import date
from flask import Blueprint, request, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models import User, Policy, Claim, ClaimDocument, InvestigationNote, ClaimDecision

claims_bp=Blueprint('claims',__name__)
def role_required(*roles):
 def deco(fn):
  from functools import wraps
  @wraps(fn)
  @jwt_required()
  def wrapped(*a,**k):
   if get_jwt().get('role') not in roles: return {'message':'Forbidden'},403
   return fn(*a,**k)
  return wrapped
 return deco

@claims_bp.get('/claims')
@jwt_required()
def list_claims():
 role=get_jwt().get('role'); uid=int(get_jwt_identity())
 q=Claim.query
 if role=='Customer': q=q.filter_by(customer_id=uid)
 rows=q.order_by(Claim.created_at.desc()).all()
 return {'claims':[{'id':x.id,'claim_id':x.claim_id,'customer':x.customer.name,'type':x.claim_type,'amount':x.amount,'status':x.status,'risk_score':x.risk_score,'risk_category':x.risk_category,'created_at':x.created_at.isoformat(),'location':x.location} for x in rows]}

@claims_bp.post('/claims')
@role_required('Customer','Admin')
def create_claim():
 d=request.get_json() or {}; uid=int(get_jwt_identity())
 policy=Policy.query.filter_by(policy_number=d.get('policy_number'),customer_id=uid).first()
 c=Claim(claim_id=f"CLM-{uuid.uuid4().hex[:8].upper()}",customer_id=uid,policy_id=policy.id if policy else None,claim_type=d.get('claim_type'),incident_date=date.fromisoformat(d['incident_date']) if d.get('incident_date') else None,incident_time=d.get('incident_time'),location=d.get('location'),amount=float(d.get('amount') or 0),description=d.get('description'),provider_name=d.get('provider'))
 db.session.add(c); db.session.commit()
 return {'claim':{'id':c.id,'claim_id':c.claim_id,'status':c.status}},201

@claims_bp.get('/claims/<int:claim_id>')
@jwt_required()
def claim_detail(claim_id):
 c=db.session.get(Claim,claim_id)
 if not c: return {'message':'Not found'},404
 if get_jwt().get('role')=='Customer' and c.customer_id!=int(get_jwt_identity()): return {'message':'Forbidden'},403
 return {'claim':{'id':c.id,'claim_id':c.claim_id,'type':c.claim_type,'amount':c.amount,'location':c.location,'description':c.description,'status':c.status,'risk_score':c.risk_score,'risk_category':c.risk_category,'customer':c.customer.name,'provider':c.provider_name,'documents':[{'id':d.id,'name':d.original_name,'type':d.document_type,'status':d.processing_status,'fields':d.extracted_fields or {}} for d in c.documents]}}

@claims_bp.post('/claims/<int:claim_id>/documents')
@role_required('Customer','Admin','Investigator')
def upload_document(claim_id):
 c=db.session.get(Claim,claim_id)
 if not c: return {'message':'Claim not found'},404
 if get_jwt().get('role')=='Customer' and c.customer_id!=int(get_jwt_identity()): return {'message':'Forbidden'},403
 f=request.files.get('file')
 if not f: return {'message':'File required'},400
 ext=f.filename.rsplit('.',1)[-1].lower() if '.' in f.filename else ''
 if ext not in current_app.config['ALLOWED_EXTENSIONS']: return {'message':'Unsupported file type'},400
 folder=os.path.join(current_app.config['UPLOAD_FOLDER'],str(claim_id)); os.makedirs(folder,exist_ok=True)
 name=f'{uuid.uuid4().hex}.{ext}'; path=os.path.join(folder,name); f.save(path)
 d=ClaimDocument(claim_id=c.id,original_name=f.filename,stored_path=path,mime_type=f.mimetype,file_size=os.path.getsize(path),processing_status='PENDING')
 db.session.add(d); db.session.commit()
 return {'document':{'id':d.id,'name':d.original_name}},201

@claims_bp.post('/claims/<int:claim_id>/notes')
@role_required('Investigator','Admin')
def add_note(claim_id):
 d=request.get_json() or {}; n=InvestigationNote(claim_id=claim_id,investigator_id=int(get_jwt_identity()),note=d.get('note','')); db.session.add(n); db.session.commit(); return {'message':'Note added'},201

@claims_bp.post('/claims/<int:claim_id>/decision')
@role_required('Investigator','Admin')
def decision(claim_id):
 d=request.get_json() or {}; choice=d.get('decision',''); reason=d.get('reason','')
 if choice not in ('APPROVED','REJECTED','INVESTIGATION') or (choice!='APPROVED' and not reason): return {'message':'Valid decision and reason required'},400
 dec=ClaimDecision(claim_id=claim_id,investigator_id=int(get_jwt_identity()),decision=choice,reason=reason); db.session.add(dec)
 c=db.session.get(Claim,claim_id); c.status=choice; db.session.commit(); return {'message':'Decision recorded','decision':choice}

@claims_bp.get('/policies')
@jwt_required()
def customer_policies():
 uid=int(get_jwt_identity())
 role=get_jwt().get('role')
 query=Policy.query
 if role=='Customer': query=query.filter_by(customer_id=uid)
 policies=query.all()
 return {'policies':[{'id':p.id,'policy_number':p.policy_number,'policy_type':p.policy_type,'coverage_limit':p.coverage_limit,'start_date':p.start_date.isoformat() if p.start_date else None,'end_date':p.end_date.isoformat() if p.end_date else None,'active':p.active} for p in policies]}
