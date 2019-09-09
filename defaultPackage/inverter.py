import timeit
from io import StringIO

print("Creating index ...")

file = open("doc_index.txt", "r", encoding="utf8")

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
outfile = open("term_index.txt", 'w', encoding="utf8")
outfile2 = open("term_info.txt", 'w', encoding="utf8")

outfile.write(termsList[0].getvalue() + "\n")

outfile2.write(
    str(0) + "\t" + str(termFileOffset) + "\t" + str(termCountList[0]) + "\t" + str(termInDocsCountList[0]) + "\n")

termFileOffset += len(termsList[0].getvalue()) + 2

for i in range(1, len(termCountList)):
    outfile.write(termsList[i].getvalue() + "\n")
    outfile2.write(
        str(i) + "\t" + str(termFileOffset) + "\t" + str(termCountList[i]) + "\t" + str(termInDocsCountList[i]) + "\n")

    termFileOffset += len(termsList[i].getvalue()) + 2

stop = timeit.default_timer()

print("\nTime : " + str(stop - start))
