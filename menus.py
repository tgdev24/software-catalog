from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Fields, Base, MenuItem

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

session.query(MenuItem).delete()
session.commit()

session.query(Fields).delete()
session.commit()

field1 = Fields(name="Front-End Development")

menuItem1 = MenuItem(name = "HTML", description = "Markup Language used to display the content of a website in a browser", website = "https://www.w3schools.com/html/", image = "html5.png", specialty = field1)
session.add(menuItem1)
session.commit()

menuItem2 = MenuItem(name = "CSS", description = "Style sheet language used for describing the presentation of a document written in a markup language like HTML. It allows one to describe colors, layout, fonts which can be displayed on different width devices.", website = "https://www.w3schools.com/css/", image = "css.jpg", specialty = field1)
session.add(menuItem2)
session.commit()

session.add(field1)
session.commit()

field2 = Fields(name="Back-End Development")

menuItem3 = MenuItem(name = "Flask", description = "Python framework to help build a solid web foundation which then can be used to add extensions. Lightweight and modular design allows developers to plug into any ORM, use handle HTTP requests, run a development server, and more.", website = "http://flask.pocoo.org/", image = "flask.png", specialty = field2)
session.add(menuItem3)
session.commit()

menuItem4 = MenuItem(name = "Django", description = "Full stack python framework which includes authentication, URL routing, template engine, object relational mapper, and database schema migrations.", website = "https://www.djangoproject.com/start/overview/", image = "django.png", specialty = field2)
session.add(menuItem4)
session.commit()

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