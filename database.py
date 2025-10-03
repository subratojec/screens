from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Update this with your actual database URL
DATABASE_URL = "postgresql://postgres:mysecretpassword@localhost:5432/postgres"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
	__tablename__ = "users"
	id = Column(Integer, primary_key=True, index=True)
	username = Column(String, unique=True, index=True, nullable=False)
	password = Column(String, nullable=False)
	email = Column(String, unique=True, index=True, nullable=False)
	phonenumber = Column(String, nullable=False)
	website = Column(String, nullable=False)
	adharid = Column(String, nullable=False)

def create_tables():
	Base.metadata.create_all(bind=engine)

def drop_tables():
    Base.metadata.drop_all(bind=engine)

def save_user(username: str, password: str, email: str, phonenumber: str, website: str, adharid: str):
	db = SessionLocal()
	existing_user = db.query(User).filter((User.username == username) | (User.email == email)).first()
	if existing_user:
		result = None
		if getattr(existing_user, 'username', None) == username:
			result = "username"
		elif getattr(existing_user, 'email', None) == email:
			result = "email"
		db.close()
		return result
	user = User(
		username=username,
		password=password,
		email=email,
		phonenumber=phonenumber,
		website=website,
		adharid=adharid
	)
	db.add(user)
	db.commit()
	db.refresh(user)
	db.close()
	return user
