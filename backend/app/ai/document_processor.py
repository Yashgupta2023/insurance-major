import re, os
import fitz
from PIL import Image
import pytesseract

KEYWORDS={
 'Insurance Policy':['policy','coverage','premium','insured'],
 'Claim Form':['claim','incident','accident','applicant'],
 'FIR':['fir','police','complaint','accident'],
 'Vehicle RC':['registration','rc','vehicle','chassis'],
 'Driving Licence':['driving licence','dl','driver'],
 'Hospital Bill':['hospital','patient','bill','consultation'],
 'Medical Report':['diagnosis','treatment','doctor','medical'],
 'Repair Invoice':['invoice','repair','garage','spares','labour']}

def extract_text(path):
 text=''
 ext=os.path.splitext(path)[1].lower()
 try:
  if ext=='.pdf':
   with fitz.open(path) as doc:
    text='\n'.join(page.get_text() for page in doc)
  elif ext in ('.jpg','.jpeg','.png'):
   text=pytesseract.image_to_string(Image.open(path))
 except Exception as exc:
  return '',f'OCR unavailable: {exc}'
 return text,None

def classify(text):
 low=text.lower(); scores={name:sum(k in low for k in words) for name,words in KEYWORDS.items()}
 best=max(scores,key=scores.get)
 return (best if scores[best]>0 else 'Other',min(95,25+scores[best]*20))

def fields(text):
 out={}
 regs={'policy_number':r'(?:policy(?:\s*(?:no|number))?)[\s:#-]*([A-Za-z0-9-]+)','vehicle_number':r'\b([A-Z]{2}\d{2}[A-Z]{1,2}\d{4})\b','claim_amount':r'(?:claim|invoice|total|amount)[^\d]*(₹?\s*[\d,]+(?:\.\d+)?)','invoice_number':r'(?:invoice(?:\s*(?:no|number))?)\s*[:#-]?\s*([A-Za-z0-9-]+)','location':r'(?:location|accident at|place)[\s:]+([^\n]+)','accident_date':r'(?:incident|accident|date)[\s:]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'}
 for key,pat in regs.items():
  m=re.search(pat,text,re.I)
  if m: out[key]=m.group(1).strip()
 return out
