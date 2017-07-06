"""game info model"""


from sqlalchemy import Column, Date, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# create base class of the object
Base = declarative_base()


class GameInfo(Base):
    # name of table:
    __tablename__ = 'game_infos'

    # struct of table
    cid = Column(String(36), primary_key=True)
    name = Column(String())
    genre = Column(String())
    content_type = Column(String())
    provider = Column(String())
    release_date = Column(Date())
    num_of_reviews = Column(Integer())
    price = Column(Integer())
    url = Column(String())
    update_datetime = Column(DateTime())

    def __repr__(self):
        return "<GameInfo(name='%s')>" % (self.name)


def get_session(database_name = "game_info"):
    from sqlalchemy import create_engine
    import os
    game_info_db_path = os.path.join(os.path.split(
        os.path.realpath(__file__))[0], database_name + ".db")
    engine = create_engine('sqlite:///' + game_info_db_path, echo=False)
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker()
    Session .configure(bind=engine)
    Base.metadata.create_all(engine)
    return Session()


def main():
    get_session()


if __name__ == '__main__':
    main()
