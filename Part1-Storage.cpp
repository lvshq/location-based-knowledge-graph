/* 
 * Author:       Shuangquan Lyu
 * Student ID :  780052
 * Purpose :     Extract landmark names from OpenStreetMap data file and match them with Wikipedia titles.
 */

#include "Storage.h"

using namespace std;

Storage* Storage::instance_ = NULL;
/* DIS is used in the OpenStreetMap,
 * It is the index difference of the string between 'v' to the first character of the landmark's name;
 * For example, a tag in the file is <tag k="operator" v="University of Melbourne"/>, so the landmark name(here is "University of Melbourne") is 3 characters after the 'v' character.
 * I use it to locate the landmark name's start index.
 */
const int DIS = 3;  

/*
 * This struct is used as a auxiliary function to compare landmark names and help to establish element in an inverted index table.
 * It is used in a sort function to sort names in ascending order.
 */
struct Greater
{
	bool operator () (const Index& index1, const Index& index2) const {
		return index1.name < index2.name;
	}
};

/*
 * Read landmarks from OpenStreetMap, set inverted index table for them,
 * and matching them with titles from Wikipedia.
 */
Storage::Storage() {
	// "MU.xml" is the data file from OpenStreetMap, here I select the area around MU
	readFromMap("data/MU.xml");

	// "landmarksInvertedIndex.txt" will store the words appearing in all landmarks' names and their corresponding appearing line number(s).
	setIndex("data/landmarksInvertedIndex.txt");

	// "enwiki-20150805-all-titles.xml" is the data file from Wikipedia and stores all the TITLEs of landmarks.
	// "result.txt" is just the matching result produced by this program. In the format: "Landmark name XX --- Wikipedia title YY"
	searchInWiki2("data/enwiki-20150805-all-titles.xml", "data/result.txt");
}

Storage* Storage::getInstance(void) {
	if (instance_ == NULL) instance_ = new Storage;
	return instance_;
}

Storage::~Storage() {
	instance_ = NULL;
}

/*
 * Set an inverted index table for all the words appearing in the landmarks. 
 * With the inverted index table we can apply matching methods between landmark names and wikipedia titles.
 */
void Storage::setIndex(const char *fpath) {
	// Use a dynamic array (vector) to store the index
	int len, n_landmark, len_landmark;
	string word, landmark;
	len = landmarks.size();
	vector<string>::iterator it;
	n_landmark = 1;

	// Iterate all the landmarks
	for (it = landmarks.begin(); it != landmarks.end(); it++, n_landmark++) {
		landmark = *it;
		len_landmark = landmark.size();
		for (int i = 0; i < len_landmark; i++) {
			//  word stores each word in a landmark's name.
			word = "";   

			// The vector "landmark" has been created and stores the landmarks before this method in method "readFromMap".
			// Note that some of the landmarks may contain some substring like "(__)" ('_' means any characters), or comma ',', etc.
			// These special situation need to be considered, so I just put them in the while condition, so that we won't include these characters.
			while (landmark[i] != ' ' && landmark[i] != '(' && landmark[i] != ')'
				&& landmark[i] != ',' && i < len_landmark) {
				word += landmark[i];
				i++;
			}

			// The dictionary stores all the dictionary and is used to avoid duplicate.
			// "makeSense()" is used to exclude some meaningless words like "of", "and", etc.
			// If there hasn't been such a word in the dictionary, we need to create an Index instance and assign the word name and the corresponding appearing line.
			if (dictionary.count(word) == 0 && makeSense(word)) {
				dictionary.insert(word);						   // Then add this word to the dictionary
				Index temp;
				temp.name = word;
				temp.lines.insert(n_landmark);  // Store the line where this word appears
				index.push_back(temp);
			}
			else if (makeSense(word)) {  // There has been such a word in the dictionary and the word is a meaningful word
				vector<Index>::iterator it = index.begin();
				for (; it != index.end(); it++) {
					if ((*it).name == word) {
						(*it).lines.insert(n_landmark);  // Just add the line it appears in the already existing record.
						break;
					}
				}
			}
		}
	}

	// Sort the words in order to make inspection convenient.
	sort(index.begin(), index.end(), Greater());

	//  Output for test
	ofstream outFile;
	outFile.open(fpath);
	set<int>::iterator sit;
	vector<Index>::iterator out_it;
	for (out_it = index.begin(); out_it != index.end(); out_it++) {
		outFile << (*out_it).name << " : ";
		for (sit = (*out_it).lines.begin(); sit != (*out_it).lines.end(); sit++)
			outFile << (*sit) << " ";
		outFile << endl;
	}
	outFile.close();
}

/*
 * Read the data from OpenStreetMap and extract all the landmark names and sort them in the file (indicated by *fpath) in ascending order.
 */
