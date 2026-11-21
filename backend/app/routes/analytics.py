from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy import func
from app import db
from app.models import Claim, User, Policy, Provider, RiskFactor

analytics_bp=Blueprint('analytics',__name__)
def authorized(fn):
 from functools import wraps
 @wraps(fn)
 @jwt_required()
 def wrapped(*a,**k):
  if get_jwt().get('role') not in ('Investigator','Admin'): return {'message':'Forbidden'},403
  return fn(*a,**k)
 return wrapped

@analytics_bp.get('/overview')
@authorized
def overview():
 return {'users':User.query.count(),'customers':User.query.filter_by(role='Customer').count(),'investigators':User.query.filter_by(role='Investigator').count(),'claims':Claim.query.count(),'policies':Policy.query.count(),'providers':Provider.query.count(),'fraud_alerts':Claim.query.filter(Claim.risk_category=='HIGH').count()}

@analytics_bp.get('/claims')
@authorized
def claims():
 month_expr=func.to_char(Claim.created_at,'YYYY-MM')
 rows=db.session.query(month_expr,func.count(Claim.id)).group_by(month_expr).all()
 categories=db.session.query(Claim.claim_type,func.count(Claim.id)).group_by(Claim.claim_type).all()
 status=db.session.query(Claim.status,func.count(Claim.id)).group_by(Claim.status).all()
 risk=db.session.query(Claim.risk_category,func.count(Claim.id)).group_by(Claim.risk_category).all()
 return {'monthly':[{'month':r[0] or '2026-11','value':r[1]} for r in rows],'categories':[{'name':r[0] or 'Other','value':r[1]} for r in categories],'status':[{'name':r[0],'value':r[1]} for r in status],'risk':[{'name':r[0],'value':r[1]} for r in risk]}
