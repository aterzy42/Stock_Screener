def get_filtered_dates(conn, inflation_min, inflation_max, unemp_min, unemp_max, brent_min, brent_max, rate_min, rate_max, coffee_min, coffee_max):
    with conn.cursor() as cur:
        query = """
            SELECT data_month
            FROM (
                SELECT date_trunc('month', data_date)::date AS data_month,
                    MAX(CASE WHEN indicator_name = 'INFLATION' THEN indicator_value END) AS inflation,
                    MAX(CASE WHEN indicator_name = 'UNEMPLOYMENT' THEN indicator_value END) AS unemp,
                    MAX(CASE WHEN indicator_name = 'BRENT' THEN indicator_value END) AS brent,
                    MAX(CASE WHEN indicator_name = 'FEDERAL_FUNDS_RATE' THEN indicator_value END) AS rate,
                    MAX(CASE WHEN indicator_name = 'COFFEE' THEN indicator_value END) AS coffee
                FROM indicator_data id
                JOIN economic_indicators ei ON id.indicator_id = ei.indicator_id
                GROUP BY data_month
            ) sub
            WHERE 
                inflation BETWEEN %s AND %s AND
                unemp BETWEEN %s AND %s AND
                brent BETWEEN %s AND %s AND
                rate BETWEEN %s AND %s AND
                coffee BETWEEN %s AND %s
            ORDER BY data_month;
        """
        cur.execute(query, (inflation_min, inflation_max, unemp_min, unemp_max, brent_min, brent_max, rate_min, rate_max, coffee_min, coffee_max))
        rows = cur.fetchall()
        return [row[0].isoformat() for row in rows]


def get_index_returns(conn, start_date):
    with conn.cursor() as cur:
        query = """
SELECT 
    mi.index_name,
    ROUND(100 * (
        MAX(CASE WHEN date_trunc('month', performance_date)::date = (%s::date + INTERVAL '3 years') THEN metric_value END) / 
        MAX(CASE WHEN date_trunc('month', performance_date)::date = %s::date THEN metric_value END) - 1
    ), 2) AS return_3y,
    ROUND(100 * (
        MAX(CASE WHEN date_trunc('month', performance_date)::date = (%s::date + INTERVAL '5 years') THEN metric_value END) / 
        MAX(CASE WHEN date_trunc('month', performance_date)::date = %s::date THEN metric_value END) - 1
    ), 2) AS return_5y
FROM 
    index_performance ip
JOIN 
    market_indices mi ON ip.index_id = mi.index_id
JOIN 
    index_metrics im ON ip.metric_id = im.metric_id
WHERE 
    im.metric_name = 'Close'
GROUP BY 
    mi.index_name;


        """
        cur.execute(query, (start_date, start_date, start_date, start_date))
        rows = cur.fetchall()
        return [{"index": row[0], "return_3y": float(row[1] or 0), "return_5y": float(row[2] or 0)} for row in rows]


def get_index_performance_monthly(conn, start_date):
    with conn.cursor() as cur:
        query = """
        SELECT 
            mi.index_name,
            date_trunc('month', ip.performance_date)::date AS performance_date,
            ROUND(ip.metric_value, 2) AS close_value
        FROM 
            index_performance ip
        JOIN 
            market_indices mi ON ip.index_id = mi.index_id
        JOIN 
            index_metrics im ON ip.metric_id = im.metric_id
        WHERE 
            im.metric_name = 'Close'
            AND date_trunc('month', ip.performance_date)::date >= %s::date
            and ip.metric_value != 'NaN'
            and ip.metric_value is not null
        ORDER BY 
            mi.index_name,
            performance_date;
        """
        cur.execute(query, (start_date,))
        rows = cur.fetchall()
        return [
            {
                "index": row[0],
                "performance_date": row[1].isoformat(),
                "close_value": float(row[2])
            } for row in rows
        ]
