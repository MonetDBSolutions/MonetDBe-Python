#include "monetdb/monetdbe.h"

void initialize_string_array_from_numpy(char** restrict output, size_t size, char* restrict numpy_string_input, size_t stride_length, bool* restrict mask) {
    if (mask) for   (size_t i = 0; i < size; i++) {
        output[i] = mask[i] ? NULL : numpy_string_input + i*stride_length;
    }
    else for        (size_t i = 0; i < size; i++) {
        output[i] = numpy_string_input + i*stride_length;
    }
}

// The way to convert a numpy datetime to datetime struct is actually in numpy source code at multiarray/datetime.c.
// 
/*
 * Converts a datetime based on the given metadata into a datetimestruct
 */

/* The FR in the unit names stands for frequency */
typedef enum {
        /* Force signed enum type, must be -1 for code compatibility */
        NPY_FR_ERROR = -1,      /* error or undetermined */

        /* Start of valid units */
        NPY_FR_Y = 0,           /* Years */
        NPY_FR_M = 1,           /* Months */
        NPY_FR_W = 2,           /* Weeks */
        /* Gap where 1.6 NPY_FR_B (value 3) was */
        NPY_FR_D = 4,           /* Days */
        NPY_FR_h = 5,           /* hours */
        NPY_FR_m = 6,           /* minutes */
        NPY_FR_s = 7,           /* seconds */
        NPY_FR_ms = 8,          /* milliseconds */
        NPY_FR_us = 9,          /* microseconds */
        NPY_FR_ns = 10,         /* nanoseconds */
        NPY_FR_ps = 11,         /* picoseconds */
        NPY_FR_fs = 12,         /* femtoseconds */
        NPY_FR_as = 13,         /* attoseconds */
        NPY_FR_GENERIC = 14     /* unbound units, can convert to anything */
} NPY_DATETIMEUNIT;

/*
 * Converts a substring given by 'str' and 'len' into
 * a date time unit enum value. The 'metastr' parameter
 * is used for error messages, and may be NULL.
 *
 * Returns NPY_DATETIMEUNIT on success, NPY_FR_ERROR on failure.
 */
static NPY_DATETIMEUNIT
parse_datetime_unit_from_string(char const *str)
{
    size_t len = strlen(str);
    /* Use switch statements so the compiler can make it fast */
    if (len == 1) {
        switch (str[0]) {
            case 'Y':
                return NPY_FR_Y;
            case 'M':
                return NPY_FR_M;
            case 'W':
                return NPY_FR_W;
            case 'D':
                return NPY_FR_D;
            case 'h':
                return NPY_FR_h;
            case 'm':
                return NPY_FR_m;
            case 's':
                return NPY_FR_s;
        }
    }
    /* All the two-letter units are variants of seconds */
    else if (len == 2 && str[1] == 's') {
        switch (str[0]) {
            case 'm':
                return NPY_FR_ms;
            case 'u':
                return NPY_FR_us;
            case 'n':
                return NPY_FR_ns;
            case 'p':
                return NPY_FR_ps;
            case 'f':
                return NPY_FR_fs;
            case 'a':
                return NPY_FR_as;
        }
    }
    else if (len == 3 && !strncmp(str, "\xce\xbcs", 3)) {
        /* greek small letter mu, utf8-encoded */
        return NPY_FR_us;
    }
    else if (len == 7 && !strncmp(str, "generic", 7)) {
        return NPY_FR_GENERIC;
    }

    return -1;
}

typedef struct {
        int64_t year;
        int32_t month, day, hour, min, sec, us, ps, as;
} npy_datetimestruct;

typedef int64_t npy_datetime;

/*
 * Returns 1 if the given year is a leap year, 0 otherwise.
 */
static int
is_leapyear(int64_t year)
{
    return (year & 0x3) == 0 && /* year % 4 == 0 */
           ((year % 100) != 0 ||
            (year % 400) == 0);
}

/*
 * Computes the python `ret, d = divmod(d, unit)`.
 *
 * Note that GCC is smart enough at -O2 to eliminate the `if(*d < 0)` branch
 * for subsequent calls to this command - it is able to deduce that `*d >= 0`.
 */
static inline
int64_t extract_unit_64(int64_t *d, int64_t unit) {
    assert(unit > 0);
    int64_t div = *d / unit;
    int64_t mod = *d % unit;
    if (mod < 0) {
        mod += unit;
        div -= 1;
    }
    assert(mod >= 0);
    *d = mod;
    return div;
}

