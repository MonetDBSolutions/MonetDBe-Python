typedef int64_t lng;
typedef int64_t monetdb_cnt;

typedef struct {
 unsigned char day;
 unsigned char month;
 int year;
} monetdb_data_date;

typedef struct {
 unsigned int ms;
 unsigned char seconds;
 unsigned char minutes;
 unsigned char hours;
} monetdb_data_time;

typedef struct {
 monetdb_data_date date;
 monetdb_data_time time;
} monetdb_data_timestamp;

typedef struct {
 size_t size;
 char* data;
} monetdb_data_blob;

typedef enum {
 monetdb_bool, monetdb_int8_t, monetdb_int16_t, monetdb_int32_t, monetdb_int64_t,

 monetdb_int128_t,

 monetdb_size_t, monetdb_float, monetdb_double,
 monetdb_str, monetdb_blob,
 monetdb_date, monetdb_time, monetdb_timestamp
} monetdb_types;

typedef struct {
 monetdb_types type;
 void *data;
 size_t count;
 char* name;
} monetdb_column;

struct monetdb_table_t;
typedef struct monetdb_table_t monetdb_table;

typedef struct {
 monetdb_cnt nrows;
 size_t ncols;
 int type;
 monetdb_cnt id;
} monetdb_result;

typedef void* monetdb_connection;
typedef struct { monetdb_types type; int8_t *data; size_t count; char *name; int8_t null_value; double scale; int (*is_null)(int8_t value); } monetdb_column_bool;
typedef struct { monetdb_types type; int8_t *data; size_t count; char *name; int8_t null_value; double scale; int (*is_null)(int8_t value); } monetdb_column_int8_t;
typedef struct { monetdb_types type; int16_t *data; size_t count; char *name; int16_t null_value; double scale; int (*is_null)(int16_t value); } monetdb_column_int16_t;
typedef struct { monetdb_types type; int32_t *data; size_t count; char *name; int32_t null_value; double scale; int (*is_null)(int32_t value); } monetdb_column_int32_t;
typedef struct { monetdb_types type; int64_t *data; size_t count; char *name; int64_t null_value; double scale; int (*is_null)(int64_t value); } monetdb_column_int64_t;

typedef struct { monetdb_types type; size_t *data; size_t count; char *name; size_t null_value; double scale; int (*is_null)(size_t value); } monetdb_column_size_t;

typedef struct { monetdb_types type; float *data; size_t count; char *name; float null_value; double scale; int (*is_null)(float value); } monetdb_column_float;
typedef struct { monetdb_types type; double *data; size_t count; char *name; double null_value; double scale; int (*is_null)(double value); } monetdb_column_double;

typedef struct { monetdb_types type; char * *data; size_t count; char *name; char * null_value; double scale; int (*is_null)(char * value); } monetdb_column_str;
typedef struct { monetdb_types type; monetdb_data_blob *data; size_t count; char *name; monetdb_data_blob null_value; double scale; int (*is_null)(monetdb_data_blob value); } monetdb_column_blob;

typedef struct { monetdb_types type; monetdb_data_date *data; size_t count; char *name; monetdb_data_date null_value; double scale; int (*is_null)(monetdb_data_date value); } monetdb_column_date;
typedef struct { monetdb_types type; monetdb_data_time *data; size_t count; char *name; monetdb_data_time null_value; double scale; int (*is_null)(monetdb_data_time value); } monetdb_column_time;
typedef struct { monetdb_types type; monetdb_data_timestamp *data; size_t count; char *name; monetdb_data_timestamp null_value; double scale; int (*is_null)(monetdb_data_timestamp value); } monetdb_column_timestamp;

extern char* monetdb_connect(monetdb_connection *conn);
extern char* monetdb_disconnect(monetdb_connection conn);
extern char* monetdb_startup(char* dbdir, 
                                                  _Bool 
                                                       sequential);
extern 
               _Bool 
                     monetdb_is_initialized(void);

extern char* monetdb_get_autocommit(monetdb_connection conn, int* result);
extern char* monetdb_set_autocommit(monetdb_connection conn, int value);
extern int monetdb_in_transaction(monetdb_connection conn);

extern char* monetdb_query(monetdb_connection conn, char* query, monetdb_result** result, monetdb_cnt* affected_rows, int* prepare_id);
extern char* monetdb_result_fetch(monetdb_connection conn, monetdb_result *mres, monetdb_column** res, size_t column_index);

extern char* monetdb_clear_prepare(monetdb_connection conn, int id);
extern char* monetdb_send_close(monetdb_connection conn, int id);

extern char* monetdb_append(monetdb_connection conn, const char* schema, const char* table, monetdb_column **input, size_t column_count);

extern char* monetdb_cleanup_result(monetdb_connection conn, monetdb_result* result);
extern char* monetdb_get_table(monetdb_connection conn, monetdb_table** table, const char* schema_name, const char* table_name);

extern char* monetdb_get_columns(monetdb_connection conn, const char* schema_name, const char *table_name, size_t *column_count, char ***column_names, int **column_types);

extern char* monetdb_shutdown(void);
