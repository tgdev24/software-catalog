import os
import sys
from sqlalchemy import Column, Foreign, Integer, String
from sqlalchemy.ext.declative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class