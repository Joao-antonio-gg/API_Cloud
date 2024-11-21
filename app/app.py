import os
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import jwt
from datetime import datetime, timedelta
import bcrypt
import requests
from fastapi.middleware.cors import CORSMiddleware

SECRET_KEY = os.getenv("SECRET_KEY", "SENHA!")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db/dbname")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Pydantic models
class User(BaseModel):
    nome: str
    email: str
    senha: str

class Login(BaseModel):
    email: str
    senha: str

# SQLAlchemy model
class UserDB(Base):  # Modelo SQLAlchemy
    __tablename__ = "users"
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    nome = Column(String(100))
    email = Column(String(100), unique=True)
    senha = Column(String(100))  # A senha será armazenada como string (hash)

app = FastAPI()

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Função para criar o token JWT
def creat_token(data: dict):
    encode = data.copy()
    encode.update({"iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependência para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependência para verificar o token JWT
oauth2_scheme = HTTPBearer()

def jwtBearer(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Token inválido")
    return payload

# Função para verificar o token
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Token inválido")

# Rota de registro de usuário
@app.post("/registrar")
def registrar(user: User, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=409, detail="Email já registrado")
    
    # Hasheando a senha do usuário
    hashed_password = bcrypt.hashpw(user.senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Criar um novo usuário no banco de dados
    new_user = UserDB(nome=user.nome, email=user.email, senha=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Gerando o token JWT
    token_data = {"email": user.email, "nome": user.nome}
    jwt_token = creat_token(token_data)

    return {"jwt": jwt_token}

# Rota de login
@app.post("/login")
def login(user: Login, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.email == user.email).first()
    if not db_user or not bcrypt.checkpw(user.senha.encode('utf-8'), db_user.senha.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")

    # Gerar o token JWT após sucesso no login
    token_data = {"email": user.email, "nome": db_user.nome}
    jwt_token = creat_token(token_data)

    return {"jwt": jwt_token}

# Rota para consultar o valor do dólar
@app.get("/consultar")
def consultar(request: Request, token: str = Depends(jwtBearer)):
    # O token já foi verificado na função jwtBearer
    url = "https://economia.awesomeapi.com.br/last/USD-BRL"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro ao consultar a API")

    try:
        data = response.json()
        high = data["USDBRL"]["high"]
        low = data["USDBRL"]["low"]
    except (KeyError, ValueError):
        raise HTTPException(status_code=500, detail="Erro ao processar a resposta da API")

    return {"high": high, "low": low}

# Criando as tabelas no banco de dados
Base.metadata.create_all(bind=engine)
