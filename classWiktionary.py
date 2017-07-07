#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from bs4 import BeautifulSoup
import requests
import simplejson as json

class WikitionaryParser(object):
    def __init__(self):
        self.session=requests.Session()
        self.vector=dict ()
        self.word_found=False

    def __getitem__(self, i):
        if self.word_found:
            if i in self.vector.keys():
                return self.vector[i]
            else:
                return "ERROR/NFL: Word not found for given language"
        else:
            return "ERROR/NFW: Word not found in Wiktionary"

    def appendSingleList(self,singleList,currentKey):
        toAppend=[item.text for item in singleList.findAll("li")]
        if not toAppend in self.vector[currentKey]:
            self.vector[currentKey].append(toAppend)

    def processPage(self,rawText):
        soup=BeautifulSoup(rawText,"html5lib")
        tags=[tag for tag in soup.html.body.findAll("h2") if tag.text!=""]
        ctag=tags[0]
        for tag in tags:
            i=0
            while ctag:
                if ctag.name=="h2":
                    i+=1
                    if i==1:
                        currentKey=ctag.text
                        self.vector[currentKey]=list ()
                if i==2:
                    i=0
                    break
                if i==1:
                    lists=ctag.findAll("ol")
                    for singleList in lists:
                        self.appendSingleList(singleList,currentKey)
                    if ctag.name=="ol":
                        self.appendSingleList(ctag,currentKey)

                ctag=ctag.findNext()
        return tags

    def get(self,title):
        result=self.session.get('https://en.wiktionary.org/w/api.php?titles='+title+'&action=query&prop=extracts&format=json')
        self.status=result.status_code
        if self.status!=200:
            print "ERROR/404: Network connection error"
            return
        pages=json.loads(result.text)["query"]["pages"]
        if "-1" in pages.keys():
            self.word_found=False
            return
        self.rawTexts=[pages[page]["extract"] for page in pages]
        self.pages=[self.processPage(rawText) for rawText in self.rawTexts]
        self.word_found=True
        return "STATUS:OK"

def main():
    definition=WikitionaryParser()
    definition.get("window")
    print json.dumps(definition["English"],indent=4)

if __name__ == '__main__':
    main()
