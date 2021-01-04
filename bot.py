#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import time
import os
import hashlib
import logging
from telegram import Update
from telegram.constants import MESSAGEENTITY_URL, CHATACTION_UPLOAD_VIDEO
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

cwd = os.getcwd()


def download_tiktok_video(url: str) -> str:
    '''
    Download a TikTok video

    Parameters:
            url (str): any url that leads to a tik tok

    Returns:
            path (str): Absolute path to the downloaded file
    '''
    options = Options()
    options.add_argument('--headless')

    profile = FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2)
    profile.set_preference('browser.download.dir', cwd)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk',
                           'video/mp4, application/octet-stream, mp4')
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.useDownloadDir', True)
    profile.set_preference(
        'browser.download.viewableInternally.enabledTypes', '')
    profile.set_preference('media.play-stand-alone', False)
    profile.set_preference('webdriver.load.strategy', 'fast')
    profile.set_preference('browser.tabs.remote.autostart.2', False)

    driver = webdriver.Firefox(profile, options=options)

    driver.get(url)
    time.sleep(1)
    elem = driver.find_element(By.TAG_NAME, 'video')
    src = elem.get_attribute('src')
    script = f'''
        var link = document.createElement('a');
        link.setAttribute('download', 'download');
        link.setAttribute('href', '{src}');
        link.click();
        '''
    driver.execute_script(script)

    driver.quit()

    with open('mp4', 'rb') as f:
        file_hash = hashlib.blake2b()
        while chunk := f.read(8192):
            file_hash.update(chunk)

    new_name = file_hash.hexdigest()+'.mp4'
    os.rename('mp4', new_name)
    return os.path.abspath(new_name)


def reply_video(update: Update, context: CallbackContext) -> None:
    try:
        for ent in update.message.entities:
            if ent.type == 'url':
                url = update.message.parse_entity(ent)
                update.message.chat.send_action(CHATACTION_UPLOAD_VIDEO)
                file = download_tiktok_video(url)
                update.message.chat.send_video(video=open(file, 'rb'))
    except Exception as exception:
        update.message.chat.send_message(text=str(exception))


def main():
    token = os.getenv('TELEGRAM_TOKEN')
    updater = Updater(token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.text & Filters.entity(
        MESSAGEENTITY_URL) & Filters.regex('tiktok\.com\/[-A-Za-z0-9+/=]+'), reply_video))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
