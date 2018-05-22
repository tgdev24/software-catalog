import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
	__tablename__ = 'user'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	email = Column(String(250), nullable=False)
	picture = Column(String(250))

	@property
	def serialize(self):
		return{
			'id': self.id,
			'name': self.name,
			'email':self.email,
			'picture':self.picture
		}

class Fields(Base):
	__tablename__ = 'specialties'
	
	id = Column(Integer, primary_key= True)
	name = Column(String(250), nullable= False)
	user_id = Column(Integer, ForeignKey('user.id'))	
	user = relationship(User)

	@property
	def serialize(self):
		return{
			'id': self.id,
			'name': self.name,
			'user_id':self.user_id
		}

class MenuItem(Base):
	__tablename__ = 'menu_item'
	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable= False)
	description = Column(String(1000))
	website = Column(String(500))
	image = Column(String(1000))
	specialty_id = Column(Integer, ForeignKey('specialties.id'))
	specialty = relationship(Fields)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	@property
	def serialize(self):
		return {
			'id': self.id,
			'name': self.name, 
			'description': self.description,
			'website': self.website,
			'image': self.image,
			'specialty_id': self.specialty_id,
			'user_id': self.user_id
		}

engine = create_engine('sqlite:///catalogwithusers.db')
Base.metadata.create_all(engine)