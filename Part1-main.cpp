/*
* Author:       Shuangquan Lyu
* Student ID :  780052
* Purpose :     Extract landmark names from OpenStreetMap and match them with Wikipedia titles.
*/

#include "Storage.h"
#include "LandMark.h"
using namespace std;
int main() {
	// Use Singleton Pattern
	Storage *ins = Storage::getInstance();
	delete ins;
	getchar();
	return 0;
}