bool Storage::readFromMap(const char *fpath) {
	int len, mul, i, lens, num;
	vector<string> temp_landmarks;
	string str, s;
	ifstream inFile;
	inFile.open(fpath);
	if (!inFile.is_open()) {
		return false;
	}
	if (inFile.peek() == EOF) {
		inFile.close();
		return true;
	}

	while (getline(inFile, str)) {
		s = "";
		// The names of landmark are store in a tag named <tag>. Before it there will be many <node> tag to describe it.
		// So we can jump over those <node> tags in order to save time. <node> tag can be captured by "str[2] == 'n'"
		if (str[2] != 'n' && str.find("k=\"name\"") != string::npos) {
			int i = str.find("v=");
			i += DIS;
			while (str[i] != '"') {
				s += str[i];
				i++;
			}
			//  If the string is not pure-digit (this is a strange phenonmen in OSM, some landmark are purely some digis), then add it to the landmarks
			if (!ifPureDigit(s)) {
				temp_landmarks.push_back(s);
			}
		}
	}

	// Sort the landmark names in ascending order
	sort(temp_landmarks.begin(), temp_landmarks.end());

	// Delete duplicate landmarks and store them in vector landmarks
	num = 0;
	vector<string>::iterator it = temp_landmarks.begin();
	for (; it != temp_landmarks.end() - 1; it++)
		if ((*it) != (*(it + 1))) {
			landmarks.push_back(*it);
			num++;
		}
	cout << "The number of landmarks is : " << num << endl;
	sync();
	inFile.close();
	return true;
}

/*
 * Write the landmarks to file, here the file is "Landmark Names.txt" 
 */
bool Storage::writeToFile(const char *fpath) {
	ofstream outFile;
	outFile.open(fpath);
	if (!outFile.is_open())
		return false;
	vector<string>::iterator it;
	for (it = landmarks.begin(); it != landmarks.end(); it++) {
		outFile << (*it) << endl;
	}
}

bool Storage::sync(void) {
	return writeToFile("data/Landmark Names.txt");
}

/*
* Because wikipedia titles use '_' to replace ' ' in order to add it directly to the url, so we do this conversion here.
*/
string Storage::process(string s) {
	int len = s.size();
	for (int i = 0; i < len; i++)
		if (s[i] == ' ')
			s[i] = '_';
	return s;
}

/*
 * NOTE: This method is not called in this version. It is a trying during the project to test the result.
 * What is used called is "searchInWiki2" instead of "searchInWiki"
 * Search each landmark's name in Wikipedia. Using full-name matching, namely the landmark's name must be a title in the wikipedia.
 */
void Storage::searchInWiki(const char *readFile, const char *writeFile) {
	int len, mul, i, lens, num, used_for_testing;
	string str, s;
	ifstream inFile;
	ofstream outFile;
	inFile.open(readFile);  //  open the .xml file
	outFile.open(writeFile);
	if (!inFile.is_open()) {
		return;
	}
	if (inFile.peek() == EOF) {
		inFile.close();
		return;
	}

	if (!outFile.is_open())
		return;

	num = 0;
	used_for_testing = 0;
	vector<string>::iterator it = landmarks.begin();
	while (true) {
		if (!getline(inFile, str))
			break;
		// parallel searching
		while ((*it) > str) {
			if (!getline(inFile, str))  //  Reach the end
				break;
			used_for_testing++;
			if (used_for_testing % 200000 == 0)
				cout << str << endl;  // Just for test, showing that the program is running
		}
		// have found a matching pair
		if ((*it) == str && str != "") {
			num++;
			outFile << str << endl;
			it++;
		}
		it++;
		if (it >= landmarks.end())
			break;
	}
	inFile.close();
	outFile.close();
}


/*
 * search each landmark's name in Wikipedia. Using each-word matching method.
 * Need to consider and deal with all the special cases to get a best matching result.
 */