static int64_t
days_to_yearsdays(int64_t *days_)
{
    const int64_t days_per_400years = (400*365 + 100 - 4 + 1);
    /* Adjust so it's relative to the year 2000 (divisible by 400) */
    int64_t days = (*days_) - (365*30 + 7);
    int64_t year;

    /* Break down the 400 year cycle to get the year and day within the year */
    year = 400 * extract_unit_64(&days, days_per_400years);

    /* Work out the year/day within the 400 year cycle */
    if (days >= 366) {
        year += 100 * ((days-1) / (100*365 + 25 - 1));
        days = (days-1) % (100*365 + 25 - 1);
        if (days >= 365) {
            year += 4 * ((days+1) / (4*365 + 1));
            days = (days+1) % (4*365 + 1);
            if (days >= 366) {
                year += (days-1) / 365;
                days = (days-1) % 365;
            }
        }
    }

    *days_ = days;
    return year + 2000;
}

/* Days per month, regular year and leap year */
int _days_per_month_table[2][12] = {
    { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 },
    { 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 }
};

/*
 * Fills in the year, month, day in 'dts' based on the days
 * offset from 1970.
 */
static void
set_datetimestruct_days(int64_t days, npy_datetimestruct *dts)
{
    int *month_lengths, i;

    dts->year = days_to_yearsdays(&days);
    month_lengths = _days_per_month_table[is_leapyear(dts->year)];

    for (i = 0; i < 12; ++i) {
        if (days < month_lengths[i]) {
            dts->month = i + 1;
            dts->day = (int)days + 1;
            return;
        }
        else {
            days -= month_lengths[i];
        }
    }
}

/*
 * Port numpy#13188 https://github.com/numpy/numpy/pull/13188/
 *
 * Computes the python `ret, d = divmod(d, unit)`.
 *
 * Note that GCC is smart enough at -O2 to eliminate the `if(*d < 0)` branch
 * for subsequent calls to this command - it is able to deduce that `*d >= 0`.
 */
int64_t extract_unit(npy_datetime *d, npy_datetime unit) {
    assert(unit > 0);
    int64_t div = *d / unit;
    int64_t mod = *d % unit;
    if (mod < 0) {
        mod += unit;
        div -= 1;
    }
    assert(mod >= 0);
    *d = mod;
    return div;
}

/* The special not-a-time (NaT) value */
#define NPY_MAX_INT64 9223372036854775807L
#define NPY_MIN_INT64 (-NPY_MAX_INT64 - 1L)
#define NPY_DATETIME_NAT NPY_MIN_INT64

