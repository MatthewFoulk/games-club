from bs4 import BeautifulSoup
import requests
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects import postgresql
import time
import openpyxl
from selenium import webdriver


def main():
    
    # Setting up database
    db_base = declarative_base()

    class Game(db_base):
        __tablename__ = "test_board_games"

        id = Column('id', Integer, primary_key=True)
        name = Column('name', String, unique = True)
        copies = Column('copies', Integer)
        game_url = Column('game_url', String)
        min_player = Column('min_player', Integer)
        max_player = Column('max_player', Integer)
        min_time = Column('min_time', Integer)
        max_time = Column('max_time', Integer)
        min_age = Column('min_age', Integer)
        category = Column('category', String)
        difficulty_color = Column('difficulty_color', String)
        description = Column('description', String)
        video_url = Column('video_url', String)

    engine = create_engine('sqlite:///games_club.db', echo=False)
    db_base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)

    # Opening spreadsheet
    spreadsheet = openpyxl.load_workbook('Game Inventory.xlsx')
    board_games = spreadsheet['Board Games']
    row_counter = 2 # Start at two because of titles

    # Used to find the game page url
    base_url = 'https://boardgamegeek.com'
    base_search = '/geeksearch.php?action=search&objecttype=boardgame&q='

    # Set up driver for selenium
    driver = webdriver.Firefox()

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
        game.url = get_game_url(base_url, base_search, game.name)

        # Allow the information to load on games webpage
        driver.get(game.url)
        time.sleep(1) # TODO test to see if this is necessary, or if it can be lowered

        # Prepare to scrape information from games webpage
        game_page_html = driver.page_source
        game_page_content = BeautifulSoup(game_page_html, "html.parser")

        game.min_player = get_min_player(game_page_content)
        game.max_player = get_max_player(game_page_content)
        game.min_time = get_min_time(game_page_content)
        game.max_time = get_max_time(game_page_content)
        game.min_age = get_min_age(game_page_content)
        game.description = get_description(game_page_content)

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

def get_game_url(base_url, base_search, name):
    game_search = base_url + base_search + name.replace(" ", "%20")
    search_response = requests.get(game_search, timeout = 5)
    search_content = BeautifulSoup(search_response.content, "html.parser")
    return base_url + search_content.find('div', {'id' : 'results_objectname1'}).find('a')['href']

def get_min_player(game_page_content):    
    return game_page_content.find('span', {'ng-if' : 'min > 0'}).text

def get_max_player(game_page_content):
    try:
        return game_page_content.find('span', {'ng-if' : 'max>0 && min != max'}).text.replace('–', '')

    except AttributeError:
        return get_min_player(game_page_content)

def get_min_time(game_page_content):
    return game_page_content.find_all('span', {'ng-if': 'min > 0'})[1].text

def get_max_time(game_page_content):
    try:
        return game_page_content.find_all('span', {'ng-if': 'max>0 && min != max'})[1].text.replace('–', '')

    except IndexError:
        return get_min_time(game_page_content)
    
def get_min_age(game_page_content):
    return game_page_content.find('span', {'ng-if' : '::geekitemctrl.geekitem.data.item.minage > 0'}).text.replace('+', '')

def get_description(game_page_content):
    return game_page_content.find('p').text

if __name__ == "__main__":
    main()