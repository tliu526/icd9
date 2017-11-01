# Python library for ICD9 Codes

## My edits
A fork of [sirrice's ICD9 repository](https://github.com/sirrice/icd9).
The target website in the original repo
has inconsistent structure and as a result the ICD9 data pulled is incomplete.
Here I put together a simple scraper using requests and BeautifulSoup that
targets the icd9data.com website to generate the `code.json` used by the `ICD9`
class. The structure is consistent and complete for the 2015 ICD9-CM Volume 1
diagnosis codes.

## Description

The library encodes ICD9 codes in their natural hierarchy.  For example,
Cholera due to vibrio cholerae has the ICD9 code `0010`, and are categorized as
as type of Cholera, which in turn is a type of Intestinal Infectious Disease.
Specifically, `001.0` has the following hierarchy:

  001-139     Infectious and Parasitic Diseases
    001-009   Intestinal Infectious Diseases
      001     Cholera
        001.0 Cholera due to vibrio cholerae

This library encodes all ICD9 codes into a tree that captures this
relationship.  

## Using the library

Include `icd9.py` in your python path.  The following is an example:

  from icd9 import ICD9

  tree = ICD9('codes.json')

  # list of top level codes (e.g., '001-139', ...)
  toplevelnodes = tree.children
  toplevelcodes = [node.code for node in toplevelnodes]
  print '\t'.join(toplevelcodes)


The hierarchy is encoded in a tree of `Node` objects.  `Node` has the following methods:

`search(code)`

  # find all sub-nodes whose codes contain '001'
  tree.search('001')

`find(code)`

  # find sub-node with code '001.0'. Returns None if code is not found
  tree.find('001.0')

And the following properties:

`children`

  # get node's children
  tree.children

  # search for '001.0' in root's first child
  tree.children[0].search('001.0')

`parent`

  # get 001.0 node's parent.  None if node is a root
  tree.find('001.0').parent

`parents`

  # get 001.0 node's parent path from the root.  Root node is the first element
  tree.find('001.0').parents

`leaves`

  # get all leaf nodes under root's first child
  tree.children[0].leaves

`siblings`

  # get all of 001.0 node's siblings that share the same parent
  tree.find('001.0').siblings

 `description`

 # get the text description of the node
 tree.find('001.0').description

## Scraper

`icd9_data_scraper.py` creates a json file `codes.json` of each ICD9 code's parent codes:

  [None, "001-139", "001-009", "001", "001.0"]

The last element is the actual code, the preceeding elements are coarser groupings of codes.
