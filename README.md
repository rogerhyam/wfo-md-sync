# WFO Markdown Synchronizer 

__VERY MUCH UNDER CONSTRUCTION__

A script to keep a local set of markdown files in sync with the WFO PlantList taxonomy.

The  [World Flora Online (WFO)](http://www.worldfloraonline.org/) is the international initiative to achieve Target 1 of the Global Strategy for Plant Conservation and provides a global overview of the diversity of plant species. It is the essential tool for conservation planners, policymakers and practitioners at all levels.

The [WFO PlantList (WfoPlantList)](https://wfoplantlist.org/) is a collaborative project within the WFO to maintain a consensus nomenclature and classification of plants to act as a __taxonomic backbone__ for the WFO and other projects.

The [WfoPlantList API](https://list.worldfloraonline.org/) provided machine readable access to the WfoPlantList so that it can be used in other projects.

This Python script will query the API to create and maintain a set of [Markdown](https://en.wikipedia.org/wiki/Markdown) text files in sync with the current taxonomy and nomenclature. This means that researchers can work on a local set of notes that are bound to the global consensus view of plant diversity.

The initial intent is for the markdown files to be edited using the [Obsidian](https://obsidian.md/) application, possibly with taxonomically focussed plugins, but any editor or IDE could be used. The local markdown files could be versioned and backed up to GitHub. They could also be published directly to the web or to print via some intermediate applications.

## Modes of Operation

The script can be used in two different modes.

In __Monographic Mode__ the script synchronizes with a complete branch of the classification below a root taxon. The root taxon's ID is specified in a configuration file. This is appropriate for working on a genus, family or other taxon.

In __Floristic Mode__ the user provides a CSV file which contains a list of WFO name IDs. The script then synchronizes files for these taxa only, along with any of their parent taxa. This is appropriate for working on geographically or ecologically restricted projects where a subset of taxa are of interest, possibly spread right across the diversity of plants.

## Requirements

The script is run from the command line. You must be familiar with running simple scripts and manipulating some simple text and CSV files.

### Python 3 (required)

You must have Python3 installed on your machine. Type 

```
python3 --version
```

at the command prompt to see if you have it.

### Git (recommended)

It is possible to download the code from GitHub and install it on your machine but it is far easier to install it and keep it up to date by using the git application. You don't need to know much about git, just the commands here, but we would recommend you become familiar enough to version and backup your own work using git in the long run.








