"""
Scrapes information from the icd9data.com website.

Python 2.7.x
"""

import json
import requests
from bs4 import BeautifulSoup

base_url = "http://www.icd9data.com"
root_path = "/2015/Volume1/default.htm"

icd9_data = requests.get(base_url + root_path)
icd9_bs = BeautifulSoup(icd9_data.text, "lxml")

# first level codes
lvl1 = icd9_bs.ul.find_all('li')
codes = []

def build_node(href, code, descr, depth):
    node = {}

    node['href'] = href
    node['code'] = code
    node['depth'] = depth
    node['descr'] = descr

    return node


def get_children(lvl_doc):
    """
    Extracts the relevant UL object in lvl_root. We assume
    the two list types are mutually exclusive.
    """
    lst_root = lvl_doc.find('div', class_='definitionList')
    if lst_root is not None:
        lst_root = lst_root.ul
    if lst_root is None:
        lst_root = lvl_doc.find('ul', class_='definitionList')
    if lst_root is None:
        lst_root = lvl_doc.find('ul', class_='codeHierarchyUL')

    return list(lst_root.children)


def parse_base_cat(lvl, depth, path_so_far):
    """
    Parses base category icd9data information (ranged categories).
    """
    depth += 1
    base_path = list(path_so_far) # copy path_so_far
    for code_group in lvl:
        path_so_far = list(base_path)
        code = code_group.a.text
        text_gen = code_group.strings
        descr = None
        for descr in code_group.strings:
            pass
        href = code_group.a['href']

        node = build_node(href, code, descr, depth)
        path_so_far.append(node)

        print base_url + node['href']
        next_lvl_data = requests.get(base_url + node['href'])
        next_lvl_data = BeautifulSoup(next_lvl_data.text, "lxml")
        next_lvl = get_children(next_lvl_data)

        if (next_lvl[0].img is not None
            and (next_lvl[0].img['alt'] == 'Non-specific code'
                 or next_lvl[0].img['alt'] == 'Specific code' )):
            # we're at 3-digit codes now
            parse_specific(next_lvl, depth, list(path_so_far))

        else:
            # then we're still in ranged categories
            parse_base_cat(next_lvl, depth, list(path_so_far))


def build_specific_node(code, depth):
    """
    Builds specific-level (3+ digit) nodes
    """
    href = code.a['href']
    code_str = code.a.text
    descr = code.find("span", class_="threeDigitCodeListDescription").text

    return build_node(href, code_str, descr, depth)


def parse_specific(lvl, depth, path_so_far):
    """
    Parses specific-level (3+ digits) icd9 information
    """
    depth += 1
    start = 0

    base_path = list(path_so_far)
    if lvl[0].img['alt'] == 'Non-specific code':
        # we're leading with the previous level code, don't add again
        start = 1
    code_iter = iter(lvl[start:])

    code = code_iter.next()
    while True:
        try:
            path_so_far = list(base_path) # make a copy

            if code.find_all('img')[-1]['alt'] == 'Non-specific code':
                path_so_far.append(build_specific_node(code, depth))
                specific_path = list(path_so_far)
                non_specific_code = code.a.text
                depth += 1
                code = code_iter.next()

                while (code.find_all('img')[-1]['alt'] != 'Non-specific code'
                       and code.a.text.startswith(non_specific_code)):
                    path_so_far = list(specific_path)
                    path_so_far.append(build_specific_node(code, depth))

                    codes.append(path_so_far) # add to global list
                    code = code_iter.next()

                depth -= 1
                continue

            elif code.find_all('img')[-1]['alt'] == 'Specific code':
                # at a leaf code
                path_so_far = list(path_so_far)
                path_so_far.append(build_specific_node(code, depth))
                codes.append(path_so_far)

            code = code_iter.next()
        except StopIteration:
            break


if __name__ == '__main__':
    for base in lvl1:
        depth = 0
        path_so_far = []
        parse_base_cat([base], depth, path_so_far)

    print len(codes)
    with open('codes.json', 'w') as outfile:
        json.dump(codes, outfile)
