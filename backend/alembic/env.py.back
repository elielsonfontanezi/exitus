# backend/alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# ADICIONAR ESTAS LINHAS:
import sys
import os
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.database import db

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ADICIONAR ESTA LINHA:
# Configurar a URL do banco a partir da aplicação Flask
app = create_app()
config.set_main_option('sqlalchemy.url', app.config['SQLALCHEMY_DATABASE_URI'])

# add your model's MetaData object here
# SUBSTITUIR por:
target_metadata = db.metadata

# ... resto do arquivo permanece igual
