import sys
import requests
from bs4 import BeautifulSoup


class Translator:
    languages = ['all', 'arabic', 'german', 'english', 'spanish', 'french',
                 'hebrew', 'japanese', 'dutch', 'polish', 'portuguese',
                 'romanian', 'russian', 'turkish']
    language_in = ''
    language_out = ''
    word = ''
    n = 5
    save = False
    words_str = ''
    examples_str = ''
    argv = ''

    def initialize(self):
        self.argv = sys.argv

        # Check if the user has already provided the parameters from the
        # command line, otherwise ask for them.
        if len(self.argv) == 1:
            print("Hello, you're welcome to the translator.")
            self.define_parameters()
        else:
            self.get_param_from_command_line()

        self.check_parameters()
        # if the output is set to all languages, get translations and examples
        # and print just one of them to each language and save all in a file.
        if self.language_out == 'all':
            self.n = 1
            self.save = True
            try:
                self.establish_connection2()
            except requests.exceptions.ConnectionError:
                print('Something wrong with your internet connection')
                exit()
        else:  # get translations and examples and print 5 of them
            self.n = 5
            self.save = False
            try:
                self.establish_connection()
            except requests.exceptions.ConnectionError:
                print('Something wrong with your internet connection')
                exit()

    def get_param_from_command_line(self):
        self.language_in = self.argv[1].lower()
        self.language_out = self.argv[2].lower()
        self.word = self.argv[3].lower()

    def define_parameters(self):
        """ Gets the settings (languages and word to translate) from the
            user and stores it in the global variables. """

        print('Translator supports:')
        # print the supported languages from the list
        for i, lang in enumerate(self.languages):
            if i == 0:
                pass
            else:
                print(f'{i}. {lang.capitalize()}')

        # set the source language from the language's list
        self.language_in = self.languages[
            int(input('Type the number of your language:\n'))]

        # set the language to translate to
        self.language_out = self.languages[
            int(input("Type the number of language you want to translate to"
                      " or '0' to all languages:\n"))]

        self.word = input('Type the word you want to translate:\n').lower()

    def check_parameters(self):
        if self.language_in not in self.languages:
            print(f"Sorry, the program doesn't support {self.language_in}")
            exit()
        if self.language_out not in self.languages:
            print(f"Sorry, the program doesn't support {self.language_out}")
            exit()

    def establish_connection2(self):
        page = requests.Session()
        my_file = open(f'{self.word}.txt', 'a', encoding='utf-8')
        r = page.get('https://context.reverso.net/translation/',
                     headers={'User-Agent': 'Mozilla/5.0'})

        for i in range(1, len(self.languages)):
            self.language_out = self.languages[i]

            # do not attempt to translate to the same language of the source
            if self.language_out == self.language_in:
                pass
            else:  # translate to the rest of the languages
                r = page.get('https://context.reverso.net/translation/' +
                             self.language_in + '-' + self.language_out +
                             '/' + self.word,
                             headers={'User-Agent': 'Mozilla/5.0'})

                # If the word is not found, end the program
                if str(r) != '<Response [200]>':
                    print(f'Sorry, unable to find {self.word}')
                    exit()

                self.get_translation(r.content)
                my_file.write(self.words_str + self.examples_str)

        my_file.close()
        page.close()

    def establish_connection(self):
        """ Establishes the connection and if succeed, calls the
            get_translations function"""

        # concatenate variables to form the url and get the web page info
        page = requests.get('https://context.reverso.net/translation/' +
                            self.language_in + '-' + self.language_out +
                            '/' + self.word
                            , headers={'User-Agent': 'Mozilla/5.0'})

        if page.status_code == 200:
            self.get_translation(page.content)
        else:
            print(f'Sorry, unable to find {self.word}')

    def get_translation(self, web_page):
        # parse the website content
        soup = BeautifulSoup(web_page, 'html.parser')

        # get the translations and make a list
        translations = soup.find('div', {'id': 'translations-content'})

        # todo: 'bye' == 'au revoir', but the translator only prints 'au'.
        words = translations.text.strip('\n').split()

        # get the available examples and make a list
        open_examples = soup.find_all('div', {'class': 'example'})
        examples_list = []
        for ex in open_examples:
            text_list = ex.text.replace('\n', ''). \
                replace('          ', '+').split('+')
            if len(text_list) == 3:
                examples_list.append(
                    text_list[1])  # example in source language
                examples_list.append(
                    text_list[2])  # example in translated language

        self.print_translations(words, examples_list)

    def print_translations(self, items, phrases):

        # store n possible translation words
        self.words_str = self.language_out.capitalize() + ' Translations:\n'
        for i in range(self.n):
            self.words_str += items[i] + '\n'

        # store n examples of use
        self.examples_str = '\n' + self.language_out.capitalize() + ' Examples:\n'
        for j in range(0, self.n * 2, 2):
            self.examples_str += phrases[j] + ':\n' + phrases[j + 1] + '\n\n'

        print()
        print(self.words_str + self.examples_str)


if __name__ == '__main__':
    translator = Translator()
    translator.initialize()
