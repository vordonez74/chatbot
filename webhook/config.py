# config.py
import os

class Config:
        SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:changeme@localhost/postgres'
        SQLALCHEMY_TRACK_MODIFICATIONS = False

