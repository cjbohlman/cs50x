import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL")) # database engine object from SQLAlchemy that manages connections to the database
db = scoped_session(sessionmaker(bind=engine))    # create a 'scoped session' that ensures different users' interactions with the


f = open("books.csv")
reader = csv.reader(f)
for isbn, title, author, year in reader: # loop gives each column a name
    if (isbn=="isbn" and title=="title" and author=="author" and year=="year"):
        # column names
        continue
    #print(f"Added book: {isbn} {title} {author} {year}.")

    db.execute("INSERT INTO books (fstrisbn, fstrtitle, fstrauthor, fi16year) VALUES (:isbn, :title, :author, :year)",
    {"isbn": isbn, "title": title, "author": author, "year": int(year)}) # substitute values from CSV line into SQL command, as per this dict

db.commit() # transactions are assumed, so close the transaction finished