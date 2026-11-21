from datetime import datetime
from app import db

class User(db.Model):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(120),nullable=False)
    email=db.Column(db.String(180),unique=True,index=True,nullable=False); password_hash=db.Column(db.String(255),nullable=False)
    role=db.Column(db.String(20),nullable=False,index=True); active=db.Column(db.Boolean,default=True)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
    claims=db.relationship('Claim',back_populates='customer',lazy='dynamic')

class Policy(db.Model):
    __tablename__='policies'; id=db.Column(db.Integer,primary_key=True); policy_number=db.Column(db.String(50),unique=True,index=True)
    customer_id=db.Column(db.Integer,db.ForeignKey('users.id')); policy_type=db.Column(db.String(50)); provider=db.Column(db.String(120))
    coverage_limit=db.Column(db.Float,nullable=False); start_date=db.Column(db.Date); end_date=db.Column(db.Date)
    exclusions=db.Column(db.JSON,default=list); active=db.Column(db.Boolean,default=True)

class Provider(db.Model):
    __tablename__='providers'; id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(180),unique=True)
    provider_type=db.Column(db.String(50)); suspicious=db.Column(db.Boolean,default=False); active=db.Column(db.Boolean,default=True)

class Claim(db.Model):
    __tablename__='claims'; id=db.Column(db.Integer,primary_key=True); claim_id=db.Column(db.String(30),unique=True,index=True)
    customer_id=db.Column(db.Integer,db.ForeignKey('users.id'),index=True,nullable=False); policy_id=db.Column(db.Integer,db.ForeignKey('policies.id'))
    claim_type=db.Column(db.String(50)); incident_date=db.Column(db.Date); incident_time=db.Column(db.String(20)); location=db.Column(db.String(255)); amount=db.Column(db.Float)
    description=db.Column(db.Text); provider_name=db.Column(db.String(180)); status=db.Column(db.String(30),default='SUBMITTED',index=True)
    risk_score=db.Column(db.Integer,default=0); risk_category=db.Column(db.String(20),default='LOW'); created_at=db.Column(db.DateTime,default=datetime.utcnow)
    customer=db.relationship('User',back_populates='claims'); documents=db.relationship('ClaimDocument',back_populates='claim',cascade='all,delete-orphan')

class ClaimDocument(db.Model):
    __tablename__='claim_documents'; id=db.Column(db.Integer,primary_key=True); claim_id=db.Column(db.Integer,db.ForeignKey('claims.id'),index=True)
    original_name=db.Column(db.String(255)); stored_path=db.Column(db.String(512)); mime_type=db.Column(db.String(100)); file_size=db.Column(db.Integer)
    document_type=db.Column(db.String(80),default='Other'); extracted_text=db.Column(db.Text); extracted_fields=db.Column(db.JSON,default=dict)
    processing_status=db.Column(db.String(30),default='PENDING'); confidence=db.Column(db.Float,default=0); processed_at=db.Column(db.DateTime)
    claim=db.relationship('Claim',back_populates='documents')

class DocumentVerification(db.Model):
    __tablename__='document_verifications'; id=db.Column(db.Integer,primary_key=True); claim_id=db.Column(db.Integer,db.ForeignKey('claims.id'),index=True)
    field_name=db.Column(db.String(80)); status=db.Column(db.String(30)); values=db.Column(db.JSON,default=list); evidence=db.Column(db.Text)

class HistoricalClaim(db.Model):
    __tablename__='historical_claims'; id=db.Column(db.Integer,primary_key=True); customer_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    claim_id=db.Column(db.String(30)); policy_number=db.Column(db.String(50)); vehicle_number=db.Column(db.String(30)); incident_date=db.Column(db.Date)
    location=db.Column(db.String(255)); amount=db.Column(db.Float); description=db.Column(db.Text); provider_name=db.Column(db.String(180)); fraud_score=db.Column(db.Integer,default=0)

class RiskFactor(db.Model):
    __tablename__='risk_factors'; id=db.Column(db.Integer,primary_key=True); claim_id=db.Column(db.Integer,db.ForeignKey('claims.id'),index=True)
    code=db.Column(db.String(80)); title=db.Column(db.String(180)); reason=db.Column(db.Text); severity=db.Column(db.String(20)); contribution=db.Column(db.Integer); evidence=db.Column(db.JSON)

class InvestigationNote(db.Model):
    __tablename__='investigation_notes'; id=db.Column(db.Integer,primary_key=True); claim_id=db.Column(db.Integer,db.ForeignKey('claims.id'),index=True)
    investigator_id=db.Column(db.Integer,db.ForeignKey('users.id')); note=db.Column(db.Text); created_at=db.Column(db.DateTime,default=datetime.utcnow)

class ClaimDecision(db.Model):
    __tablename__='claim_decisions'; id=db.Column(db.Integer,primary_key=True); claim_id=db.Column(db.Integer,db.ForeignKey('claims.id'),index=True)
    investigator_id=db.Column(db.Integer,db.ForeignKey('users.id')); decision=db.Column(db.String(30)); reason=db.Column(db.Text); created_at=db.Column(db.DateTime,default=datetime.utcnow)

class AuditLog(db.Model):
    __tablename__='audit_logs'; id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer,db.ForeignKey('users.id')); action=db.Column(db.String(180)); details=db.Column(db.JSON); created_at=db.Column(db.DateTime,default=datetime.utcnow)
