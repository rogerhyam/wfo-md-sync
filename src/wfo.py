# functions module for wfo md sync
import os.path
import requests
import json
from pprint import pprint

# we keep a list of taxa we have processed this run
processedTaxa = []


def synchronizeFromList(csvFilePath, dataDir):
    print(f"- Synchronizing from list in: {csvFilePath}")


def synchronizeFromRoot(wfoId, dataDir):
    print(f"- Synchronizing root taxon with id: {wfoId}")
    taxon = getTaxonGraph(wfoId)
    # knock the name of the end of the path to get the root
    pathParts = os.path.split(taxon['pathString'])
    writeFile(taxon, dataDir, pathParts[0], True)


def writeFile(taxon, dataDir, rootPath='', includeChildren=False):

    # removing the path from the wfo root (Code) to the root taxon
    if len(taxon['pathString']) > len(rootPath):
        filePath = dataDir + taxon['pathString'][len(rootPath):]
    else:
        filePath = dataDir

    # check directory exist
    fileDirParts = os.path.split(filePath)
    if not os.path.exists(fileDirParts[0]):
        os.makedirs(fileDirParts[0])

    # filePath actually ends with the full taxon name now.
    filePath = fileDirParts[0] + '/' + \
        taxon['hasName']['fullNameStringNoAuthorsPlain']

    # create the taxon file itself
    if os.path.exists(filePath + '.md'):
        updateFile(taxon, filePath, rootPath)
    else:
        createFile(taxon, filePath, rootPath)

    # flag that we have done this one
    processedTaxa.append(taxon['hasName']['id'])

    if includeChildren and len(taxon['hasPart']) > 0:

        # work through the kids
        for child in taxon['hasPart']:
            childTaxon = getTaxonGraph(child['hasName']['id'])
            writeFile(childTaxon, dataDir, rootPath, True)


def updateFile(taxon, filePath, rootPath):
    print(f"Updating taxon {filePath}")

    # get the data
    file = open(filePath + '.md', 'r')
    sections = splitFileContent(file.read())
    file.close()

    # update the taxon stuff
    sections['wfo'] = getWfoData(taxon, rootPath)

    # write it back out
    file = open(filePath + '.md', 'w')
    file.write(sections['meta'])
    file.write(sections['wfo'])
    file.write(sections['body'])
    file.close()


def createFile(taxon, filePath, rootPath):
    print(f"Creating file {filePath}")
    # content of file
    file = open(filePath + '.md', 'w')
    file.write(getWfoData(taxon, rootPath))
    file.close()


def getWfoData(taxon, rootPath):

    if taxon['hasName']['authorsString']:
        out = f"{taxon['hasName']['authorsString']} | "
    else:
        out = ''

    out += f"{taxon['hasName']['rank']}"

    if taxon['hasName']['citationMicro']:
        out += f" | {taxon['hasName']['citationMicro']}"

    # path not if we are at the root of all
    if os.path.split(taxon['pathString'])[0] != rootPath:
        taxon['path'].reverse()
        out += "\n__Path:__"
        for ancestor in taxon['path']:
            if len(ancestor['pathString']) <= len(rootPath) or ancestor['id'] == taxon['id']:
                continue
            out += f" {getTaxonLink(ancestor, rootPath, False)} >"
        out += f" {ancestor['hasName']['fullNameStringNoAuthorsPlain']}"

    # Synonyms
    if len(taxon['hasSynonym']):
        out += "\n\n### Synonyms"

    for synonym in taxon['hasSynonym']:
        out += f"\n- {synonym['fullNameStringPlain']}"

    # Children
    if len(taxon['hasPart']):
        out += "\n\n### Subtaxa"

        for child in taxon['hasPart']:
            out += f"\n- {getTaxonLink(child, rootPath)}"

    # References
    if len(taxon['hasName']['references']) > 0 or len(taxon['references']) > 0:
        out += "\n\n### References"

        # Nomenclatural
        if len(taxon['hasName']['references']) > 0:
            out += "\n#### Nomenclatural"
            # FIXME

        # Taxonomic
        if len(taxon['references']) > 0:
            out += "\n#### Taxonomic"
            # FIXME

    out += "\n\n---\n\n"
    return out


def getTaxonLink(taxon, rootPath, includeAuthors=True):
    filePath = os.path.split(taxon['pathString'][len(rootPath):])[0]
    if filePath != "/":
        filePath += "/"
    filePath += taxon['hasName']['fullNameStringNoAuthorsPlain']
    filePath += ".md"
    if includeAuthors:
        return f"[[{filePath}|{taxon['hasName']['fullNameStringPlain']}]]"
    else:
        return f"[[{filePath}|{taxon['hasName']['fullNameStringNoAuthorsPlain']}]]"


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
        sectionData[section] += line + "\n"

        # --- marks end of meta section
        if lineCount > 0 and section == 'meta' and line == '---':
            section = 'wfo'

        # --- marks end of wfo section
        if lineCount > 0 and section == 'wfo' and line.strip() == '---':
            section = 'body'

        lineCount += 1

    return sectionData


def getTaxonGraph(wfoId):
    # fetches all the data needed to populate one markdown file
    # or nothing if wfoId is inappropriate
    url = 'https://list.worldfloraonline.org/gql.php'

    query = """
query getTaxonGraph($wfoId: String!) {
  taxonNameById(nameId: $wfoId) {
    id
    fullNameStringPlain
    currentPreferredUsage {
      id
      pathString
      path {
        id
        pathString
        hasName {
          ...nameFields
        }
      }
      hasName {
        ...nameFields
      }
      hasSynonym {
        ...nameFields
      }
      hasPart {
        id
        pathString
        hasName {
          ...nameFields
        }
      }
      references {
        uri
        label
        comment
        kind
        thumbnailUri
      }
    }
  }
}
fragment nameFields on TaxonName {
  id
  fullNameStringHtml
  fullNameStringPlain
  fullNameStringNoAuthorsHtml
  fullNameStringNoAuthorsPlain
  authorsString
  citationMicro
  rank
  references{
    uri
    label
    comment
    kind
    thumbnailUri
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
