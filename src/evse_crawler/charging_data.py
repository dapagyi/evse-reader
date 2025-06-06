import calendar
from datetime import datetime, timedelta
from flask import Blueprint, current_app

from evse_crawler.db import get_db

from evse_crawler.refresh_charging_data import (
    refresh_charging_data,
)

bp = Blueprint(
    "charging_data",
    __name__,
)


@bp.route("/refresh-charging-data")
def _refresh_charging_data():
    base_url = current_app.config["EVSE_BASE_URL"]
    username = current_app.config["EVSE_USERNAME"]
    password = current_app.config["EVSE_PASSWORD"]

    db = get_db()
    refresh_charging_data(db, base_url, username, password)

    return {}


@bp.route("/results")
def get_charging_data_from_db():
    db = get_db()

    # Get the most recent session
    row = db.execute(
        """
        SELECT start_time, end_time, energy_kWh
        FROM charging
        ORDER BY start_time DESC
        LIMIT 1
        """
    ).fetchone()

    last_session = (
        {
            "start_datetime": row[0],
            "end_datetime": row[1],
            "energy_kwh": row[2],
        }
        if row
        else None
    )

    # Total energy
    total_energy = (
        db.execute("SELECT SUM(energy_kWh) FROM charging").fetchone()[0] or 0.0
    )

    # Current month energy
    now = datetime.now()
    first_day = now.replace(day=1)
    first_day_next_month = (first_day + timedelta(days=32)).replace(day=1)

    current_month_energy = (
        db.execute(
            """
            SELECT SUM(energy_kWh)
            FROM charging
            WHERE start_time >= ? AND start_time < ?
            """,
            (first_day.strftime("%Y-%m-%d"), first_day_next_month.strftime("%Y-%m-%d")),
        ).fetchone()[0]
        or 0.0
    )

    total_records = db.execute("SELECT COUNT(*) FROM charging").fetchone()[0] or 0

    # Last 3 full months: collect data
    monthly_energies = []
    for i in range(1, 4):
        year = now.year
        month = now.month - i
        if month <= 0:
            month += 12
            year -= 1

        start_date = datetime(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = datetime(year, month, last_day) + timedelta(days=1)

        energy = (
            db.execute(
                """
                SELECT SUM(energy_kWh)
                FROM charging
                WHERE start_time >= ? AND start_time < ?
                """,
                (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")),
            ).fetchone()[0]
            or 0.0
        )

        monthly_energies.append(
            {"month": start_date.strftime("%m"), "year": year, "energy_kwh": energy}
        )

    return {
        "last_session": last_session,
        "total_energy": total_energy,
        "current_month_energy": current_month_energy,
        "total_records": total_records,
        "last_3_months": monthly_energies,
    }
