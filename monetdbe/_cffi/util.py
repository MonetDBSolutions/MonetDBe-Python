def get_info() -> dict:
    """
    Fetch some MonetDBe specific properties
    """
    from monetdbe import connect
    return dict(connect("/tmp/test").execute("select * from env()").fetchall())