static
void pandas_datetime_to_datetimestruct(npy_datetime dt, NPY_DATETIMEUNIT base, npy_datetimestruct *out) {
    int64_t perday;


    /* NaT is signaled in the year */
    if (dt == NPY_DATETIME_NAT) {
        out->year = NPY_DATETIME_NAT;
        return;
    }

    /* Initialize the output to all zeros */
    memset(out, 0, sizeof(npy_datetimestruct));
    out->year = 1970;
    out->month = 1;
    out->day = 1;

    /*
     * Note that care must be taken with the / and % operators
     * for negative values.
     */
    switch (base) {
        case NPY_FR_Y:
            out->year = 1970 + dt;
            break;

        case NPY_FR_M:
            out->year  = 1970 + extract_unit(&dt, 12);
            out->month = dt + 1;
            break;

        case NPY_FR_W:
            /* A week is 7 days */
            set_datetimestruct_days(dt * 7, out);
            break;

        case NPY_FR_D:
            set_datetimestruct_days(dt, out);
            break;

        case NPY_FR_h:
            perday = 24LL;

            set_datetimestruct_days(extract_unit(&dt, perday), out);
            out->hour = dt;
            break;

        case NPY_FR_m:
            perday = 24LL * 60;

            set_datetimestruct_days(extract_unit(&dt, perday), out);
            out->hour = (int)extract_unit(&dt, 60);
            out->min = (int)dt;
            break;

        case NPY_FR_s:
            perday = 24LL * 60 * 60;

            set_datetimestruct_days(extract_unit(&dt, perday), out);
            out->hour = (int)extract_unit(&dt, 60 * 60);
            out->min  = (int)extract_unit(&dt, 60);
            out->sec  = (int)dt;
            break;

        case NPY_FR_ms:
            perday = 24LL * 60 * 60 * 1000;

            set_datetimestruct_days(extract_unit(&dt, perday), out);
            out->hour = (int)extract_unit(&dt, 1000LL * 60 * 60);
            out->min  = (int)extract_unit(&dt, 1000LL * 60);
            out->sec  = (int)extract_unit(&dt, 1000LL);
            out->us   = (int)(dt * 1000);
            break;

        case NPY_FR_us:
            perday = 24LL * 60LL * 60LL * 1000LL * 1000LL;

            set_datetimestruct_days(extract_unit(&dt, perday), out);
            out->hour = (int)extract_unit(&dt, 1000LL * 1000 * 60 * 60);
            out->min  = (int)extract_unit(&dt, 1000LL * 1000 * 60);
            out->sec  = (int)extract_unit(&dt, 1000LL * 1000);
            out->us   = (int)dt;
            break;

        case NPY_FR_ns:
            perday = 24LL * 60LL * 60LL * 1000LL * 1000LL * 1000LL;

            set_datetimestruct_days(extract_unit(&dt, perday), out);
            out->hour = (int)extract_unit(&dt, 1000LL * 1000 * 1000 * 60 * 60);
            out->min  = (int)extract_unit(&dt, 1000LL * 1000 * 1000 * 60);
            out->sec  = (int)extract_unit(&dt, 1000LL * 1000 * 1000);
            out->us   = (int)extract_unit(&dt, 1000LL);
            out->ps   = (int)(dt * 1000);
            break;

        case NPY_FR_ps:
            perday = 24LL * 60 * 60 * 1000 * 1000 * 1000 * 1000;

            set_datetimestruct_days(extract_unit(&dt, perday), out);
            out->hour = (int)extract_unit(&dt, 1000LL * 1000 * 1000 * 60 * 60);
            out->min  = (int)extract_unit(&dt, 1000LL * 1000 * 1000 * 60);
            out->sec  = (int)extract_unit(&dt, 1000LL * 1000 * 1000);
            out->us   = (int)extract_unit(&dt, 1000LL);
            out->ps   = (int)(dt * 1000);
            break;

        case NPY_FR_fs:
            /* entire range is only +- 2.6 hours */
            out->hour = (int)extract_unit(&dt, 1000LL * 1000 * 1000 * 1000 *
                                        1000 * 60 * 60);
            if (out->hour < 0) {
                out->year  = 1969;
                out->month = 12;
                out->day   = 31;
                out->hour  += 24;
                assert(out->hour >= 0);
            }
            out->min  = (int)extract_unit(&dt, 1000LL * 1000 * 1000 * 1000 *
                                        1000 * 60);
            out->sec  = (int)extract_unit(&dt, 1000LL * 1000 * 1000 * 1000 *
                                        1000);
            out->us   = (int)extract_unit(&dt, 1000LL * 1000 * 1000);
            out->ps   = (int)extract_unit(&dt, 1000LL);
            out->as   = (int)(dt * 1000);
            break;

        case NPY_FR_as:
            /* entire range is only +- 9.2 seconds */
            out->sec = (int)extract_unit(&dt, 1000LL * 1000 * 1000 * 1000 *
                                        1000 * 1000);
            if (out->sec < 0) {
                out->year  = 1969;
                out->month = 12;
                out->day   = 31;
                out->hour  = 23;
                out->min   = 59;
                out->sec   += 60;
                assert(out->sec >= 0);
            }
            out->us   = (int)extract_unit(&dt, 1000LL * 1000 * 1000 * 1000);
            out->ps   = (int)extract_unit(&dt, 1000LL * 1000);
            out->as   = (int)dt;
            break;

        default:
            // TODO: error
            assert(0);
    }
}

void initialize_timestamp_array_from_numpy(
    monetdbe_database dbhdl,
    void* restrict output, const size_t size,
    int64_t* restrict numpy_datetime_input, char const *unit_string,
    const monetdbe_types type) {

    NPY_DATETIMEUNIT base = parse_datetime_unit_from_string(unit_string);

    // TODO: handle error

    npy_datetimestruct out;
    for (size_t i = 0; i < size; i++) {
        npy_datetime dt = numpy_datetime_input[i];
        pandas_datetime_to_datetimestruct(dt, base, &out);

        monetdbe_data_timestamp*    ts  = NULL;
        monetdbe_data_date*         d   = NULL;
        monetdbe_data_time*         t   = NULL;

        switch (type) {
        case monetdbe_timestamp: {
            ts  = &((monetdbe_data_timestamp*) output)[i];
            d = &ts->date;
            t = &ts->time;
            break;
        }
        case monetdbe_date: {
            d = &((monetdbe_data_date*) output)[i];
            break;
        }
            // TODO error wrong type
        }

        if (out.year == NPY_DATETIME_NAT) switch (type) {
            // nil value
            case monetdbe_timestamp: {
                *ts = *(monetdbe_data_timestamp*) monetdbe_null(dbhdl, monetdbe_timestamp);
                continue;
            }
            case monetdbe_date: {
                *d = *(monetdbe_data_date*) monetdbe_null(dbhdl, monetdbe_date);
                continue;
            }
        }

        d->year  = (short) out.year;
        d->month = (unsigned char) out.month;
        d->day   = (unsigned char) out.day;

        if (t) {
            t->hours     = (unsigned char) out.hour;
            t->minutes   = (unsigned char) out.min;
            t->seconds   = (unsigned char) out.sec;
            t->ms        = (unsigned int) (out.us / 1000);
        }
    }
}
