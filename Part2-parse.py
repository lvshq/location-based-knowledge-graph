# Author:       Shuangquan Lyu
# Student ID:   780052
# Date:         26th Oct 2015
# Purpose:      Extract wikipedia information for landmarks.
#               This is done through:
#                   (1)Extract coordinates from OpenStreetMap file.
#                   (2)Extract information box from Wikipedia.
#                   (3)Use coordinates matching to match landmarks on the basis of previous matching results (recorded in 'resultV5.txt').


import urllib2
import pdb
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint

url = 'https://en.wikipedia.org/wiki/'
# 'result (Final V1.0).txt' records the landmarks from OpenStreetMap with the information extracted from Wikipedia.
outFile = open('result (Final V1.1).txt', 'w')
# 'MU.xml' is OpenStreetMap's landmarks data. Including landmarks' names, coordinates and etc.
inFile = open('MU.xml', 'r')

# Used for parsering the first paragraph of those titles without infoBox
class MyHTMLParser(HTMLParser):
    content = ""
    def handle_data(self, data):
        #print "Data     :", data
        MyHTMLParser.content += data

# Compare the coordinates(including latitude and longitude) from OpenStreetMap and Wikipedia
def cmpCoor(CoorOSM, CoorWiki):
    print CoorOSM
    print CoorWiki
    if (CoorOSM == "" or CoorWiki == ""):
        return False
    OSM_Lat = ""
    OSM_Long = ""
    Wiki_Lat = ""
    Wiki_Long = ""
    # First find the '.' as the seperate symbol. Extract latitude's digits before '.' and longitude's digits before '.'
    i_OSM_Lat = CoorOSM.find('.')
    i_OSM_Long = CoorOSM.find('.', i_OSM_Lat+5)
    i_Wiki_Lat = CoorWiki.find('.')
    i_Wiki_Long = CoorWiki.find('.', i_Wiki_Lat+5)
    while (i_OSM_Lat >= 0):
        OSM_Lat += CoorOSM[i_OSM_Lat]
        Wiki_Lat += CoorWiki[i_Wiki_Lat]
        i_OSM_Lat -= 1
        i_Wiki_Lat -= 1
    if (OSM_Lat != Wiki_Lat):
        return False

    while (CoorOSM[i_OSM_Long] != ' '):
        OSM_Long += CoorOSM[i_OSM_Long]
        Wiki_Long += CoorWiki[i_Wiki_Long]
        i_OSM_Long -= 1
        i_Wiki_Long -= 1
    if (OSM_Long != Wiki_Long):
        return False
    # If both latitude and longitude's digits before '.' are same, then it should be the same place.
    return True

################################################################################
# Used in the file from OpenStreetMap.
# Only extract those coordinates from tag <node> and <way>.
# So if we encountered with <member>(a child node of <relation>), we should jump over it (namely return False)
def checkTag(s):
    if (s == '<mem'):
        return False
    else:
        return True

################################################################################
# Used when compare coordinates. Convert latitude to a uniform format.
def convertLat(s):
    if (s == ""):
        return ""
    _s = ""
    # If the coord is a negative one, then it should be 
    if (s[0] == '-'):
        flag = 'S'
    else:
        flag = 'N'
    # Set the start index
    if (s[0] == '-'):
        i = 1
    else:
        i = 0
    while (i < len(s)):
        _s += s[i]
        i += 1
    return _s + ' ' + flag

################################################################################
# Used when compare coordinates. Convert longitude to a uniform format.
def convertLong(s):
    if (s == ""):
        return ""
    _s = ""
    # If the coord is a negative one, then it should be 
    if (s[0] == '-'):
        flag = 'W'
    else:
        flag = 'E'
    # Set the start index
    if (s[0] == '-'):
        i = 1
    else:
        i = 0
    while (i < len(s)):
        _s += s[i]
        i += 1
    return _s + ' ' + flag

global mapInfo
mapInfo = inFile.read()

