import pandas as pd
from utils import get_db_conn


query = r"""
SELECT country, COUNT(has_port) as port_count FROM (
	SELECT c."Country Name" AS country, wpi."Load_offload_wharves" AS has_port
	FROM "Wpi Data" wpi
	INNER JOIN "Country Codes" c ON c."Country Code" = wpi."Wpi_country_code"
	WHERE wpi."Load_offload_wharves" = 'Y'
) sub
GROUP BY country
ORDER BY COUNT(has_port) DESC;
"""


conn = get_db_conn(dialect='postgres')

df = pd.read_sql(query, con=conn)

df.head(1).to_sql('2_country_with_highest_wharves', index=False, if_exists='replace', con=conn)
