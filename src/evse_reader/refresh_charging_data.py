import requests
import urllib3
import sqlite3
import polars as pl
import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def login(base_url: str, username: str, password: str) -> requests.Session:
    login_url = f"{base_url}/cgi-bin/cgiServer?worker=Login"
    data = dict(lang="en", login=username, password=password, remember="on")
    session = requests.Session()
    response = session.post(login_url, data=data, verify=False)

    if response.status_code == 200:
        return session
    else:
        raise Exception("Login failed!")


def download_charging_data_csv(session: requests.Session, base_url: str) -> None:
    # Step 1: Trigger the export (if needed, depending on server behavior)
    initial_url = f"{base_url}/cgi-bin/cgiServer?worker=DisplayChargeDetails&cdrType=manual&cdrFileName=/tmp/export.csv&localIP=192.168.100.102&longProcessing=true"
    session.get(initial_url, verify=False)

    # Step 2: Download the actual exported file
    download_url = f"{base_url}/cgi-bin/cgiServer?worker=ExportFile&filePath=/tmp/&filename=export.csv"
    response = session.get(download_url, verify=False)

    if (
        response.status_code == 200
        and response.headers.get("Content-Type") == "application/octet-stream"
    ):
        with open("export.csv", "wb") as f:
            f.write(response.content)
    else:
        raise Exception("Failed to download file.")


def load_charging_data_into_db(db: sqlite3.Connection) -> None:
    df = pl.read_csv(
        "export.csv",
        separator=";",
        try_parse_dates=True,
        null_values=[""],
        decimal_comma=True,
    )

    df = df.with_columns([pl.col("Energy_kWh").cast(pl.Float64).alias("Energy_kWh")])

    for row in df.iter_rows(named=True):
        db.execute(
            """
            INSERT OR IGNORE INTO charging (
                charge_number_internal,
                charge_type,
                start_time,
                end_time,
                energy_kWh,
                duration
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                int(row["CDR_ID"]),
                row["Type of charge"],
                row["Start_Datetime"].strftime("%Y-%m-%d %H:%M:%S"),
                row["End_Datetime"].strftime("%Y-%m-%d %H:%M:%S"),
                row["Energy_kWh"],
                row["Duration"].strftime("%H:%M:%S")
                if isinstance(row["Duration"], datetime.time)
                else str(row["Duration"]),
            ),
        )
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    db.execute(
        """
        INSERT INTO app_state (key, value)
        VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value;
        """,
        ("last_updated", now),
    )

    db.commit()


def refresh_charging_data(
    db: sqlite3.Connection, base_url: str, username: str, password: str
) -> None:
    session = login(base_url, username, password)
    download_charging_data_csv(session, base_url)
    load_charging_data_into_db(db)
