from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from src.database import SessionLocal
from src.models import Case
from src.metrics import customer_effort, first_response_minutes, resolution_minutes, silent_wait_minutes

cases = SessionLocal().query(Case).all()
X=[]; y=[]
for c in cases:
    X.append([first_response_minutes(c),silent_wait_minutes(c),sum(i.transfer_flag for i in c.interactions),bool(c.feedback and c.feedback.repeat_contact_flag),sum(not p.promise_met for p in c.promises),resolution_minutes(c),c.escalation_flag,customer_effort(c)])
    y.append(int(c.feedback.dsat_flag))
train_x,test_x,train_y,test_y=train_test_split(X,y,test_size=.25,random_state=42,stratify=y)
model=LogisticRegression(max_iter=1000).fit(train_x,train_y); predicted=model.predict(test_x)
print("Experimental ML Benchmark")
print({"accuracy":round(accuracy_score(test_y,predicted),3),"precision":round(precision_score(test_y,predicted,zero_division=0),3),"recall":round(recall_score(test_y,predicted,zero_division=0),3),"f1":round(f1_score(test_y,predicted,zero_division=0),3)})
print("confusion_matrix", confusion_matrix(test_y,predicted).tolist())
print("feature_coefficients", model.coef_[0].round(4).tolist())

