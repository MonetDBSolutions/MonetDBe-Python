def get_info():
    """
    Fetch some MonetDBe specific properties
    """
    from monetdbe import connect
    return connect().execute("select * from env()").fetchall()