################################################################################
# Search through the content of OpenStreetMap file to find out those landmarks' coordinates.
def findCoord(landMarkName):
    # This is the identifier of a landmark in the .xml file from OpenStreetMap
    temp = 'k="name" v="'
    temp_search = temp + landMarkName
    i = mapInfo.find(temp_search)
    # If the identifier string can be found, we can continue to search the landmark's coordinates
    # Variable i used to iterate the whole file
    if (i != -1):
        cooInfo = ""
        # We only collect the coordinates of tag <node> and <way>, so if the tag is <relation>(with <member> inside), we just drop it.
        # Add four characters together to check whether it is latitude or longitude when search in <node>.
        tem = mapInfo[i]+mapInfo[i+1]+mapInfo[i+2]+mapInfo[i+3]
        global lati
        global longi
        lati = ""
        longi = ""
        # Every check whether we are searching the <relation> tag. If so, we should stop immediately because we don't want to use it.
        while (checkTag(tem)):
            # @Test
            #pdb.set_trace()

            if (tem == 'lon='):
                # Variable j used to iterate the <node> tage's content
                # Plus 5 to jump over substring "lon="
                j = i+5
                while (mapInfo[j] != '"'):
                    longi += mapInfo[j]
                    j += 1
            elif (tem == 'lat='):
                j = i+5
                while (mapInfo[j] != '"'):
                    lati += mapInfo[j]
                    j += 1
            # If met '<node', it means the search in the <node> tag should stop
            elif (tem == '<nod'):
                break

            # If met '<nd ', it means we are searching in the <way> tag.
            # So we should extract the node reference number and use it to extract the node's actual coordinates.
            # Here I temporaly use the first node in the <way> tag. (The <way> tag can have 2 to 2000 <nd> tags)
            elif (tem == '<nd ' and lati == ""):
                # Plus 8 to jump over '<nd ref="'
                j = mapInfo.find('"', i) + 1
                nodeRef = ""
                while (mapInfo[j] != '"'):
                    nodeRef += mapInfo[j]
                    j += 1
                # @Test
                print nodeRef
                # Then find "<node id="+nodeRef
                wayNodeIndex = mapInfo.find('<node id="'+nodeRef)
                # As long as there is coresponding <node> tag in this xml file, we should extract the coordinate infomation of the way node.
                if (wayNodeIndex != -1):
                    JumpNoUseInfor = 100
                    wayNodeIndex += JumpNoUseInfor
                    j = mapInfo.find("lat=", wayNodeIndex)
                    # Plus 5 to jump over substring "lat="
                    j += 5
                    if (lati == ""):
                        while (mapInfo[j] != '"'):
                            lati += mapInfo[j]
                            j += 1
                    _j = j
                    j = mapInfo.find("lon=", _j)
                    # Plus 5 to jump over substring "lon="
                    j += 5
                    if (longi == ""):
                        while (mapInfo[j] != '"'):
                            longi += mapInfo[j]
                            j += 1
                    break
            # If met '<way', it means the search in the <way> tag should stop
            elif (tem == '<way'):
                break

            # i minus 1 to iterate backwards, since the information of the landmark is before the identifier <tag k="name" v="...">
            # This controls the outer iteration.
            i -= 1
            tem = mapInfo[i]+mapInfo[i+1]+mapInfo[i+2]+mapInfo[i+3]

        if (lati == ""):
            return ""
        else:
            return convertLat(lati) + "    " + convertLong(longi)
    # If there are no more landmarks in the tag <node>, just return ""
    return ""