void Storage::searchInWiki2(const char *readFile, const char *writeFile) {
	bool test = false;
	int len, i, word_num, used_for_testing, all_word, landmark_word;
	string str, s, word;
	ifstream inFile;
	ofstream outFile;
	inFile.open(readFile);  //  open the .xml file
	outFile.open(writeFile);
	if (!inFile.is_open()) {
		return;
	}
	if (inFile.peek() == EOF) {
		inFile.close();
		return;
	}

	if (!outFile.is_open())
		return;

	used_for_testing = 0;
	set<int> non_duplicate_lines;
	set<string> temp_dic;

	while (getline(inFile, str)) {
		temp_dic.clear();
		
		len = str.size();
		word_num = 0;
		all_word = 0;
		set<int> intersection;
		bool first_time = true;
		set<int> temp_set;  // temp_set is used to get the intersection of all words' lines.
		set<int> set_from_index;

		// Iterator this string, separate each word and deal with it
		for (i = 0; i < len; i++) {
			set_from_index.clear();
			word = "";

			// Because the title in Wikipedia use '_' to replace space, so '_' is used as a separate sign.
			while (str[i] != '_' && i < len) {
				word += str[i];
				i++;
			}
			// all_word is the number of words in the Wikpedia title
			if (makeSense(word))
				all_word++;

			// In set, "count" method use operator<, so it would be faster than use iterator to iterate all the set or the Index vector
			if (dictionary.count(word) != 0) {

				// This block is used to eliminate the duplicate words in a title, otherwise "Porta_a_Porta"(Wiki title) would match "Porta" (Landmark).
				if (temp_dic.count(word) == 0 && makeSense(word)) {
					word_num++;
					temp_dic.insert(word);
				} else {
					continue;
				}

				// Find the corresponding lines of the word in those landmarks.
				for (vector<Index>::iterator temp_it = index.begin(); temp_it != index.end(); temp_it++) {
					if (temp_it->name == word) {
						set_from_index = temp_it->lines;
						if (first_time) {
							first_time = false;
							temp_set = set_from_index;
						}
						// Since there are titles like "Porta_a_Porta", we need to delete that index once the first "Porta" appears.
						// Here just make its name null.
						break;
					}
					else if (temp_it->name > word) {
						// Since the names are arranged in lexicographic ordering, this means the landmark dictionary doesn't have such a word.
						// For example, the dictionary contains ('A','B','D'). When we search 'C' in it.
						//    When we meet "(*it) > C"(here (*it) will be 'D'), we know 'D' isn't in this dictionary.
						break;
					}
				}

				// Find the intersecton of two sets. These two sets both stores the lines which a word appears in the landmarks.
				temp_set = findIntersection(temp_set.begin(), temp_set.end(), set_from_index.begin(), set_from_index.end());
			}
		}

		// More than two words in the dictionary is in the wikipedia's title and the words appear in the same landmarks.
		// NOTE: This can be adjusted. For example, if we have title "A_B_C" and landmark "A_B", then it would be match because there are two valid words.
		if (word_num >= 1 && (3 * word_num - 2 * all_word >= 0) && !temp_set.empty())  
		{
			set<int>::iterator it, final_it;
			it = temp_set.begin();
			string temp_landmark = landmarks[(*it) - 1];

			
			// Find the corresponding landmark with the shortest name
			// NOTE: This can be adjusted. Because actually there might be several landmark names "match" the title. We just choose the shortest in the temporary vector.
			for (; it != temp_set.end(); it++) {
				if (landmarks[(*it) - 1].size() <= temp_landmark.size()) {
					temp_landmark = landmarks[(*it) - 1];
					final_it = it;
				}
			}

			/* This block is used to count the make-sense words in the landmark */
			int landmark_len = temp_landmark.size();
			string temp;
			int sum = 0;
			for (int k = 0; k < landmark_len; k++) {
				temp = "";
				while (k < landmark_len && temp_landmark[k] != ' ') {
					temp += temp_landmark[k];
					k++;
				}
				if (makeSense(temp)) {
					sum++;
				}
					
				
			}

			/* Test */
			/*
			if (str == "University_of_Melbourne") {
				cout << str << " : " << word_num << sum << all_word << endl;
				//getchar();
			}*/

			// The make-sense should occupy at least 1/2 in the landmark's name and there shouldn't be duplicate name appear.
			if (word_num == sum && sum == all_word && non_duplicate_lines.count(*final_it) == 0) {
				non_duplicate_lines.insert(*final_it);
				outFile << "Landmark name : " 
					<< setw(45) << std::left << temp_landmark
						<< "  ---  Wikipedia title : " << str << endl;
			}
		}
		used_for_testing++;
		// The program will run more than an hour so we need some feedback inorder to know it is running.
		// We set it show the string every 200000 titles.
		if (used_for_testing % 200000 == 0)
			cout << str << endl;  

		// Sometimes the while loop will restart from the start of the file (maybe because the end file character in the Wiki's file is special and not captured by "getline()")
		//   So we just break it if it restart.
		if (str[0] == '!' && used_for_testing > 2000000)
			break;
	}

	inFile.close();
	outFile.close();
}

/*
 * Used when matching the landmark names and Wikipedia titles.
 * Each name has a set storing all its words. Here we find their intercsection, namely the common words.
 */
set<int> Storage::findIntersection(set<int>::iterator first1, set<int>::iterator last1, set<int>::iterator first2, set<int>::iterator last2) {
	set<int> result;
	while (first1 != last1 && first2 != last2)
	{
		if (*first1 < *first2)
			++first1;
		else if (*first2 < *first1)
			++first2;
		else {
			result.insert(*first1);
			++first1;
			++first2;
		}
	}
	return result;
}

/*
 * Used to test whether a string consists of pure digits.
 */
bool Storage::ifPureDigit(string s) {
	if ('0' <= s[0] && s[0] <= '9') {
		int len = s.size();
		for (int i = 0; i < len; i++)
			if ('9' < s[i] || s[i] < '0')
				return false;  //  not pure-digit
		return true;
	}
	else {   // if the first digit is not a digit, then must not be pure-digit
		return false;
	}
}

/* 
 * There are some words doesn't make sense such as "of", "and".
 * Therefore these words should be excluded from the dictionary.
 */
bool Storage::makeSense(string word) {
	if (word != "" && word != "-" //&& word.size() != 1 && !ifPureDigit(word)
		&& word != "The" && word != "of" && word != "and" && word != "for" && word != "on")
		return true;
	else
		return false;
}
