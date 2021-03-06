"""
Step 1:
    IN: URL
    OUT: RAW HTML
    PROCESS:

STEP 2:
    IN: RAW HTML
    OUT: LIST

STEP 3:
    IN: LIST
    OUT: LISTS IN EN, CZ

STEP 4:
    Save to database


TODO: NLP/ML confidence rating of text being daily menu
"""

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from time import sleep
from bs4 import BeautifulSoup as bs

from urllib import request
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
from jinja2 import Template
import requests
import json
import logging
import os, sys, traceback
from unidecode import unidecode
from time import sleep

# from restaurants.models import Restaurant

from facebook_scraper import get_posts

chromedriver_path = r'C:\Users\kotek\Documents\KOTEK.CO\youtube_subscriber\chromedriver'

Scraper().get(url="https://www.facebook.com/Pastva%20/")

s = Scraper()           
x = s.get(url="http://www.prostor.je", selector="#daily-menu ul")

url = "http://www.prostor.je"
selector = "#daily-menu ul li"

# TEST
def test():
    options = Options()
    browser = Chrome(options=options, executable_path=chromedriver_path)
    browser.get(url)
    elems = browser.find_elements_by_css_selector(selector)
    elems
    

class Scraper(object):

    def __init__(self):
        """Restaurant as DB object?"""

        self.options = Options()
        # self.options.headless = True
        self.browser = Chrome(options=self.options, executable_path=chromedriver_path)

    def get(self, restaurant=None, url=None, selector=None):

        if 'facebook' in url:
            print("Facebook detected.")
            response = self.facebook(url)
        else:
            print("Facebook not detected.")
            response = self.default(url, selector)
        
        return response

    def facebook(self, url):
        fb_slug = url.lower().rstrip('/').rsplit('/', maxsplit=1)[-1]
        posts = get_posts(fb_slug, pages=3)
        for post in posts: #TODO: Fix so that it ignores pinned posts? Or looks for today's date/day name first?
            if 'menu' in post['text'].lower():
                return post['text']

    def default(self, url, selector):

        print(url, selector)

        self.browser.get(url)
        sleep(1)
        elems = self.browser.find_elements_by_css_selector(selector)
        sleep(1)
        print(elems)
        for elem in elems:
            print(elem.text)

        text_list = [elem.text for elem in elems]

        print(text_list)
        text = text_list


        return text


    def add_menu(self, id, language, name, url, selector, n=0, javascript=False, facebook=False, location=None):
        """
        id          :: id of the restaurant, used for grouping and hiding restaurants.
        name        :: name of the restaurant
        url         :: the URL where the menu can be found
        selector    :: CSS selector to find menu on page
        n           :: specifies how to handle results
        javascript  :: use headless chrome to render page - when content is loaded by JS.
        n = 0 [DEFAULT]
        Gets the first element in the response.
        n = -1
        Combines the text in all found elements.
        n = range(x, y)
        Fetches tech from elements x through y from the response."""

        print("[{}] Fetching menu for {}".format(id, name.ljust(30)), end="")
        try:

            if 'facebook' in url:
                print("Is facebook..")
                self.text = self.facebook(url)
                print(self.text)
            else:
                raw_html = self.html(url)
                # Get the raw menu from URL
                text_raw = self.scrape_menu( url, selector)

                # Convert raw text to a list
                text_list = self.convert_to_list( text_raw, n)

            # Checks if menu is for more days, extracts today's menu.
            text_menu = self.get_today_items(text_list)

            # Remove any short list items (i.e. prices)
            # Trim non alpha values from start and end of string
            # Capitalize each list item
            count_letters = lambda x: len( [char for char in x if char.isalpha() ] )
            text_menu = [ self.trim(t).capitalize() for t in text_menu if count_letters(t) > 5]

            # Remove duplicates
            text_menu = list( set( text_menu ) )

            # Translate to Czech / English

            if not text_menu:
                raise Exception("No data returned.")

            if language == 'cs':
                text_menu_cs = text_menu
                text_menu_en = translator.translate(text_menu, 'cs', 'en')
            elif language == 'en':
                text_menu_en = text_menu
                text_menu_cs = translator.translate(text_menu, 'en', 'cs')

            if not isinstance(text_menu, list):
                print('ERROR: NOT A LIST ({})'.format(type(text_menu)))
                raise Exception("Expected list, got {}".format(type(text_menu)))

            print("OK!")
            return True

        except Exception as e:
            print("Couldn't get menu for {}. Error: {}".format(name, e))
            # print('-'*60)
            # traceback.print_exc(file=sys.stdout)
            # print('-'*60)

            # Dummy values on failure
            text_menu = ["Menu not found."]
            text_menu_cs = ["Menu nenalezeno."]
            text_menu_en = ["Couldn't find menu."]

        finally:
            self.menus.append(
                {
                    'id':id,
                    'name':name,
                    'url':url,
                    'location': location,
                    'menu':text_menu,
                    'menu_cs': text_menu_cs,
                    'menu_en': text_menu_en,
                })

    def scrape_menu(self, url, selector, javascript):
        try:
            # Use Selenium and headless Chrome browswer to render JS generated pages.
            if javascript:
                options = Options()
                options.headless = True
                driver = webdriver.Chrome(options=options, executable_path=r'/usr/bin/chromedriver')
                driver.get(url)
                sleep(1)
                html = driver.page_source
                soup = bs(html, 'lxml')
                selected = soup.select(selector)
                return selected
            else:
                with requests.get(url, timeout=9) as response:
                    response.encoding = 'UTF-8'
                    html = response.text
                    soup = bs(html, 'lxml')
                    selected = soup.select(selector)

                return selected
        except:
            raise Exception("Unable to retrieve menu from URL. ({})".format(url))

    def convert_to_list(self, raw_text, n=0):

        if not isinstance(raw_text, list):
            raw_text2 = [raw_text]

        if n == -1:
            text = "\n".join([item.get_text() for item in raw_text])

        elif isinstance(n, range):
            text = []
            for i in n:
                text.append( self.clean(raw_text[i].get_text()) )
            text = "\n".join(text)

        else:
            text = raw_text[n]
            text = str(text).replace("<br/>", "\n")
            text = bs(text, 'lxml').get_text()

        text = [ t for t in text.split("\n") if len(t) > 0]

        return text

    # Trim string on both ends - can it be replaced by the trim_junk function??
    @staticmethod
    def trim(txt):

        if not isinstance(txt, str):
            return txt

        def trim_left(txt):
            if not txt[0].isalnum():
                return lunchScraper.trim(txt[1:])
            else:
                return txt

        def trim_right(txt):
            if not txt[-1].isalnum():
                return lunchScraper.trim(txt[:-1])
            else:
                return txt

        return trim_left(trim_right(txt))

    def send_messages_html(self, email=None):

        if email:
            users = controller.User()
            user = users.get(email=email)
            if not user:
                user = users.add(email, verify=True)
            recipients = [user]
        else:
            recipients = self.get_recipients()

        auth = ("api", self.settings.MAIL_API_KEY)

        notice = controller.Email.get_notice()

        send_counter = 0

        recipients = [recipient for recipient in recipients if recipient['verified'] is not False]

        for recipient in recipients:

            try:

                print( "Sending email to {}".format(recipient['email'].ljust(40, ".") ), end="")

                # Get menus for preferences of given user
                foo = [r for r in self.menus if str(r['id']) in recipient['preferences']]

                def get_menus():
                    userMenu = []
                    for preference in recipient['preferences']:
                        for menu in self.menus:
                            if str(menu['id']) == preference:
                                userMenu.append( menu )
                                continue
                    return userMenu
                
                userMenus = get_menus()
                print(userMenus)
                
                # for each user preferences, get the corresponding 

                # Define language so it corresponds to dictionary keys of languages in menu dict
                if recipient['language'] in ['cs', 'en']: # Check if language is set for user.
                    language = str('menu_' + recipient['language'])
                else: # Use original menu language
                    language = 'menu'
                for menu in userMenus:
                    menu['menu'] = menu[language]

                data = {
                    'title': "Daily Menu for {}".format(datetime.now().strftime("%A, %d-%b")),
                    'notice': notice,
                    'recipient': {
                        'email': recipient['email'],
                        'url': SETTINGS.URL + "/edit?token=" + recipient['token'],
                    },
                    'menus': userMenus,
                    'language': language,
                }

                # Generate html email template for user with given data
                email_html = self.render_email('master.html', data)

                config = {
                    "from": self.settings.FROM,
                    "to": recipient['email'],
                    "subject": "Daily Menu for {}".format(datetime.now().strftime("%A, %d-%b")),
                    "html": email_html,
                }
                r = requests.post(self.settings.MAIL_URL, auth=auth, data=config)

                if r.status_code == 200:
                    send_counter += 1
                    print("OK!")
                else:
                    print("FAILED ({})".format(str(r.status_code)))

            except Exception as e:
                print("ERROR: {}".format(str(e)))


        print("{} / {} Emails sent successfully.".format( send_counter, len(recipients) ) )

        return True

    def get_recipients(self):

        file = SETTINGS.SUBSCRIBERS

        with open(file, 'r') as f:
            subscribers = json.load(f)
        return subscribers

    def render_email(self, template, data):

        with open("templates/"+template, 'r') as html:
            html = html.read()
            template = Template(html)
            html = template.render(data=data)

        return html

    def scrape_restaurants(self, id=None):
        restaurants.scrape(self, id)

    @staticmethod
    def wday_to_text(weekday):
        """
        Converts int of weekday into list of text versions of given day.
        """
        if weekday == 0:
            return ["pondeli",  "pondělí",  "pondělní",                 "monday"]
        elif weekday == 1:
            return ["utery",    "úterý",    "úterní",                   "tuesday"]
        elif weekday == 2:
            return ["streda",   "středa",   "středeční",    "středu",   "wednesday"]
        elif weekday == 3:
            return ["ctvrtek",  "čtvrtek",  "čtvrteční",                "thursday"]
        elif weekday == 4:
            return ["patek",    "pátek",    "páteční",                  "friday"]
        elif weekday == 5:
            return ["sobota",   "sobota",   "sobotní",      "sobotu",   "saturday"]
        elif weekday == 6:
            return ["nedele",   "neděle",   "nedělní",      "neděli",   "sunday"]
        else:
            return [""]

    @staticmethod
    def day_found(text, day):
        for lang in day:
            if unidecode( text.lower( ) ).find( lang ) >= 0:
                return True

    def get_today_items(self, menu_list):
        """
        Check if menu is for multiple days, extract and return today's menu items.
        """

        weekday = datetime.today().weekday()

        today, tomorrow = self.wday_to_text(weekday), self.wday_to_text(weekday+1)

        menu_text = ";".join(menu_list).lower()

        # Check if at today is mentioned on the menu. If yes, continue.
        if not self.day_found(menu_text, today):
            return menu_list

        start, end = None, None
        for i, item in enumerate(menu_list):
            if self.day_found(item, today):
                start = i + 1
            elif self.day_found(item, tomorrow):
                end = i

        return menu_list[start:end]

    def save_menu(self):

        filename = "data/menu.json"
        print("Attempting to save menu to {}..".format( os.path.abspath(filename)) )

        data = {
            'date': datetime.now().strftime("%A (%Y-%m-%d)"),
            'menus': self.menus
        }

        try:
            with open(filename, "w+") as f:
                json.dump(data, f)
            print ("OK!")
            return True
        except Exception as e:
            print ("Error occured during saving:", e)
            return False

    @staticmethod
    def clean(string):
        return "".join([char for char in string if char.isalnum() or char == " "])

    @staticmethod
    def trim_junk(text):
        def find_last_letter(text):
            last_letter = 0
            for i, letter in enumerate(text):
                if letter.isalpha():
                    last_letter = i + 1
            return last_letter

        return text[:find_last_letter(text)]