####################################################################################################
# Extract the content from information box of each landmark's matching wikipedia page.
def extractInfoBox(HTML, infoIndex):
    endSymbol = "</table>"
    extraTableTag = "<table"
    global infoEndIndex
    # The first </table> tag's index is the end of this information box.
    infoEndIndex = HTML.find(endSymbol, infoIndex)
    # If there exist some extra tables, then we should jump their corresponding '</table>' over.
    extraTableIndex = HTML.find(extraTableTag, infoIndex, infoEndIndex)
    global tempBeginIndex
    tempBeginIndex = infoIndex
    while (extraTableIndex != -1):
        # Jump over '<table>'
        tempBeginIndex = extraTableIndex+5
        infoEndIndex = HTML.find(endSymbol, infoEndIndex+1)
        extraTableIndex = HTML.find(extraTableTag, tempBeginIndex, infoEndIndex)
    
    # Find the first row of the information to be print
    rowSymbol = '<th scope="row"'
    i = HTML.find(rowSymbol, infoIndex, infoEndIndex)
    infoBoxMessage = ""

    # Iterate all valid infomation between the tag <table> and </table>
    # The valid infomation is between an end tag and a start tag, namely between '>' and next '<'
    i += len(rowSymbol)
    # Each row consists of a pair (key, value), such as "Location" - "Brisbane"
    # Initially we should first find the key of each pair.
    while (i < infoEndIndex and i != -1):
        specialSym = '&#160;'
        thEndIndex = HTML.find("</th>", i, infoEndIndex)
        tdEndIndex = HTML.find("</td>", i, infoEndIndex)

        # brack is used to eliminate some referrings occured in the information box. Such as "Founded :  1927 [1]", the last '[1]' should be eliminated
        global bracket
        bracket = 0
        # Extract the head of each row of the information box
        while (i < thEndIndex):
            content = ""
            # Iterator meets an end of a tag, then collects the content between the tag and next tag
            if (HTML[i] == '>'):
                i += 1
                content = ""
                while (HTML[i] != '<' and HTML[i] != '\n'):
                    tempStr = HTML[i]+HTML[i+1]+HTML[i+2]+HTML[i+3]+HTML[i+4]+HTML[i+5]
                    if (tempStr != specialSym):
                        if (HTML[i] == '['):
                            bracket = 1
                        elif (HTML[i] == ']'):
                            bracket = 0
                        # Only there the content is not between '[' and ']' can be printed
                        if (bracket == 0 and HTML[i] != ']'):
                            content += HTML[i]
                            i += 1
                        else:
                            i += 1
                    else:
                        content += ' '
                        i += 6
            else:
                i += 1
            if (content != ""):
                infoBoxMessage += "---   " + content + " : "

        bracket = 0
        # Extract the body of each row of the information box
        while (i < tdEndIndex):
            content = ""
            if (HTML[i] == '>'):
                i += 1
                content = ""
                while (HTML[i] != '<' and HTML[i] != '\n'):
                    tempStr = HTML[i]+HTML[i+1]+HTML[i+2]+HTML[i+3]+HTML[i+4]+HTML[i+5]
                    if (tempStr != specialSym):
                        if (HTML[i] == '['):
                            bracket = 1
                        elif (HTML[i] == ']'):
                            bracket = 0
                        # Only there the content is not between '[' and ']' can be printed
                        if (bracket == 0 and HTML[i] != ']'):
                            content += HTML[i]
                            i += 1
                        else:
                            i += 1
                    else:
                        content += ' '
                        i += 6
            else:
                i += 1
            if (content != ""):
                infoBoxMessage += " " + content
        temp = HTML.find(rowSymbol, i, infoEndIndex)
        i = temp
        infoBoxMessage += "\n"

    return infoBoxMessage

