# functions module for wfo md sync
import os.path
import requests
import json
import yaml
from pprint import pprint

# we keep a list of taxa we have processed this run
processedTaxa = []


def synchronizeFromList(csvFilePath, dataDir):
    print(f"- Synchronizing from list in: {csvFilePath}")


def synchronizeFromRoot(wfoId, dataDir):
    print(f"- Synchronizing root taxon with id: {wfoId}")
    taxon = getTaxonGraph(wfoId)
    writeFile(taxon, dataDir, True)


def writeFile(taxon, dataDir, includeChildren):

    filePath = dataDir + taxon['hasName']['fullNameStringNoAuthorsPlain']

    # create the taxon file itself
    if os.path.exists(filePath + '.md'):
        updateFile(taxon, filePath)
    else:
        createFile(taxon, filePath)

    # flag that we have done this one
    processedTaxa.append(taxon['hasName']['id'])

    if includeChildren and len(taxon['hasPart']) > 0:

        # make a dir with same name as file
        if not os.path.exists(filePath):
            os.makedirs(filePath)

        # work through the kids
        for child in taxon['hasPart']:
            childTaxon = getTaxonGraph(child['hasName']['id'])
            writeFile(childTaxon, filePath + '/', True)


def updateFile(taxon, filePath):
    print(f"Updating taxon {filePath}")

    # get the data
    file = open(filePath + '.md', 'r')
    sections = splitFileContent(file.read())
    file.close()

    # update the taxon stuff
    sections['wfo'] = getWfoData(taxon)

    # write it back out
    file = open(filePath + '.md', 'w')
    file.write(sections['meta'])
    file.write(sections['wfo'])
    file.write(sections['body'])
    file.close()


def createFile(taxon, filePath):
    print(f"Creating file {filePath}")
    # content of file
    file = open(filePath + '.md', 'w')
    file.write(getWfoData(taxon))
    file.close()


def getWfoData(taxon):
    out = "__Full Name:__ " + taxon['hasName']['fullNameStringHtml']

    # Synonyms
    if len(taxon['hasSynonym']):
        out += "\n\n## Synonyms"

    for synonym in taxon['hasSynonym']:
        out += f"\n- {synonym['fullNameStringPlain']}"

    # Children
    if len(taxon['hasPart']):
        out += "\n\n## Subtaxa"

    for child in taxon['hasPart']:
        out += f"\n- [[{child['hasName']['fullNameStringNoAuthorsPlain']}|{child['hasName']['fullNameStringPlain']} ]]"

    out += "\n\n---\n\n"
    return out


def splitFileContent(content):

    section = 'meta'
    sectionData = {'meta': '', 'wfo': '', 'body': ''}
    lineCount = 0

    # line at a time
    for line in content.splitlines():

        # if the first line is not --- then we skip
        # metadata and go straight to wfo
        if lineCount == 0 and line != '---':
            section = 'wfo'

        # actually add the line
        sectionData[section] += line

        # --- marks end of meta section
        if lineCount > 0 and section == 'meta' and line == '---':
            section = 'wfo'

        # --- marks end of wfo section
        if lineCount > 0 and section == 'wfo' and line == '---':
            section = 'body'

    return sectionData


def getTaxonGraph(wfoId):
    # fetches all the data needed to populate one markdown file
    # or nothing if wfoId is inappropriate
    url = 'https://list.worldfloraonline.org/gql.php'

    query = """
        query getTaxonGraph($wfoId: String!){
            taxonNameById(nameId: $wfoId){
                id
                fullNameStringPlain
                currentPreferredUsage{
                    id
                    path{
                        id
                        hasName{
                            id
                            fullNameStringNoAuthorsPlain
                        }
                    }
                    hasName{
                        id
                        fullNameStringNoAuthorsPlain
                        fullNameStringHtml
                    }
                    hasSynonym{
                        id
                        fullNameStringPlain
                    }
                    hasPart{
                        id
                        hasName{
                            id
                            fullNameStringNoAuthorsPlain
                            fullNameStringPlain
                            fullNameStringHtml
                        }
                    }
                }
            }
        }
        """

    variables = {"wfoId": wfoId}

    payload = {
        'query': query,
        'variables': variables
    }

    response = requests.post(url, json=payload)
    data = json.loads(response.text)
    name = data['data']['taxonNameById']

    # test if this is a synonym or not
    # we only support accepted taxa as files
    if 'currentPreferredUsage' not in name:
        print(
            f"This name {wfoId} : {name['fullNameStringPlain']} has not been placed in the taxonomy. Can not proceed.")
        exit
    else:
        return name['currentPreferredUsage']
