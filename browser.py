import os
import argparse
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from colorama import Fore


HEADERS = {
    'user-agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:83.0) Gecko/20100101 Firefox/83.0"
}


def is_valid_url(url):
    return '.' in url


def process_url(url):
    if not url.startswith("https://"):
        return 'https://' + url


def get_page_name_from_url(url):
    dotstring = urlparse(url).netloc
    return '-'.join(dotstring.split('.')[:-1])


def mark_link_text(soup):
    for link in soup.find_all('a'):
        link.string = "{}{}{}".format(Fore.BLUE, link.text.strip(), Fore.RESET)
    return soup


def get_text_content(soup):
    soup = mark_link_text(soup)
    return soup.get_text('\n', strip=True)


class Browser:

    def __init__(self, directory):
        self.dir = directory
        self.make_directory()
        self._page_history = []   #
        self._page_names = set()
        self.current_page = None

    def browse(self, page):
        if is_valid_url(page):
            page = process_url(page)
            content = self.get_website(page)
            self.save_website(page, content)
            self.show_page(content)
        elif self.has_visited(page):
            content = self.load_website(page)
            self.show_page(content)
        else:
            raise ValueError("Incorrect URL")

    def has_visited(self, page_name):
        return page_name in self._page_names

    def make_directory(self):
        if not os.access(self.dir, os.F_OK):
            os.mkdir(self.dir)

    def get_file_path(self, page_name):
        return os.path.join(self.dir, page_name)

    def save_website(self, url, content):
        pagename = get_page_name_from_url(url)
        with open(self.get_file_path(pagename), 'w', encoding='utf-8') as f:
            print(content, file=f)
        self._page_names.add(pagename)
        if self.current_page is not None:
            self._page_history.append(self.current_page)
        self.current_page = pagename

    @staticmethod
    def get_website(url):
        response = requests.get(url, headers=HEADERS)
        if response:
            soup = BeautifulSoup(response.text, 'html.parser')
            return get_text_content(soup)
        raise ValueError("Incorrect URL")

    def load_website(self, page_name):
        file_path = self.get_file_path(page_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if self.current_page is not None:
            self._page_history.append(self.current_page)
        self.current_page = page_name
        return content

    def back(self):
        try:
            page_name = self._page_history.pop()
            self.current_page = page_name
            content = self.load_website(page_name)
            self.show_page(content)
        except IndexError:
            pass

    @staticmethod
    def show_page(content):
        print(content, end='\n')

    def exit(self):
        pass


def main():
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument('directory')
    args = my_parser.parse_args()

    browser = Browser(directory=args.directory)

    while True:
        user_input = input(">")
        if user_input == 'exit':
            browser.exit()
            break
        elif user_input == 'back':
            browser.back()
        else:
            try:
                browser.browse(user_input)
            except ValueError:
                print("Error: Incorrect URL")


if __name__ == '__main__':
    main()