####################################################################################################
# This is the MAIN program
# resultV5.txt stores the matching result generated from previous program, in the format of "landmark name - wikipedia name".
with open('resultV5.txt', 'r') as f:
    fi = f.readlines()
    multiMeaningCount = 0
    foundedSubTitle = 0
    landmarkCount = 0
    # For every record in the landmark (each with a Wikipedia matching), search its corresponding information
    for line in fi:
        wikiSymbol = 'Wikipedia title : '
        landMarkSymbol = 'Landmark name : '
        infoSymbol = 'infobox vcard'
        index = line.find(wikiSymbol)
        openStreetIndex = line.find(landMarkSymbol)
        titleInUrl = ""
        title = ""
        # Jump over the length of 'Wikipedia title : '
        index += len(wikiSymbol)
        while line[index] != '\n':
            titleInUrl += line[index]
            # The name of Wikipedia uses '_' instead of ' ', so we need to convert it when extract landmark name.
            if (line[index] == '_'):
                title += ' '
            else:
                title += line[index]
            index += 1

        # @Test
        print title

        # @Test
        #if (title != "Carlton"):
        #    continue

        landmarkCount += 1

        ###################################################################################################
        # Find the landmark name in OpenStreetMap's file, in order to find its coordinate.
        coordContent = ""
        openStreetIndex += len(landMarkSymbol)
        # If there are continous spaces, then it means that we have collected the whole name of the landmark
        # For example, a record is "Landmark name : 7-11       ---  Wikipedia title : 7-11"
        # If we encountered two contineous spaces, it means that the first part has been collected.
        while (not (line[openStreetIndex] == ' ' and line[openStreetIndex+1] == ' ')):
            coordContent += line[openStreetIndex]
            openStreetIndex += 1
        
        ####################################################################################################
        # get each title's url
        response = urllib2.urlopen(url + titleInUrl)
        html = response.read()
        coordFromOSM = ""
        coordFromOSM = findCoord(coordContent)
        if (coordFromOSM != ""):
            coordInfo = '{:30s} {:4s} {:30s}'.format("Landmark : [" + title +"] ", ':', coordFromOSM+'\n\n')
        else:
            coordInfo = '{:30s}'.format("Landmark : [" + title +"] " + '\n\n')
        # @Test
        print coordInfo

        outFile.write(coordInfo)

        ##################################################################################
        # For those titles with multiple referrings
        multiReferSymbol = 'may refer to:'
        referringIndex = html.find(multiReferSymbol)
        # there are multiple referring titles
        if (referringIndex != -1 and coordFromOSM != ""):
            #outFile.write("This landmark has multiple relative links (showing at most ten below):\n")
            count = 0
            multiMeaningCount += 1
            coord = '<a href="/wiki'
            subIndex = html.find(coord, referringIndex)
            # As long as there are subtitles, print it
            while subIndex != -1:
                containsColon = False
                subTitle = ""
                # minus 4 to show the substring "wiki"
                subIndex += len(coord)-4
                referringIndex = subIndex
                while html[referringIndex] != '"':
                    # If the record contains ':', then it is not a valid title that we want
                    if (html[referringIndex] == ':'):
                        containsColon = True
                        break
                    subTitle += html[referringIndex]
                    referringIndex += 1
                subUrl = "https://en.wikipedia.org/" + subTitle
                coordInfo = '{:34s} {:30s}'.format('---', subUrl + '\n')
                # If the link doesn't contain a colon or a "Main_Page" substring, then it should be something valid
                if (containsColon == False and subUrl.find('Main_Page') == -1):
                    ############################################################
                    # Search those referrings and extract the coordinates, then compare with its original coordinates.
                    # symbols for extracting coordinates and information
                    geoSymbol = 'span class="geo-dec" title="Maps, aerial photos, and other data for this location">'
                    jumpGeo = len(geoSymbol)
                    subResponse = urllib2.urlopen(subUrl)
                    subHtml = subResponse.read()

                    rIndex = subHtml.find(geoSymbol)
                    if (rIndex != -1):
                        rIndex += jumpGeo
                        tempCoor = ""
                        while (subHtml[rIndex] != '<'):
                            tempCoor += subHtml[rIndex]
                            rIndex += 1
                        if (cmpCoor(coordFromOSM, tempCoor) == True):
                            _infoI = subHtml.find(infoSymbol)
                            # As long as we have find a suitable referring with infobox, then print it and ignore other sub-referrings
                            if (_infoI != -1):
                                s0 = extractInfoBox(subHtml, _infoI)
                                foundedSubTitle += 1
                                # We don't need the coordinates in the infoBox, in order not to confuse users.
                                # (The coordinate from infoBox and OpenStreetMap may be different)
                                if (s0.find("Coordinates :") == -1):
                                    outFile.write(s0 +'\n\n')
                                break

                    ############################################################
                # Find next sub-referring link
                subIndex = html.find(coord, referringIndex)
            outFile.write('\n')

        ##################################################################################
        
        # find each title's Information Box content
        infoI = html.find(infoSymbol)
        # There exists an information box in this page
        if (infoI != -1):
            s1 = extractInfoBox(html, infoI)
            # We don't need the coordinate in the infoBox, in order not to confuse users.
            # (The coordinate from infoBox and OpenStreetMap may be different)
            if (s1.find("Coordinates :") == -1):
                outFile.write(s1 +'\n\n')
        else:
            paragraph = '<div id="mw-content-text" lang="en" dir="ltr" class="mw-content-ltr">'
            infoI = subHtml.find(paragraph)
            _infoI = subHtml.find("<p>",infoI)
            __infoI = subHtml.find("</p>",_infoI+1)
            _temp = ""
            while (_infoI <= __infoI):
                _temp += subHtml[_infoI]
                _infoI += 1
                parser = MyHTMLParser()
                parser.feed(_temp)

outFile.write("\n[Summary]\n")        
outFile.write("    There are " + str(landmarkCount) + " landmarks in total.\n")
outFile.write("    There are " + str(multiMeaningCount) + " landmarks' correspoding Wikipedia title has multiple referencing meanings.\n")
outFile.write("        Among the referencings we have founded " + str(foundedSubTitle) + " titles having the same location with the original landmark.\n")
outFile.close()

