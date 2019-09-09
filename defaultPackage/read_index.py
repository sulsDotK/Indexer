import sys

# doc_name = sys.argv[1]
# print(len(sys.argv))
# print(sys.argv)
# idsToNames = {}
import timeit
from nltk import SnowballStemmer

start = timeit.default_timer()
stemmer = SnowballStemmer("english")

# either docName or termName
if len(sys.argv) == 3:
    paramType = sys.argv[1]

    if paramType == '--doc':
        docName = sys.argv[2]

        with open("docids.txt", 'r', encoding="utf8") as file:
            docId = -1
            for line in file:
                x = line.split(sep='\t')
                x = [c.strip() for c in x]
                if x[1] == docName:
                    docId = x[0]
                    break

        with open('doc_index.txt', 'r', encoding="utf8") as file:
            totalTerms = 0
            uniqueTerms = 0
            found = False
            for line in file:
                entries = line.split()
                if entries[0] == docId:
                    totalTerms += len(entries) - 1
                    uniqueTerms += 1
                    found = True
                elif found == True:
                    break

        print("Listing for document : " + docName)
        print('DOCID : ' + str(docId))
        print('Distinct Terms : ' + str(uniqueTerms))
        print('Total Terms : ' + str(totalTerms))

    elif paramType == '--term':

        termName = stemmer.stem(sys.argv[2])
        termID = -1

        with open("termids.txt", "r", encoding="utf8") as file:
            for line in file:
                line = line.strip().split("\t")
                if len(line) > 0:
                    if line[1] == termName:
                        termID = line[0]

        if termID == -1:
            print("Term not found!")
        else:
            with open("term_info.txt", "r", encoding="utf8") as file:
                for line in file:
                    line = line.strip().split()
                    if len(line) > 0 and line[0] == termID:
                        print("Listing for term: " + sys.argv[2])
                        print("TERMID: " + line[0])
                        print("Number of documents containing term: " + line[3])
                        print("Term frequency in corpus: " + line[2])
                        print("Inverted list offset: " + line[1])
                        break

# both docName and termName
elif len(sys.argv) == 5:

    docName = sys.argv[4]
    termName = stemmer.stem(sys.argv[2])
    termID = -1
    docId = -1

    with open("docids.txt", 'r', encoding="utf8") as file:
        for line in file:
            x = line.split(sep='\t')
            x = [c.strip() for c in x]
            if x[1] == docName:
                docId = x[0]
                break

    with open("termids.txt", "r", encoding="utf8") as file:
        for line in file:
            line = line.strip().split("\t")
            if len(line) > 0:
                if line[1] == termName:
                    termID = line[0]
                    break

    print('Inverted list for term : ' + termName)
    print('In document : ' + docName)
    print('TERMID : ' + str(termID))
    print('DOCID : ' + str(docId))

    with open("doc_index.txt", 'r', encoding="utf8") as file:
        for line in file:
            entries = line.split()
            if entries[0] == docId and entries[1] == termID:
                print('Positions : ', end='')
                for i in range(2, len(entries)):
                    if i > 2:
                        print(', ', end='')
                    print(entries[i], end='')
            break

end = timeit.default_timer()
print("\nTime : " + str(end - start))
