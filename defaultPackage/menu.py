import bs4
import chardet
import nltk
import os
import re
import timeit
from bs4 import BeautifulSoup
from io import StringIO
from nltk.stem.snowball import SnowballStemmer

path = "C:\\Users\\luky\\PycharmProjects\\Indexer\\corpus"
stopListPath = "C:\\Users\\luky\\PycharmProjects\\Indexer\\stoplist.txt"
list = []
fileNames = []
wordList = {}
wordID = 0
stemmer = SnowballStemmer("english")


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]', 'http:', 'a']:
        return False
    elif isinstance(element, bs4.element.Comment):
        return False
    elif isinstance(element, bs4.element.Doctype):
        return False
    elif re.match(r"[\s\r\n]+", str(element)):
        return False
    elif re.match(
            "^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$",
            str(element)):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    # print(soup.original_encoding)
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    str = u" ".join(t.strip() for t in visible_texts)
    str = re.sub("[()-:!'’—?&@{}[\]|%$◄►#©“”`→\"]", " ", str)
    str = str.strip()
    return str


with open(stopListPath, "r") as file:
    stop = file.read()
    stopList = stop.split()

for root, dirs, files in os.walk(path):
    for file in files:
        fileNames.append(file)
        list.append(os.path.join(root, file))
        # if file.endswith(".txt"):
        #     #print(os.path.join(root, file))
        #     list.append(os.path.join(root, file))

# nltk.download('punkt')

while True:

    print("\nMENU : ")
    print("1) Parse files\n"
          "2) Create inverted index\n")

    selection = input()
    if selection == '1':

        open("doc_index.txt", "w").close()

        start = timeit.default_timer()

        for i in range(0, 99):
            # print( list[i] )

            rawdata = open(list[i], 'rb').read()
            result = chardet.detect(rawdata)
            encoding = result['encoding']
            # print(encoding)

            file = open(list[i], encoding=encoding, errors='ignore')

            # print(file.read())
            result = text_from_html(file.read())

            words = nltk.wordpunct_tokenize(result)

            # lowercase
            # words = [item.lower() for item in words]

            # removing stop words
            words = [stemmer.stem(word.lower()) for word in words if word.lower() not in stopList]

            # stemming
            # words = [stemmer.stem(word) for word in words]

            # check if word exists in dictionary, if not add it.
            for word in words:
                if word not in wordList:
                    wordList[word] = wordID
                    wordID += 1

            # write forward index
            with open("doc_index.txt", "a+") as file:
                prevWords = []
                for word in words:
                    if word not in prevWords:
                        prevWords.append(word)
                        indices = [str(i + 1) for i, x in enumerate(words) if x == word]
                        file.write(str(i) + "\t" + str(wordList[word]) + "\t" + "\t".join(indices) + "\n")

            print(str(i) + ") ")
            # print(words)
            file.close()

        # write doc ids
        with open("docids.txt", "w") as file:
            index = 0
            for name in fileNames:
                file.write(str(index) + "\t" + name + "\n")
                index += 1

        # write term ids
        with open("termids.txt", "w", encoding="utf-8") as file:
            for key, value in wordList.items():
                file.write(str(value) + "\t" + key + "\n")

        stop = timeit.default_timer()
        print('Time: ', stop - start)

    else:
        print("Creating index ...")

        file = open("doc_index.txt", "r")

        start = timeit.default_timer()

        termsList = []
        termCountList = {}
        termInDocsCountList = {}
        prevDocIds = {}

        iteration = 0

        for line in file:
            contents = line.split()
            docID = contents[0]
            termID = contents[1]
            del contents[0:2]

            # from
            # docID  termID  position  position  position
            # to
            # termID  docID:position  docID:position  docID:position

            file_str = StringIO()
            new = True

            prevDocId = 0

            # check if this term has occurred before
            if int(termID) < len(termsList):
                file_str = termsList[int(termID)]

                # get previous docID for curr - prev offset
                if int(termID) in prevDocIds:
                    prevDocId = prevDocIds[int(termID)]

                file_str.write("\t" + str(int(docID) - prevDocId) + ':' + contents[0])
                new = False
                termCountList[int(termID)] += 1  # count word at first position
                termInDocsCountList[int(termID)] += 1  # word found in one more document

            # new term
            else:
                file_str.write(termID + "\t" + docID + ':' + contents[0])
                termCountList[int(termID)] = 1  # count word at first position
                termInDocsCountList[int(termID)] = 1  # word found first time

            # write docID:positions
            for i in range(1, len(contents)):
                file_str.write('\t' + '0' + ':' + str(int(contents[i]) - int(contents[i - 1])))
                termCountList[int(termID)] += 1

            # record last written docId for this term
            prevDocIds[int(termID)] = int(docID)

            if new:
                termsList.append(file_str)

            iteration += 1

        # write statistics in files

        termFileOffset = 0
        outfile = open("term_index.txt", 'w')
        outfile2 = open("term_info.txt", 'w')

        outfile.write(termsList[0].getvalue() + "\n")

        outfile2.write(
            str(0) + "\t" + str(termFileOffset) + "\t" + str(termCountList[0]) + "\t" + str(
                termInDocsCountList[0]) + "\n")

        termFileOffset += len(termsList[0].getvalue()) + 2

        for i in range(1, len(termCountList)):
            outfile.write(termsList[i].getvalue() + "\n")
            outfile2.write(
                str(i) + "\t" + str(termFileOffset) + "\t" + str(termCountList[i]) + "\t" + str(
                    termInDocsCountList[i]) + "\n")

            termFileOffset += len(termsList[i].getvalue()) + 2

        stop = timeit.default_timer()

        print("\nTime : " + str(stop - start))
