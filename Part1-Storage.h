#ifndef STORAGE_H
#define STORAGE_H

#include <list>
#include <string>
#include <vector>
#include <map>
#include <set>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <algorithm>
#include "LandMark.h"
using namespace std;

typedef struct Index {
	string name;
	set<int> lines;
} Index;

class Storage {
public:
	// singleton
	static Storage *getInstance(void);
	~Storage();
	bool sync(void);

private:
	static Storage *instance_;
	Storage();
	void searchInWiki(const char*, const char*);
	void searchInWiki2(const char*, const char*);
	void setIndex(const char *fpath);
	set<int> findIntersection(set<int>::iterator, set<int>::iterator, set<int>::iterator, set<int>::iterator);
	string process(string s);
	bool readFromMap(const char *fpath);
	bool writeToFile(const char *fpath);
	bool makeSense(string);
	vector<string> landmarks;
	vector<Index> index;
	set<string> dictionary;  //  word_set stores the different words
	
	bool ifPureDigit(string s);
	//bool cmp(Index& it1, Index& it2);

};

#endif

