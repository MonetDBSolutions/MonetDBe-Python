def get_info():
    """
    Fetch some MonetDBe specific properties
    """
    from monetdbe import connect
    return connect("/tmp/test").execute("select * from env()").fetchall()
