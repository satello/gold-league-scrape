import os
from flask_sqlalchemy import SQLAlchemy
from webapp.memory_model import MemoryModel


db = SQLAlchemy()
mem_db = MemoryModel()
