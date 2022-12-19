import json
import string
import subprocess
import bibtexparser


class Bibentry(object):
    def __init__(self, publisher:str, address:str,year:str,title:str,author:str,ENTRYTYPE:str,ID:str):
        self.publisher = publisher
        self.address = address
        self.year = year
        self.title = title
        self.author = author
        self.ENTRYTPE = ENTRYTYPE
        self.ID = ID


def convert_texfile_2_bib_entries(php_convertion_script_file, tex_input_file):
    """
    Uses this Bib 2 convert tex2bib: https://github.com/juusechec/tex2bib
    that is based on :https://text2bib.economics.utoronto.ca/index.php/index
    Parameters
    ----------
    php_convertion_script_file : str
        the path to the convertion script file
    tex_input_file : str
        tex file with the bibitems that are to be converted
    """
    result = subprocess.run(
        ['php', php_convertion_script_file,
         tex_input_file],  # program and arguments
        text=True,
        capture_output=True,
        check=True  # raise exception if program fails
    )
    resultstring: string = result.stdout
    print(resultstring)
    print("NEWLINES",resultstring.count('\n'))
    bib_entries = bibtexparser.loads(resultstring).entries
    return bib_entries

def check_how_many_titles_are_usable(bibentrie_title_list: list):
    accepted = 0
    for i,bibentry in enumerate(bibentrie_title_list):
        if(bibentrie_title_list!=""):
            accepted += 1
    i=i+1
    acceptancerate = accepted/i

    return i,accepted,acceptancerate


def get_list_of_titles(bib_entries):
    def helper(bibentry:dict):
        return bibentry['title']
    return list(map(helper,bib_entries))


if __name__ == "__main__":
    tex_input_file = '/mnt/c/Users/sgoodall/Desktop/archive/NLPProjekt/phptesting/tex2bib-master/example-cites.tex'
    php_convertion_script_file = '/mnt/c/Users/sgoodall/Desktop/archive/NLPProjekt/phptesting/tex2bib-master/index.php'
    bib_entries = convert_texfile_2_bib_entries(php_convertion_script_file=php_convertion_script_file, tex_input_file=tex_input_file)
    print(len(bib_entries))
    print("Usable Titles",check_how_many_titles_are_usable(get_list_of_titles(bib_entries)))
    print(len(get_list_of_titles(bib_entries)))

