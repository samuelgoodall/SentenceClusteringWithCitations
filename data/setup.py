
#unzips the archive.zip file of the meta data
from zipfile import ZipFile

print("starting extraction")
with ZipFile('archive.zip','r') as file:
    file.extractall()
print("finished extraction")

