from app.constants import GC
import os
import json

from app.service import AppService


class InitializeApp:

    def __init__(self):

        GC.INDICES = self.loadIndex()

    def loadIndex(self):

        index_file_path = os.path.join(os.path.join(
            os.getcwd(), GC.DATASET), GC.JSFILE)

        print(index_file_path)

        mode = 'r+' if os.path.exists(index_file_path) else 'w+'

        index_file = {}
        with open(index_file_path, mode) as idxfile:
            try:
                index_file = json.load(idxfile)
            except:
                print("Index File is Blank or of wrong format, Trying to index it")
                if AppService().isProcessed():
                    print("Indexed Successfully")
                else:
                    print("Cant Index")
            # print(index_file, type(index_file))
            return index_file
