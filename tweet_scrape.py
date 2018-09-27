import os
import time
import argparse
import codecs

import tqdm
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

def define_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-dt', type=int, default=0,
                        help='Driver type, supported drivers: '
                             '0 - Chrome, 1 - Firefox'
                             ' Default - 0')
    parser.add_argument('-dp', type=str, default='',
                        help='Driver path, Default "" - in this case'
                             ' driver is assumed to be specified on path')
    parser.add_argument('-src', type=str, default='./words.txt',
                        help='Source of file that contains words that needs '
                             'to be in the tweets Default - "words.txt"')
    parser.add_argument('-nst', type=int, default=50,
                        help='Load tweets for nst seconds per topic and username.'
                             ' Default=50')
    parser.add_argument('-dest', type=str, default='./tweets.txt',
                        help='Destination to which we need to store a tweet a line.'
                             ' Default="tweets.txt"')
    return parser.parse_args()

def get_data(browser, query, ns):
    base_url = u'https://twitter.com/search?q='

    browser.get(base_url + query)
    time.sleep(5)

    body = browser.find_element_by_tag_name('body')

    t_start = time.time()
    while time.time() - t_start >= ns:
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.2)

    tweets = browser.find_elements_by_class_name('tweet-text')
    return [tweet.text.encode('utf-8') for tweet in tweets]

def get_browser(cmd_args):
    if len(cmd_args.dp) == 0:
        if cmd_args.dt == 0:
            return webdriver.Chrome()
        return webdriver.Firefox()

    if cmd_args.dt == 0:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--log-level=3')
        browser = webdriver.Chrome(executable_path=args.dp, chrome_options=options)
    else:
        os.environ['MOZ_HEADLESS'] = '1'
        browser = webdriver.Firefox(executable_path=args.dp)
    return browser

def get_words(filename):
    with open(filename) as f:
        lines = f.readlines()
    return [line.strip() for line in lines]

def save_tweets(path, tweets):
    with open(path, 'w+', encoding='utf-8') as f:
        for tweet in tweets:
            f.write(tweet)
            f.write('\n')

def run(args):
    browser = get_browser(args)
    words = get_words(args.src)

    tweets = []
    for word in tqdm.tqdm(words):
        if len(word) == 0:
            continue
        cur_tweets = get_data(browser, word, args.nst)
        tweets.extend([str(tweet) for tweet in cur_tweets if word.encode('utf-8') in tweet])
    browser.close()
    save_tweets(args.dest, tweets)

if __name__ == '__main__':
    args = define_argparser()
    print('* Starting Scraper')
    t_start = time.time()
    run(args)
    print('* Scraper finished working total time taken: {}s'.format(int(time.time() - t_start)))
