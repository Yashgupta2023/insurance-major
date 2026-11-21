from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt
from app import db
from app.models import User, Policy, Provider, Claim

admin_bp=Blueprint('admin',__name__)
def admin_required(fn):
 from functools import wraps
 @wraps(fn)
 @jwt_required()
 def wrapped(*a,**k):
  if get_jwt().get('role')!='Admin': return {'message':'Forbidden'},403
  return fn(*a,**k)
 return wrapped

@admin_bp.get('/users')
@admin_required
def users():
 return {'users':[{'id':u.id,'name':u.name,'email':u.email,'role':u.role,'active':u.active} for u in User.query.order_by(User.id)]}

@admin_bp.patch('/users/<int:user_id>')
@admin_required
def update_user(user_id):
 d=request.get_json() or {}; u=db.session.get(User,user_id)
 if not u: return {'message':'Not found'},404
 if 'active' in d: u.active=bool(d['active'])
 db.session.commit(); return {'message':'User updated'}

@admin_bp.get('/policies')
@admin_required
def policies():
 return {'policies':[{'id':p.id,'policy_number':p.policy_number,'customer_id':p.customer_id,'policy_type':p.policy_type,'coverage_limit':p.coverage_limit,'start_date':p.start_date.isoformat() if p.start_date else None,'end_date':p.end_date.isoformat() if p.end_date else None,'active':p.active} for p in Policy.query.all()]}

@admin_bp.post('/policies')
@admin_required
def create_policy():
 d=request.get_json() or {}; p=Policy(policy_number=d['policy_number'],customer_id=d.get('customer_id'),policy_type=d.get('policy_type','Motor'),coverage_limit=float(d.get('coverage_limit',0)),exclusions=d.get('exclusions',[]),active=True)
 db.session.add(p); db.session.commit(); return {'message':'Policy created','id':p.id},201

@admin_bp.get('/providers')
@admin_required
def providers():
 return {'providers':[{'id':p.id,'name':p.name,'provider_type':p.provider_type,'suspicious':p.suspicious,'active':p.active} for p in Provider.query.all()]}
