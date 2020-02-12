from bs4 import BeautifulSoup
import requests
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects import postgresql
import time
import openpyxl


def main():
    
    # Setting up database
    db_base = declarative_base()

    class Game(db_base):
        __tablename__ = "test_board_games"

        id = Column('id', Integer, primary_key=True)
        name = Column('name', String, unique = True)
        copies = Column('copies', Integer)
        url = Column('url', String)
        min_player = Column('min_player', Integer)
        max_player = Column('max_player', Integer)
        min_time = Column('min_time', Integer)
        max_time = Column('max_time', Integer)
        min_age = Column('min_age', Integer)
        category = Column('category', String)
        difficulty_num = Column('difficulty_num', Float)
        difficulty_color = Column('difficulty_color', String)
        description = Column('description', String)
        video_url = Column('video_url', String)

    engine = create_engine('sqlite:///games_club.db', echo=False)
    db_base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)

    # Opening spreadsheet
    spreadsheet = openpyxl.load_workbook('Game Inventory.xlsx')
    board_games = spreadsheet['Board Games']
    name = " " # Initialized for while loop
    row_counter = 2 # Start at two because of titles

    # Start session
    session = Session()

    # Scrape information from board_games spreadsheet
    while get_name(board_games, row_counter):
        game = Game() # TODO PLACE THIS IN CORRECT PLACE
        game.name = get_name(board_games, row_counter)
        game.copies = get_copies(board_games, row_counter)
        game.difficulty_color = get_difficulty_color(board_games, row_counter)
        game.category = get_category(board_games, row_counter)
        game.video_url = get_video_url(board_games, row_counter)

        row_counter += 1
        session.add(game) # TODO PLACE THIS IN CORRECT PLACE
    session.commit()

def get_name(board_games, row):
    return board_games['A' + str(row)].value

def get_copies(board_games, row):
    return board_games['E' + str(row)].value

def get_difficulty_color(board_games, row):
    
    if board_games['F' + str(row)]:
        return 'G'

    elif board_games['G' + str(row)]:
        return 'Y'
    
    elif board_games['H' + str(row)]:
        return 'R'

    else:
        return 'N/A'

def get_category(board_games, row):
    return board_games['J' + str(row)].value

def get_video_url(board_games, row):
    return board_games['L' + str(row)].value

if __name__ == "__main__":
    main()