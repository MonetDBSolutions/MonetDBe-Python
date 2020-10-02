typedef int64_t monetdbe_cnt;

typedef struct {
 unsigned char day;
 unsigned char month;
 short year;
} monetdbe_data_date;

typedef struct {
 unsigned int ms;
 unsigned char seconds;
 unsigned char minutes;
 unsigned char hours;
} monetdbe_data_time;

typedef struct {
 monetdbe_data_date date;
 monetdbe_data_time time;
} monetdbe_data_timestamp;

typedef struct {
 size_t size;
 char* data;
} monetdbe_data_blob;

typedef enum {
 monetdbe_bool, monetdbe_int8_t, monetdbe_int16_t, monetdbe_int32_t, monetdbe_int64_t,
 monetdbe_size_t, monetdbe_float, monetdbe_double,
 monetdbe_str, monetdbe_blob,
 monetdbe_date, monetdbe_time, monetdbe_timestamp,
 monetdbe_type_unknown
} monetdbe_types;

typedef struct {
 monetdbe_types type;
 void *data;
 size_t count;
 char* name;
} monetdbe_column;

struct monetdbe_table_t;
typedef struct monetdbe_table_t monetdbe_table;

typedef struct {
 size_t nparam;
 monetdbe_types *type;
} monetdbe_statement;

typedef struct {
 monetdbe_cnt nrows;
 size_t ncols;
 char *name;
 monetdbe_cnt last_id;
} monetdbe_result;

typedef void* monetdbe_database;

typedef struct {
 int memorylimit;
 int querytimeout;
 int sessiontimeout;
 int nr_threads;
} monetdbe_options;

typedef struct { monetdbe_types type; int8_t *data; size_t count; char *name; int8_t null_value; double scale; int (*is_null)(int8_t *value); } monetdbe_column_bool;
typedef struct { monetdbe_types type; int8_t *data; size_t count; char *name; int8_t null_value; double scale; int (*is_null)(int8_t *value); } monetdbe_column_int8_t;
typedef struct { monetdbe_types type; int16_t *data; size_t count; char *name; int16_t null_value; double scale; int (*is_null)(int16_t *value); } monetdbe_column_int16_t;
typedef struct { monetdbe_types type; int32_t *data; size_t count; char *name; int32_t null_value; double scale; int (*is_null)(int32_t *value); } monetdbe_column_int32_t;
typedef struct { monetdbe_types type; int64_t *data; size_t count; char *name; int64_t null_value; double scale; int (*is_null)(int64_t *value); } monetdbe_column_int64_t;

typedef struct { monetdbe_types type; size_t *data; size_t count; char *name; size_t null_value; double scale; int (*is_null)(size_t *value); } monetdbe_column_size_t;

typedef struct { monetdbe_types type; float *data; size_t count; char *name; float null_value; double scale; int (*is_null)(float *value); } monetdbe_column_float;
typedef struct { monetdbe_types type; double *data; size_t count; char *name; double null_value; double scale; int (*is_null)(double *value); } monetdbe_column_double;

typedef struct { monetdbe_types type; char * *data; size_t count; char *name; char * null_value; double scale; int (*is_null)(char * *value); } monetdbe_column_str;
typedef struct { monetdbe_types type; monetdbe_data_blob *data; size_t count; char *name; monetdbe_data_blob null_value; double scale; int (*is_null)(monetdbe_data_blob *value); } monetdbe_column_blob;

typedef struct { monetdbe_types type; monetdbe_data_date *data; size_t count; char *name; monetdbe_data_date null_value; double scale; int (*is_null)(monetdbe_data_date *value); } monetdbe_column_date;
typedef struct { monetdbe_types type; monetdbe_data_time *data; size_t count; char *name; monetdbe_data_time null_value; double scale; int (*is_null)(monetdbe_data_time *value); } monetdbe_column_time;
typedef struct { monetdbe_types type; monetdbe_data_timestamp *data; size_t count; char *name; monetdbe_data_timestamp null_value; double scale; int (*is_null)(monetdbe_data_timestamp *value); } monetdbe_column_timestamp;

extern int monetdbe_open(monetdbe_database *db, char *url, monetdbe_options *opts);

extern int monetdbe_close(monetdbe_database db);

extern char* monetdbe_error(monetdbe_database db);

extern char* monetdbe_get_autocommit(monetdbe_database dbhdl, int* result);
extern char* monetdbe_set_autocommit(monetdbe_database dbhdl, int value);
extern int monetdbe_in_transaction(monetdbe_database dbhdl);

extern char* monetdbe_query(monetdbe_database dbhdl, char* query, monetdbe_result** result, monetdbe_cnt* affected_rows);
extern char* monetdbe_result_fetch(monetdbe_result *mres, monetdbe_column** res, size_t column_index);
extern char* monetdbe_cleanup_result(monetdbe_database dbhdl, monetdbe_result* result);

extern char* monetdbe_prepare(monetdbe_database dbhdl, char *query, monetdbe_statement **stmt);
extern char* monetdbe_bind(monetdbe_statement *stmt, void *data, size_t parameter_nr);
extern char* monetdbe_execute(monetdbe_statement *stmt, monetdbe_result **result, monetdbe_cnt* affected_rows);
extern char* monetdbe_cleanup_statement(monetdbe_database dbhdl, monetdbe_statement *stmt);

extern char* monetdbe_append(monetdbe_database dbhdl, const char* schema, const char* table, monetdbe_column **input, size_t column_count);
extern const void* monetdbe_null(monetdbe_database dbhdl, monetdbe_types t);

extern char* monetdbe_get_table(monetdbe_database dbhdl, monetdbe_table** table, const char* schema_name, const char* table_name);
extern char* monetdbe_get_columns(monetdbe_database dbhdl, const char* schema_name, const char *table_name, size_t *column_count, char ***column_names, int **column_types);

extern char* monetdbe_dump_database(monetdbe_database dbhdl, const char *backupfile);
extern char* monetdbe_dump_table(monetdbe_database dbhdl, const char *schema_name, const char *table_name, const char *backupfile);
