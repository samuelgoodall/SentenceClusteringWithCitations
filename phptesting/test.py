import subprocess

if __name__ == "__main__":
    import subprocess

    result = subprocess.run(
        ['php', '/home/samuel/Desktop/WS2223Projekt/NLPProjekt/phptesting/tex2bib-master/index.php'],  # program and arguments
        check=True  # raise exception if program fails
    )
    resultstring = result.stdout
    print(resultstring)  # result.stdout contains a byte-string