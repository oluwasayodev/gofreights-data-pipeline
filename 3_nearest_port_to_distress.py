import pandas as pd
from utils import haversine_distance, get_db_conn, get_lat_long_decimal

distress_caller_lat = 32.610982
distress_caller_long = -38.706256

wpi_port_query = """
SELECT 
	DISTINCT
    "Wpi_country_code",
    "Main_port_name",
    "Latitude_degrees",
    "Latitude_minutes",
    "Latitude_hemisphere",
    "Longitude_degrees",
    "Longitude_minutes",
    "Longitude_hemisphere"
    FROM "Wpi Data"
WHERE "Supplies_provisions" = 'Y'
	AND "Supplies_water" = 'Y'
	AND "Supplies_fuel_oil" = 'Y'
	AND "Supplies_diesel_oil" = 'Y'
ORDER BY
   "Latitude_degrees",
   "Longitude_degrees",
   "Latitude_minutes",
   "Longitude_minutes";
"""



conn = get_db_conn(dialect="postgres")
wpi_port_df = pd.read_sql(wpi_port_query, con=conn)
wpi_port_df = wpi_port_df.apply(get_lat_long_decimal, axis=1)
wpi_port_df = wpi_port_df.loc[
    :, ["Wpi_country_code", "Main_port_name", "latitude", "longitude"]
]

wpi_port_df["distress_latitude"] = distress_caller_lat
wpi_port_df["distress_longitude"] = distress_caller_long

wpi_port_df["distance_from_distress_caller"] = haversine_distance(
    wpi_port_df["latitude"],
    wpi_port_df["distress_latitude"],
    wpi_port_df["longitude"],
    wpi_port_df["distress_longitude"],
)

countries_query = """SELECT * FROM "Country Codes" """
countries = pd.read_sql(countries_query, con=conn)

new_df = pd.merge(
    wpi_port_df, countries, left_on="Wpi_country_code", right_on="Country Code"
)
new_df.rename(
    columns={
        "Main_port_name": "port_name",
        "Country Name": "country",
        "Country Code": "country_code",
        "latitude": "port_latitude",
        "longitude": "port_longitude",
    },
    inplace=True,
)

nearest_port = (
    new_df.sort_values(by=["distance_from_distress_caller"])
    .reset_index()[["country", "port_name", "port_latitude", "port_longitude"]]
).head(1)

print(nearest_port)

postgres_con = get_db_conn(dialect='postgresql')
nearest_port.to_sql('3_nearest_port_to_distress', con=postgres_con, if_exists='replace', index=False)
