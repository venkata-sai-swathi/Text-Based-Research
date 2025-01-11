import spacy


class GC:
    DATASET = "app/dataset"
    JSFILE = "index.json"
    DIR_IGNORE = ["json", "py", "DS_Store"]
    INDICES = {}
    LEMMA = spacy.load("en_core_web_sm", disable=['parser', 'ner'])
    WLIST = []
