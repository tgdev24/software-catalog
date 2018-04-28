import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Fields(Base):
	__tablename__ = 'specialties'
	id = Column(Integer, primary_key= True)
	name = Column(String(250), nullable= False)

	@property
	def serialize(self):
		return{
			'id': self.id,
			'name': self.name
		}

class MenuItem(Base):
	__tablename__ = 'menu_item'
	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable= False)
	description = Column(String(1000))
	website = Column(String(500))
	image = Column(String(500))
	specialty_id = Column(Integer, ForeignKey('specialties.id'))
	specialty = relationship(Fields)

	@property
	def serialize(self):
		return {
			'id': self.id,
			'name': self.name, 
			'description': self.description,
			'website': self.website,
			'image': self.image,
		}

engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)