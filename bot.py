from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import time
import logging
from telegram.ext import Updater, MessageHandler, Filters, Handler
from telegram import Bot
import json
import os



logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

WAITING = 3

with open("config.json", "r") as read_file:
    config = json.load(read_file)


def update_config():
    with open("config.json", "w") as write_file:
        json.dump(config, write_file)

def check_center(bot, update, chat_id):
    logging.log(logging.INFO, "Setup Driver")
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(30)
    base_url = "https://www.google.com/"
    verificationErrors = []
    accept_next_alert = True

    logging.log(logging.INFO, "Going to Website")
    driver.get("https://www.ets.org/mygre")
    time.sleep(10)

    logging.log(logging.INFO, "Fill and Login")
    driver.find_element_by_id("username").clear()
    driver.find_element_by_id("username").send_keys(config["GRE_USER"])
    driver.find_element_by_id("password").clear()
    driver.find_element_by_id("password").send_keys(config["GRE_PASS"])
    driver.find_element_by_name("submitSign").click()
    time.sleep(10)

    logging.log(logging.INFO, "Go to Centers")
    driver.find_element_by_link_text("Register / Find Test Centers, Dates").click()
    time.sleep(5)

    logging.log(logging.INFO, "Fill Center Info")
    driver.find_element_by_id("testId-kinput").click()
    time.sleep(1)
    driver.find_element_by_xpath("//ul[@id='testId_listbox']/li[2]").click()
    driver.find_element_by_id("location").click()
    driver.find_element_by_id("location").clear()
    driver.find_element_by_id("location").send_keys("Tehran, Tehran Province, Iran")
    # For Next Month:
    # driver.find_element_by_xpath("//div[@id='testCenter-Carousel']/a[2]").click() 
    driver.find_element_by_id("findTestCenterButton").click()
    time.sleep(5)

    found = False;
    while not found:
        try:
            driver.find_element_by_id("testCenterErrorMsg")
            logging.log(logging.INFO, "No Place !")
        except:
            try:
                driver.find_element_by_id("show-map-button") 
                logging.log(logging.INFO, "FOUUUUUNNND")
                bot.send_message(chat_id=chat_id, text="Center Is Available!!!")
                bot.send_message(chat_id=chat_id, text="Go and Check Your Profile!!!")
                bot.send_message(chat_id=chat_id, text="Hurry up!!!")
            except:
                pass
            break;

        time.sleep(WAITING)
        driver.find_element_by_id("findTestCenterButton").click()
    
    driver.quit()


updater = Updater(config["TOKEN"])
dispatcher = updater.dispatcher


def get_center_availability_handler(bot, update):
    if config["AUTH"]["ENABLE"]:
        authenticate(bot, update)
    get_centers(bot, update)


def get_centers(bot, update):
    chat_id = update.effective_message.chat_id
    message_id = update.effective_message.message_id
    username = update.message.chat.username
    logging.log(logging.INFO, f'start to query message {message_id} in chat:{chat_id} from {username}')
    if update.effective_message.text == "start_check":
        bot.send_message(chat_id=chat_id, text="From Now Centeres will be Checked for You!") 
        while True:
            check_center(bot, update, chat_id)



def authenticate(bot, update):
    username = update.message.chat.username
    chat_id = update.effective_message.chat_id
    if update.effective_message.text == config["AUTH"]["PASSWORD"]:
        logging.log(logging.INFO, f'new sign in for user {username}, {chat_id}')
        config["AUTH"]["USERS"].append(chat_id)
        update_config()
        bot.send_message(chat_id=chat_id, text="You signed in successfully. Enjoy🍻")
        raise Exception("Signed In")
    elif chat_id not in config["AUTH"]["USERS"]:
        logging.log(logging.INFO, f'not authenticated try')
        bot.send_message(chat_id=chat_id, text="⚠️This bot is personal and you are not signed in. Please enter the "
                                               "password to sign in. If you don't know it contact the bot owner. ")
        raise Exception("Not Signed In")


handler = MessageHandler(Filters.text, get_center_availability_handler)
dispatcher.add_handler(handler=handler)

POLLING_INTERVAL = 0.8
updater.start_polling(poll_interval=POLLING_INTERVAL)
updater.idle()


