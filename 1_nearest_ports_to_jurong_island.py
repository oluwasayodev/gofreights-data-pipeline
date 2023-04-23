import requests
from zipfile import ZipFile
import re
import pandas as pd
from utils import get_db_conn


google_drive_url = "https://drive.google.com/uc"
# file_url = 'https://drive.google.com/file/d/1SzmRIwlpL5PrFuaUe_1TAcMV0HYHMD_b/view'
file_url = "https://drive.google.com/file/d/1VyCGCAfFuEK7vB1C9Vq8iPdgBdu-LDM4/view"
file_path_regex = re.compile("\/d\/([0-9a-zA-Z_-]+)\/")
matches = file_path_regex.findall(file_url)
file_id = matches[0]
print(file_id)


def download_google_document(file_id: str, destination: str):
    params = dict(id=file_id, confirm=1, export="download")
    res = requests.get(google_drive_url, params=params, stream=True)
    with open(destination, "wb") as file:
        file.write(res.content)


# download_google_document(file_id, "gofreights.zip")

# with ZipFile("gofreights.zip", 'r') as zipfile:
#     zipfile.extractall()

conn_string = (
    r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
    r"DBQ=C:\Users\hp\10alytics\gofreights-data-project\WPI.mdb;"
)


# query = """SELECT c.[Country Name] , COUNT(wpi.[Load_offload_wharves])
# FROM [Wpi Data] wpi
# INNER JOIN [Country Codes] c ON c.[Country Code] = wpi.[Wpi_country_code]
# WHERE wpi.[Load_offload_wharves] = 'Y'
# GROUP BY c.[Country Name]
# ORDER BY COUNT(wpi.[Load_offload_wharves]) DESC;
# """

query = r"""
SELECT country, COUNT(has_port) as port_count FROM (
	SELECT c.[Country Name] AS country, wpi.[Load_offload_wharves] AS has_port
	FROM [Wpi Data] wpi
	INNER JOIN [Country Codes] c ON c.[Country Code] = wpi.[Wpi_country_code]
	WHERE wpi.[Load_offload_wharves] = 'Y'
) sub
GROUP BY country
ORDER BY COUNT(has_port) DESC;
"""
conn = get_db_conn(conn_string, dialect='msaccess')

df = pd.read_sql(query, con=conn)

pg_conn = get_db_conn(dialect='postgres')
df.head(1).to_sql('2_country_with_highest_wharves', index=False, if_exists='replace', con=pg_conn)
