from datetime import datetime, time, date

PARSE_DECLTYPES = 1
PARSE_COLNAMES = 2
converters = {}
adapters = {}

def register_adapter(k, v):
    global adapters
    adapters[k] = v


def register_converter(k, v):
    global converters
    converters[k] = v


def register_adapters_and_converters():
    def adapt_date(val):
        return val.isoformat()

    def adapt_datetime(val):
        return val.isoformat(" ")

    def convert_date(val):
        return date(*map(int, val.split(b"-")))

    def convert_timestamp(val):
        datepart, timepart = val.split(b" ")
        year, month, day = map(int, datepart.split(b"-"))
        timepart_full = timepart.split(b".")
        hours, minutes, seconds = map(int, timepart_full[0].split(b":"))
        if len(timepart_full) == 2:
            microseconds = int('{:0<6.6}'.format(timepart_full[1].decode()))
        else:
            microseconds = 0

        val = datetime(year, month, day, hours, minutes, seconds, microseconds)
        return val

    register_adapter(date, adapt_date)
    register_adapter(datetime, adapt_datetime)
    register_converter("date", convert_date)
    register_converter("timestamp", convert_timestamp)


register_adapters_and_converters()

# Clean up namespace
del register_adapters_and_converters
