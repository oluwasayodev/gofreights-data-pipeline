from dotenv import dotenv_values
import sqlalchemy
import numpy as np
import pandas as pd
import pyodbc

config = dotenv_values()


def get_db_conn(conn_string="", dialect=None):
    if dialect in (None, ""):
        raise ValueError(
            "dialect is required.\n Currently supported dialects are (postgres[ql], msaccess)"
        )

    if dialect in ("postgres", "postgresql"):
        DB_USER = config.get("DB_USER")
        DB_PASSWORD = config.get("DB_PASSWORD")
        DB_HOST = config.get("DB_HOST")
        DB_PORT = config.get("DB_PORT", 5432)
        DB_NAME = config.get("DB_NAME")
        connection_string = (
            conn_string
            if conn_string
            else f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
        engine = sqlalchemy.create_engine(url=connection_string)
        return engine
    if dialect == "msaccess":
        ms_access_string = (
            rf"DRIVER={config.get('MSACCESS_DRIVER')};"
            rf"DBQ={config.get('MSACCESS_DB')};"
        )
        print(conn_string)
        print(ms_access_string)
        connection_string = conn_string if conn_string else ms_access_string
        print("connection string: ", conn_string)
        conn = pyodbc.connect(conn_string)
        return conn


def haversine_distance(
    lat1: pd.Series, lat2: pd.Series, long1: pd.Series, long2: pd.Series
):
    EARTH_RADIUS = 6371
    lat1 = lat1.values
    lat2 = lat2.values
    long1 = long1.values
    long2 = long2.values

    return (
        2
        * 1000  # in meters
        * EARTH_RADIUS
        * np.arcsin(
            np.sqrt(
                np.sin(np.deg2rad(lat2 - lat1) / 2) ** 2
                + (
                    np.cos(np.deg2rad(lat1))
                    * np.cos(np.deg2rad(lat2))
                    * np.sin(np.deg2rad(long2 - long1) / 2) ** 2
                )
            )
        )
    )


def get_lat_long_decimal(row):
    row["latitude"] = (row["Latitude_degrees"] + (row["Latitude_minutes"] / 60)) * (
        -1 if row[f"Latitude_hemisphere"] == "S" else 1
    )
    row["longitude"] = (row["Longitude_degrees"] + (row["Longitude_minutes"] / 60)) * (
        -1 if row[f"Longitude_hemisphere"] == "W" else 1
    )
    return row
