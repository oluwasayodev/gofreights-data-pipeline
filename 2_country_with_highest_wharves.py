import pandas as pd
from utils import get_db_conn, haversine_distance, get_lat_long_decimal

wpi_port_query = """
SELECT 
	DISTINCT
    [Latitude_degrees],
    [Latitude_minutes],
    [Latitude_hemisphere],
    [Longitude_degrees],
    [Longitude_minutes],
    [Longitude_hemisphere], 
    [Wpi_country_code],
    [Main_port_name]
    FROM [Wpi Data]
WHERE [Latitude_hemisphere] IS NOT NULL
ORDER BY
   [Latitude_degrees],
   [Longitude_degrees],
   [Latitude_minutes],
   [Longitude_minutes];
"""

conn_string = (
    r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
    r"DBQ=C:\Users\hp\10alytics\gofreights-data-project\WPI.mdb;"
)


conn = get_db_conn(conn_string, dialect="msaccess")

wpi_port_df = pd.read_sql(wpi_port_query, con=conn)


wpi_port_df = wpi_port_df.apply(get_lat_long_decimal, axis=1)
wpi_port_df = wpi_port_df.loc[
    :, ["Wpi_country_code", "Main_port_name", "latitude", "longitude"]
]
singapore_jurong_port_df = wpi_port_df[
    (wpi_port_df["Wpi_country_code"] == "SG")
    & (wpi_port_df["Main_port_name"] == "JURONG ISLAND")
]

wpi_port_df["distance_in_meters"] = haversine_distance(
    singapore_jurong_port_df["latitude"],
    wpi_port_df["latitude"],
    singapore_jurong_port_df["longitude"],
    wpi_port_df["longitude"],
)


nearest_ports = wpi_port_df.sort_values(by=["distance_in_meters"]).iloc[1:6, :]
nearest_ports.rename({"Main_port_name": "port_name"}, inplace=True, axis=1)

nearest_ports = nearest_ports.loc[:, ["port_name", "distance_in_meters"]]
nearest_ports = nearest_ports.round({"distance_in_meters": 2})

engine = get_db_conn(dialect="postgres")
nearest_ports.to_sql(
    "1_nearest_ports_to_jurong_island", con=engine, if_exists="replace", index=False
)

print(nearest_ports)
