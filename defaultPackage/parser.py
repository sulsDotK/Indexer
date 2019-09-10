import os
import re
import sys
import timeit
from io import StringIO

import bs4
import nltk
from bs4 import BeautifulSoup
from nltk.stem.snowball import SnowballStemmer

path = "C:\\Users\\luky\\PycharmProjects\\Indexer\\corpus"
stopListPath = "C:\\Users\\luky\\PycharmProjects\\Indexer\\stoplist.txt"
list = []
fileNames = []
wordList = {}
wordID = 0
stemmer = SnowballStemmer("english")
sumTimes = {}
forwardIndexes = []


def add_timing(key, value):
    global sumTimes
    if key not in sumTimes:
        sumTimes[key] = value
    else:
        sumTimes[key] += value


def filter_tags(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]', 'http:', 'a']:
        return False
    elif isinstance(element, bs4.element.Comment):
        return False
    elif isinstance(element, bs4.element.Doctype):
        return False
    elif re.match(r"[\s\r\n]+", str(element)):
        return False
    elif re.match(
            "^(http://www\.|https://www\.|http://|https://)?[a-z0-9]+([\-.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(/.*)?$",
            str(element)):
        return False
    return True


def apply_regex(body):
    soup = BeautifulSoup(body, 'html.parser')
    # print(soup.original_encoding)
    texts = soup.findAll(text=True)
    visible_texts = filter(filter_tags, texts)
    str = u" ".join(t.strip() for t in visible_texts)
    # print(str)
    regex = re.compile('[^a-zA-Z\d ]')
    return regex.sub(' ', str)
    # str = re.sub("[()-:!'’—?&@{}𔄜[\]|%$◄►#©“”=♦…_·€¢•<>`→\"]", " ", str)
    # str = str.strip()
    # return str


def main():
    global wordID

    # read stoplist
    with open(stopListPath, "r") as file:
        stop = file.read()
        stopList = stop.split()

    # read all file paths
    for root, dirs, files in os.walk(path):
        for file in files:
            fileNames.append(file)
            list.append(os.path.join(root, file))
            # if file.endswith(".txt"):
            #     #print(os.path.join(root, file))
            #     list.append(os.path.join(root, file))

    # nltk.download('punkt')
    # open("doc_index.txt", "w").close()

    # initialize variables
    startTime = timeit.default_timer()
    file_str = StringIO()
    startIndex = 0
    endIndex = len(list)
    sumSpeeds = 0

    # for all files
    for i in range(startIndex, endIndex):

        # rawdata = open(list[i], 'rb').read()
        # result = chardet.detect(rawdata)
        # encoding = result['encoding']
        # print(encoding)

        loopStartTime = timeit.default_timer()

        file = open(list[i], errors='ignore')

        time = timeit.default_timer()

        # parsing
        result = apply_regex(file.read())
        add_timing('parsing', timeit.default_timer() - time)

        time = timeit.default_timer()

        # tokenizing
        wordsDup = nltk.wordpunct_tokenize(result)
        add_timing('tokenizing', timeit.default_timer() - time)

        time = timeit.default_timer()

        # remove stop words, lowercase, and keep distinct
        words = []
        for word in wordsDup:
            w = word.lower()
            if w not in stopList:
                newWord = stemmer.stem(w)
                words.append(newWord)
                if newWord not in wordList:
                    wordList[newWord] = wordID
                    wordID += 1

        # words = [stemmer.stem(word.lower()) for word in words if word.lower() not in stopList]
        add_timing('stem&lower', timeit.default_timer() - time)

        # stemming
        # words = [stemmer.stem(word) for word in words]

        # check if word exists in dictionary, if not add it.
        # time = timeit.default_timer()
        #
        # for word in words:
        #     if word not in wordList:
        #         wordList[word] = wordID
        #         wordID += 1
        # checkexists('addwordtolist', timeit.default_timer() - time)
        #
        time = timeit.default_timer()

        # write forward index
        # with open("doc_index.txt", "a+", encoding="utf8") as file:
        #     prevWords = []
        #     for word in words:
        #         if word not in prevWords:
        #             prevWords.append(word)
        #             indices = [str(i + 1) for i, x in enumerate(words) if x == word]
        #             file.write(str(i) + "\t" + str(wordList[word]) + "\t" + "\t".join(indices) + "\n")

        # write forward index in ram
        prevWords = {}
        for word in words:
            if word not in prevWords:
                prevWords[word] = 0
                indices = [str(i + 1) for i, x in enumerate(words) if x == word]
                file_str.write(str(i) + "\t" + str(wordList[word]) + "\t" + "\t".join(indices) + "\n")
                # forwardIndexes.append(str(i) + "\t" + str(wordList[word]) + "\t" + "\t".join(indices) + '\n')

        add_timing('writingtoStringIO', timeit.default_timer() - time)

        # calculate speed
        currSpeed = timeit.default_timer() - loopStartTime
        sumSpeeds += currSpeed
        if i % 10 == 0:
            print('\rElapsed Time : ' + str(round(timeit.default_timer() - startTime, 1)), end='')
            print(' Progress : ' + str(i) + '/' + str(endIndex - 1), end='')
            print(' Remaining Time : ' + str(round((endIndex - 1 - i) * (sumSpeeds / (i + 1)), 0)), end='')
            sys.stdout.flush()

        file.close()

    time = timeit.default_timer()

    # write forward index
    with open("doc_index.txt", "w", encoding="utf8") as file:
        file.write(file_str.getvalue())
        # file.write(''.join(forwardIndexes))

    # write doc ids
    with open("docids.txt", "w", encoding="utf8") as file:
        index = 0
        for name in fileNames:
            file.write(str(index) + "\t" + name + "\n")
            index += 1

    exceptions = 0
    # write term ids
    with open("termids.txt", "w", encoding='utf8') as file:
        for key, value in wordList.items():
            try:
                file.write(str(value) + "\t" + key + "\n")
            except UnicodeEncodeError:
                exceptions += 1
                continue
                # print('Error printing key : ' + key.encode('utf-16', 'surrogatepass').decode('utf-16') + ' value : ' + str(value))

    add_timing('writingtofiles', timeit.default_timer() - time)

    stop = timeit.default_timer()
    print('\n\nExceptions : ' + str(exceptions))
    print('Time: ' + str(round(stop - startTime, 4)))

    for key in sumTimes:
        print(key + ' : ' + str(round(sumTimes[key], 3)))


if __name__ == "__main__":
    main()
