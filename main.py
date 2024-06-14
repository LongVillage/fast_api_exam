from fastapi import FastAPI, HTTPException, Depends, Security, Header
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import base64
from pydantic import BaseModel
from typing import List
import csv
import random

app = FastAPI()
security = HTTPBasic()

credentials_dict = {
    "alice": "wonderland",
    "bob": "builder",
    "clementine": "mandarine"
}

admin_credentials = {
        "admin": "4dm1N"
        }

class QuestionCreateRequest(BaseModel):
    question: str
    subject: str
    correct: List[str]
    use: str
    responseA: str
    responseB: str
    responseC: str
    responseD: str

class QuizRequest(BaseModel):
    test_type: str
    categories: List[str]
    number_of_questions: int


def add_question_to_csv(question_data: dict, file_path: str):
    with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['question', 'subject', 'correct', 'use', 'responseA', 'responseB', 'responseC', 'responseD']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(question_data)



def verify_admin_credentials(username: str, password: str):
    if username in admin_credentials and password == admin_credentials[username]:
        return True
    else:
        raise HTTPException(status_code=401, detail="Invalid admin username or password.")


def load_questions(file_path: str = 'questions.csv'):
    question = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
       reader = csv.DictReader(csvfile)
       i=0
       for row in reader:
           if i<5:
               question.append(row)
               i=+i
    return question

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username in credentials_dict and credentials.password == credentials_dict[credentials.username]:
        return True
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password.")

@app.get("/verify")
def verify():
    return {"message": "l'API est fonctionnelle."}

@app.post("/generate_quiz")
def generate_quiz(request: QuizRequest, credentials: HTTPBasicCredentials = Depends(security)):
    if not verify_credentials(credentials):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    # Filtrer les questions en fonction du type de test et des catégories
    filtered_questions = [
        q for q in questions if q['use'] == request.test_type and q['subject'] in request.categories
    ]
    
    # Vérifier si on a assez de questions
    if len(filtered_questions) < request.number_of_questions:
        raise HTTPException(status_code=400, detail="Pas assez de questions disponibles pour ces critères.")
    
    # Retourner un nombre aléatoire de questions
    selected_questions = random.sample(filtered_questions, request.number_of_questions)
    
    return selected_questions


questions = load_questions()

@app.post("/create_question")
def create_question(
    request: QuestionCreateRequest,
    admin_username: str = Header(...),
    admin_password: str = Header(...)
):
    if not verify_admin_credentials(admin_username, admin_password):
        raise HTTPException(status_code=401, detail="Invalid admin username or password.")
    
    question_data = request.dict()
    question_data["correct"] = ",".join(request.correct)
    
    add_question_to_csv(question_data, 'questions.csv')
    
    return {"message": "Question créée avec succès."}


@app.get("/questions")
def get_questions():
    return questions
