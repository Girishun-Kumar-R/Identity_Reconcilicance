from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, index=True)
    phoneNumber = Column(String, nullable=True)
    email = Column(String, nullable=True)
    linkedId = Column(Integer, ForeignKey('contacts.id'), nullable=True)
    linkPrecedence = Column(String, default='primary')  # 'primary' or 'secondary'
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deletedAt = Column(DateTime, nullable=True)

    secondaries = relationship(
    'Contact',
    backref='primary_contact',
    remote_side=[id],
    lazy='joined'
)

