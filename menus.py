from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Fields, Base, MenuItem

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

session.query(Fields).delete()
session.commit()

field1 = Fields(name="Front-End Development")

menuItem1 = MenuItem(name = "HTML", description = "Markup Language used to display the content of a website in a browser", website = "https://www.w3schools.com/html/", image = "https://cdn-images-1.medium.com/max/512/1*Lk7YWiSeDYGd-ITVUXbBbA.png", specialty = field1)
session.add(menuItem2)
session.commit()

session.add(field1)
session.commit()

field2 = Fields(name="Back-End Development")
session.add(field2)
session.commit()

field3 = Fields(name="Web Design")
session.add(field3)
session.commit()

field4 = Fields(name="iOS")
session.add(field4)
session.commit()

field5 = Fields(name="Android")
session.add(field5)
session.commit()

field6 = Fields(name="Machine Learning")
session.add(field6)
session.commit()

field7 = Fields(name="Artificial Intelligence")
session.add(field7)
session.commit()

field8 = Fields(name="Robotics")
session.add(field8)
session.commit()