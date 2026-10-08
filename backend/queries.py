from database import get_db


def _fetch(sql, params=None, one=False):
    """Run a read query and return dict rows (or a single dict if one=True)."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(sql, params or ())
        return cursor.fetchone() if one else cursor.fetchall()
    finally:
        cursor.close()
        db.close()


def _clean(row):
    """MySQL SUM() returns Decimal/None; convert to plain ints for JSON/LLM use."""
    if row is None:
        return None
    out = {}
    for k, v in row.items():
        if v is None:
            out[k] = 0
        elif hasattr(v, "as_tuple"):  # Decimal
            out[k] = int(v)
        elif hasattr(v, "isoformat"):  # datetime
            out[k] = v.isoformat(sep=" ", timespec="seconds")
        else:
            out[k] = v
    return out


def get_high_risk_count():
    row = _fetch(
        "SELECT COUNT(*) AS n FROM potholes WHERE risk_level = 'HIGH'", one=True
    )
    return int(row["n"])


def get_statistics():
    row = _fetch(
        """
        SELECT
            COUNT(*) AS total,
            SUM(risk_level = 'HIGH') AS high_risk,
            SUM(risk_level = 'MEDIUM') AS medium_risk,
            SUM(risk_level = 'LOW') AS low_risk
        FROM potholes
        """,
        one=True,
    )
    return _clean(row)


def get_route_summary():
    rows = _fetch(
        """
        SELECT
            route,
            COUNT(*) AS total,
            SUM(risk_level = 'HIGH') AS high_risk,
            SUM(risk_level = 'MEDIUM') AS medium_risk,
            SUM(risk_level = 'LOW') AS low_risk
        FROM potholes
        GROUP BY route
        ORDER BY high_risk DESC, total DESC
        """
    )
    return [_clean(r) for r in rows]


def get_daily_summary():
    row = _fetch(
        """
        SELECT
            COUNT(*) AS total,
            SUM(risk_level = 'HIGH') AS high_risk,
            SUM(risk_level = 'MEDIUM') AS medium_risk,
            SUM(risk_level = 'LOW') AS low_risk
        FROM potholes
        WHERE DATE(timestamp) = CURDATE()
        """,
        one=True,
    )
    return _clean(row)


def get_route_condition(route):
    row = _fetch(
        """
        SELECT
            COUNT(*) AS total,
            SUM(risk_level = 'HIGH') AS high_risk,
            SUM(risk_level = 'MEDIUM') AS medium_risk,
            SUM(risk_level = 'LOW') AS low_risk
        FROM potholes
        WHERE route = %s
        """,
        (route,),
        one=True,
    )
    return _clean(row)


def get_priority_incidents(limit=5):
    rows = _fetch(
        """
        SELECT id, route, severity_score, confidence, risk_level,
               latitude, longitude
        FROM potholes
        ORDER BY severity_score DESC
        LIMIT %s
        """,
        (int(limit),),
    )
    return [_clean(r) for r in rows]


def get_incidents(limit=100):
    rows = _fetch(
        """
        SELECT id, route, timestamp, confidence, risk_level, severity_score,
               latitude, longitude
        FROM potholes
        ORDER BY timestamp DESC, id DESC
        LIMIT %s
        """,
        (int(limit),),
    )
    return [_clean(r) for r in rows]


def get_known_routes():
    rows = _fetch("SELECT DISTINCT route FROM potholes ORDER BY route")
    return [r["route"] for r in rows]


def insert_pothole(route, confidence, risk_level, severity_score,
                   latitude, longitude, timestamp=None):
    """Insert one detection (used by the YOLO integration and POST /incidents)."""
    db = get_db()
    cursor = db.cursor()
    try:
        if timestamp is None:
            cursor.execute(
                """
                INSERT INTO potholes
                (route, timestamp, confidence, risk_level, severity_score,
                 latitude, longitude)
                VALUES (%s, NOW(), %s, %s, %s, %s, %s)
                """,
                (route, confidence, risk_level.upper(), severity_score,
                 latitude, longitude),
            )
        else:
            cursor.execute(
                """
                INSERT INTO potholes
                (route, timestamp, confidence, risk_level, severity_score,
                 latitude, longitude)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (route, timestamp, confidence, risk_level.upper(),
                 severity_score, latitude, longitude),
            )
        db.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        db.close()
