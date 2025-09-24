from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import cards

app = FastAPI(title='ARC-Easy Quiz')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(cards.router, prefix='/card', tags=['card'])
