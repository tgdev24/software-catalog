from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Fields, Base, MenuItem

engine = create_engine('sqlite:///catalogwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

session.query(MenuItem).delete()
session.commit()

session.query(Fields).delete()
session.commit()

field1 = Fields(name="Front-End Development")

menuItem1 = MenuItem(name = "HTML", description = "Markup Language used to display the content of a website in a browser", website = "https://www.w3schools.com/html/", image = "https://www.w3.org/html/logo/downloads/HTML5_1Color_Black.png", specialty = field1)
session.add(menuItem1)
session.commit()

menuItem2 = MenuItem(name = "CSS", description = "Style sheet language used for describing the presentation of a document written in a markup language like HTML. It allows one to describe colors, layout, fonts which can be displayed on different width devices.", website = "https://www.w3schools.com/css/", image = "http://thewebrocks.com/demos/html5-3d-css/html5.png", specialty = field1)
session.add(menuItem2)
session.commit()

menuItem9 = MenuItem(name = "ReactJS", description = "A javascript library for designing UI's with built-in XML-like markup langauge, components rendering, and virtual DOM. Mostly used for the front-end however there is react Native available for powering mobile apps and can be used with Node to power server-side apps.", website = "https://www.w3schools.com/html/", image = "https://cdn-images-1.medium.com/max/512/1*qUlxDdY3T-rDtJ4LhLGkEg.png", specialty = field1)
session.add(menuItem9)
session.commit()

menuItem8 = MenuItem(name = "Vue.js", description = "A javascript framework used to make user interfaces quickly and easily as noted by its small size as well as easy-to-understand syntax. It uses javascript so developers of other frameworks can understand and include in their projects. Lastly the MVVM architecture allows 2 way communication between back-end logic code and the graphical user interface code therefore speeding up operations using HTML block elements.", website = "https://vuejs.org/", image = "https://cdn-images-1.medium.com/max/850/1*nq9cdMxtdhQ0ZGL8OuSCUQ.jpeg", specialty = field1)
session.add(menuItem8)
session.commit()


session.add(field1)
session.commit()

field2 = Fields(name="Back-End Development")

menuItem3 = MenuItem(name = "Flask", description = "Python framework to help build a solid web foundation which then can be used to add extensions. Lightweight and modular design allows developers to plug into any ORM, use handle HTTP requests, run a development server, and more.", website = "http://flask.pocoo.org/", image = "https://bryson3gps.files.wordpress.com/2017/10/byo-jpi-logo.png", specialty = field2)
session.add(menuItem3)
session.commit()

menuItem4 = MenuItem(name = "Django", description = "Full stack python framework which includes authentication, URL routing, template engine, object relational mapper, and database schema migrations.", website = "https://www.djangoproject.com/start/overview/", image = "data:image/png;base64,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", specialty = field2)
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