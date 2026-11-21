from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User

auth_bp=Blueprint('auth',__name__)

@auth_bp.post('/register')
def register():
 d=request.get_json() or {}; email=(d.get('email') or '').lower().strip()
 if not d.get('name') or not email or not d.get('password'): return {'message':'Name, email and password are required'},400
 if User.query.filter_by(email=email).first(): return {'message':'Email already registered'},409
 u=User(name=d['name'],email=email,password_hash=generate_password_hash(d['password']),role=d.get('role','Customer'))
 db.session.add(u); db.session.commit()
 return {'message':'Registered','user':{'id':u.id,'name':u.name,'email':u.email,'role':u.role}},201

@auth_bp.post('/login')
def login():
 d=request.get_json() or {}; u=User.query.filter_by(email=(d.get('email') or '').lower().strip()).first()
 if not u or not u.active or not check_password_hash(u.password_hash,d.get('password','')): return {'message':'Invalid credentials'},401
 token=create_access_token(identity=str(u.id),additional_claims={'role':u.role,'name':u.name})
 return {'access_token':token,'user':{'id':u.id,'name':u.name,'email':u.email,'role':u.role}}

@auth_bp.get('/me')
@jwt_required()
def me():
 u=db.session.get(User,int(get_jwt_identity())); return {'id':u.id,'name':u.name,'email':u.email,'role':u.role}
