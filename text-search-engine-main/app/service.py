from operator import index
from os import listdir
from os.path import isfile, join
import os
from langcodes import closest_match
from app.constants import GC
from flask import jsonify
import json
import spacy
spacy.prefer_gpu()


class AppService:

    # Already Indexed? Should index?
    def isProcessed(self, first=True) -> bool:

        actual_file_list = self.dirFiles(
            os.path.join(os.getcwd(), GC.DATASET))

        index_file_file_list = GC.INDICES.get("files", None)

        if not index_file_file_list and first:
            self.ProcessFiles()
            return self.isProcessed(False)
        elif not index_file_file_list:
            return False

        self.removeIgnoredFiles(actual_file_list)

        sameLists = list(set(actual_file_list) - set(index_file_file_list)) == None

        if not sameLists and first:
            self.ProcessFiles()
            return self.isProcessed(False)
        elif not sameLists and not first:
            return False

        return True

# Preprocessing function
    def ProcessFiles(self):

        idxDict = {}
        # lemmatizer = spacy.load("en_core_web_sm", disable=['parser', 'ner'])

        fileList = self.dirFiles(
            os.path.join(os.getcwd(), GC.DATASET))

        # print(files_list)

        self.removeIgnoredFiles(fileList)

        fileDict = {}
        ctr = 0
        for file in fileList:
            fileDict[file] = ctr
            ctr += 1

        idxDict["files"] = fileList

        idxDict["index"] = {}

        for file in fileList:

            print(file)
            with open(os.path.join(os.path.join(os.getcwd(), GC.DATASET), file), 'r+') as f:
                lineNumber = 0
                for line in f:
                    lineNumber += 1
                    if not line:
                        continue

                    lemmatized_line = GC.LEMMA(line)
                    for words in lemmatized_line:
                        if words.lemma_ not in idxDict["index"]:
                            d = {}
                            d[fileDict[file]] = {}
                            d[fileDict[file]]["occurrence"] = [lineNumber]
                            idxDict["index"][words.lemma_] = d
                        else:
                            d = idxDict["index"][words.lemma_]
                            if fileDict[file] not in d:
                                d[fileDict[file]] = {}
                                d[fileDict[file]]["occurrence"] = [
                                    lineNumber]
                            else:
                                d[fileDict[file]]["occurrence"].append(
                                    lineNumber)
                            idxDict["index"][words.lemma_] = d

        GC.INDICES = idxDict
        self.computeSortedWordList()
        self.dumpIdx()

    # Given a word, Return the words Occurrences

    @staticmethod
    def dumpIdx():
        index_file_path = os.path.join(os.path.join(
            os.getcwd(), GC.DATASET), GC.JSFILE)

        mode = 'w+'
        with open(index_file_path, mode) as idxfile:
            try:
                json.dump(GC.INDICES, idxfile)
            except:
                print("ERROR WRITING")

            idxfile.close()

    def searchWord(self, word, first=True):

        if first and not GC.INDICES and not self.isProcessed():
            self.isProcessed()
            return self.searchWord(word, False)

        if word not in GC.INDICES["index"]:
            # Perform Binary Search and Return the closest
            print("NOT IN THE DICT")
            closest_word = self.similarWordSearch(word)

            print("CLOSEST WORD", closest_word)
            return json.dumps({"files": GC.INDICES["files"], "searchResults": GC.INDICES["index"][closest_word], "type": 1, "word": closest_word})
            return ResponseService().create_response(closest_word, 0)

        if not first and not GC.INDICES and not self.isProcessed():
            return jsonify({"files": {}, "searchResults": {}})
        
        return json.dumps({"files": GC.INDICES["files"], "searchResults": GC.INDICES["index"][word], "type": 0, "word": word})

    def similarWordSearch(self, word, first=True):
        if not GC.WLIST:
            self.computeSortedWordList()
            return self.similarWordSearch(word, False)

        if not first and not GC.WLIST:
            return jsonify({"files": {}, "searchResults": {}})

        low = 0

        high = len(GC.WLIST) - 1

        closest_word = self.binarySearch(low, high, word)

        return closest_word

    @staticmethod
    def binarySearch(low, high, word):
        mid = -1
        while(low < high):
            mid = (low + high)//2
            midpoint = GC.WLIST[mid]
            if midpoint > word:
                high = mid - 1
            elif midpoint < word:
                low = mid + 1
            else:
                break

        return GC.WLIST[mid]

    @staticmethod
    def dirFiles(path):
        return [f for f in listdir(path) if isfile(join(path, f))]

    @staticmethod
    def computeSortedWordList():
        if GC.INDICES:
            index = list(sorted(GC.INDICES["index"].keys()))
            GC.WLIST = index

    @staticmethod
    def removeIgnoredFiles(listOfFiles):
        for file in listOfFiles:
            print(file, file.split(".")[-1])
            if file.split(".")[-1] in GC.DIR_IGNORE:
                listOfFiles.remove(file)

    # Array 1 -> Freshly Computed File List
    # Array 2 -> Existing File List

    @staticmethod
    def areArraysSame(array1, array2):
        return list(set(array1) - set(array2)) == None
