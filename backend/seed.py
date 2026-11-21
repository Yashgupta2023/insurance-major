from datetime import date, timedelta
from random import randint
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User, Policy, Provider, Claim, HistoricalClaim
app=create_app()
with app.app_context():
 db.drop_all(); db.create_all()
 admins=[('Customer','customer@demo.com'),('Customer','customer2@demo.com')]
 customers=[]
 for i,(role,email) in enumerate(admins,1):
  u=User(name=f'Demo Customer {i}',email=email,password_hash=generate_password_hash('Demo@123'),role=role); db.session.add(u); customers.append(u)
 for i in range(3,16):
  u=User(name=f'Customer {i:02}',email=f'customer{i}@demo.com',password_hash=generate_password_hash('Demo@123'),role='Customer'); db.session.add(u); customers.append(u)
 for i in range(3): db.session.add(User(name=f'Investigator {i+1}',email=f'investigator{i+1}@demo.com',password_hash=generate_password_hash('Demo@123'),role='Investigator'))
 db.session.add(User(name='Demo Investigator',email='investigator@demo.com',password_hash=generate_password_hash('Demo@123'),role='Investigator'))
 db.session.add(User(name='System Administrator',email='admin@demo.com',password_hash=generate_password_hash('Demo@123'),role='Admin'))
 db.session.flush()
 providers=['CityCare Hospital','Metro Diagnostics','SafeDrive Garage','Apex Motors','NorthStar Clinic','GreenAuto Works','CarePlus Hospital','Precision Repairs','Prime Insurance Assist','Rapid Fix Garage']
 for i,n in enumerate(providers): db.session.add(Provider(name=n,provider_type='HOSPITAL' if i%3==0 else 'GARAGE',suspicious=(i==3)))
 db.session.flush()
 for i,c in enumerate(customers):
  db.session.add(Policy(policy_number=f'POL-{1000+i}',customer_id=c.id,policy_type='Health & Motor',provider='Apex Insurance',coverage_limit=500000 if i%2 else 300000,start_date=date(2025,1,1),end_date=date(2027,12,31),exclusions=['Cosmetic treatment']))
 db.session.flush()
 base_claims=[]
 for i,c in enumerate(customers):
  p=Policy.query.filter_by(customer_id=c.id).first()
  for j in range(2):
   h=HistoricalClaim(customer_id=c.id,claim_id=f'HCLM-{100+i}-{j}',policy_number=p.policy_number,vehicle_number=f'DL01AB{100+i+j}',incident_date=date(2025,1+i%12,5+j),location='New Delhi',amount=35000+j*17000,description='Motor accident repair and treatment',provider_name=providers[j],fraud_score=10+j*15)
   db.session.add(h)
 db.session.flush()
 demos=[('CLM-1024','Customer 01','Vehicle accident repair','HIGH',82,'SUBMITTED'),('CLM-1025','Demo Customer 2','Hospital treatment','LOW',18,'APPROVED'),('CLM-1026','Customer 03','Motor repair','MEDIUM',48,'INVESTIGATION')]
 for k,(cid,cname,ctype,risk,score,status) in enumerate(demos):
  c=customers[k%len(customers)]
  p=Policy.query.filter_by(customer_id=c.id).first()
  db.session.add(Claim(claim_id=cid,customer_id=c.id,policy_id=p.id,claim_type=ctype,incident_date=date(2026,10,10+k),incident_time='14:30',location='New Delhi',amount=120000 if k==0 else (85000 if k==2 else 28000),description='Accident and associated claim expenses',provider_name='Apex Motors' if k==0 else providers[k],status=status,risk_score=score,risk_category=risk))
 db.session.commit(); print('Seeded PostgreSQL database with demo accounts and scenarios')
