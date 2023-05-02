import re
from zipfile import ZipFile
from utils import download_google_document
import utils
import pandas as pd


try:
    file_url = "https://drive.google.com/file/d/1VyCGCAfFuEK7vB1C9Vq8iPdgBdu-LDM4/view"
    file_path_regex = re.compile("\/d\/([0-9a-zA-Z_-]+)\/")
    matches = file_path_regex.findall(file_url)
    file_id = matches[0]
    extract_filename = ""
    print(file_id)
    download_google_document(file_id, "gofreights.zip")

    with ZipFile("gofreights.zip", 'r') as zipfile:
        zipfile.extractall()
except Exception as e:
    print(e)
    
conn_string = (
    r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
    r"DBQ=C:\Users\hp\10alytics\gofreights-data-project\WPI.mdb;"
)

select_query = """SELECT * FROM "{}" """

msaccess = utils.get_db_conn(conn_string, dialect="msaccess")
postgres = utils.get_db_conn(dialect="postgres")
with msaccess.cursor() as access:
    tables = list(filter(lambda table: table[3] == "TABLE" and not table[2].startswith('~'), access.tables()))
    tables = list(map(lambda table: table[2], tables))

    for table in tables:
        df = pd.read_sql(select_query.format(table), con=msaccess)
        df.to_sql(table, if_exists='replace', con=postgres)