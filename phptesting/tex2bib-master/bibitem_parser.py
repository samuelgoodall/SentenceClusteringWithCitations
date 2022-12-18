import string
import subprocess
import bibtexparser

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
    bib_entries = bibtexparser.loads(resultstring).entries
    return bib_entries

if __name__ == "__main__":
    tex_input_file = '/home/samuel/Desktop/WS2223Projekt/NLPProjekt/phptesting/tex2bib-master/example-cites.tex'
    php_convertion_script_file = '/home/samuel/Desktop/WS2223Projekt/NLPProjekt/phptesting/tex2bib-master/index.php'
    bib_entries = convert_texfile_2_bib_entries(php_convertion_script_file=php_convertion_script_file, tex_input_file=tex_input_file)
    print("BIBENTRIES:",bib_entries)
