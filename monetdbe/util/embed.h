// todo gijs: check if just defining MT_Lock as void doesn't give any problems
typedef void MT_Lock;

typedef int8_t bit;
typedef int8_t bte;
typedef int16_t sht;
typedef int64_t lng;
typedef uint64_t ulng;
typedef void *ptr;
typedef int bat;
typedef size_t oid;

extern void c_delete( const void *p );

typedef struct sql_ref {
 int refcnt;
} sql_ref;

extern sql_ref *sql_ref_init(sql_ref *r);
extern int sql_ref_inc(sql_ref *r);
extern int sql_ref_dec(sql_ref *r);

typedef struct sql_allocator {
 size_t size;
 size_t nr;
 char **blks;
 size_t used;
 size_t usedmem;
} sql_allocator;

extern sql_allocator *sa_create(void);
extern sql_allocator *sa_reset( sql_allocator *sa );
extern void *sa_alloc( sql_allocator *sa, size_t sz );
extern void *sa_zalloc( sql_allocator *sa, size_t sz );
extern void *sa_realloc( sql_allocator *sa, void *ptr, size_t sz, size_t osz );
extern void sa_destroy( sql_allocator *sa );
extern char *sa_strndup( sql_allocator *sa, const char *s, size_t l);
extern char *sa_strdup( sql_allocator *sa, const char *s);
extern char *sa_strconcat( sql_allocator *sa, const char *s1, const char *s2);
extern size_t sa_size( sql_allocator *sa );

typedef int (*fkeyvalue) (void *data);

typedef struct sql_hash_e {
 int key;
 void *value;
 struct sql_hash_e *chain;
} sql_hash_e;

typedef struct sql_hash {
 sql_allocator *sa;
 int size;
 sql_hash_e **buckets;
 fkeyvalue key;
} sql_hash;

extern sql_hash *hash_new(sql_allocator *sa, int size, fkeyvalue key);
extern sql_hash_e *hash_add(sql_hash *ht, int key, void *value);
extern void hash_del(sql_hash *ht, int key, void *value);

extern unsigned int hash_key(const char *n);

typedef struct node {
 struct sql_hash_e e;
 struct node *next;
 void *data;
} node;

typedef void (*fdestroy) (void *);

typedef struct list {
 sql_allocator *sa;
 sql_hash *ht;
 MT_Lock ht_lock;
 fdestroy destroy;
 node *h;
 node *t;
 int cnt;
 int expected_cnt;
} list;

typedef int (*traverse_func) (void *clientdata, int seqnr, void *data);

extern list *list_create(fdestroy destroy);
extern list *sa_list(sql_allocator *sa);
extern list *list_new(sql_allocator *sa, fdestroy destroy);

extern void list_destroy(list *l);
extern int list_length(list *l);
extern int list_empty(list *l);

extern list *list_append(list *l, void *data);
extern list *list_append_before(list *l, node *n, void *data);
extern list *list_prepend(list *l, void *data);

extern node *list_remove_node(list *l, node *n);
extern void list_remove_data(list *l, void *data);
extern void list_remove_list(list *l, list *data);
extern void list_move_data(list *l, list *d, void *data);

extern int list_traverse(list *l, traverse_func f, void *clientdata);

typedef int (*fcmp) (void *data, void *key);
typedef void *(*fcmpvalidate) (void *v1, void *v2, void *extra, int *cmp);
typedef void *(*fvalidate) (void *v1, void *v2);
typedef int (*fcmp2) (void *data, void *v1, void *v2);
typedef void *(*fdup) (void *data);
typedef void *(*freduce) (void *v1, void *v2);
typedef void *(*freduce2) (sql_allocator *sa, void *v1, void *v2);
typedef void *(*fmap) (void *data, void *clientdata);

extern void *list_traverse_with_validate(list *l, void *data, fvalidate cmp);
extern void *list_append_with_validate(list *l, void *data, fvalidate cmp);
extern void *list_append_sorted(list *l, void *data, void *extra, fcmpvalidate cmp);
extern node *list_find(list *l, void *key, fcmp cmp);
extern int list_position(list *l, void *val);
extern void *list_fetch(list *l, int pos);
extern list *list_select(list *l, void *key, fcmp cmp, fdup dup);
extern list *list_order(list *l, fcmp cmp, fdup dup);
extern list *list_distinct(list *l, fcmp cmp, fdup dup);
extern void *list_reduce(list *l, freduce red, fdup dup);
extern void *list_reduce2(list *l, freduce2 red, sql_allocator *sa);
extern list *list_map(list *l, void *data, fmap f);
extern int list_cmp(list *l1, list *l2, fcmp cmp);

extern int list_match(list *l1, list *l2, fcmp cmp);

extern list *list_sort(list *l, fkeyvalue key, fdup dup);

extern list *list_keysort(list *l, int *key, fdup dup);

extern list *list_dup(list *l, fdup dup);
extern list *list_merge(list *l, list *data, fdup dup);
extern list *list_merge_destroy(list *l, list *data, fdup dup);

extern list *list_flaten(list *l);

extern void list_hash_delete(list *l, void *data, fcmp cmp);
extern void* list_hash_add(list *l, void *data, fcmp cmp);
extern void list_hash_clear(list *l);

typedef enum {
 Q_PARSE = 0,
 Q_TABLE = 1,
 Q_UPDATE = 2,
 Q_SCHEMA = 3,
 Q_TRANS = 4,
 Q_PREPARE = 5,
 Q_BLOCK = 6
} mapi_query_t;

typedef enum sql_dependency {
 SCHEMA_DEPENDENCY = 1,
 TABLE_DEPENDENCY = 2,
 COLUMN_DEPENDENCY = 3,
 KEY_DEPENDENCY = 4,
 VIEW_DEPENDENCY = 5,
 USER_DEPENDENCY = 6,
 FUNC_DEPENDENCY = 7,
 TRIGGER_DEPENDENCY = 8,
 OWNER_DEPENDENCY = 9,
 INDEX_DEPENDENCY = 10,
 FKEY_DEPENDENCY = 11,
 SEQ_DEPENDENCY = 12,
 PROC_DEPENDENCY = 13,
 BEDROPPED_DEPENDENCY = 14,
 TYPE_DEPENDENCY = 15
} sql_dependency;

extern const char *TID;

typedef enum temp_t {
 SQL_PERSIST = 0,
 SQL_LOCAL_TEMP = 1,
 SQL_GLOBAL_TEMP = 2,
 SQL_DECLARED_TABLE = 3,
 SQL_MERGE_TABLE = 4,
 SQL_STREAM = 5,
 SQL_REMOTE = 6,
 SQL_REPLICA_TABLE = 7
} temp_t;

typedef enum comp_type {
 cmp_gt = 0,
 cmp_gte = 1,
 cmp_lte = 2,
 cmp_lt = 3,
 cmp_equal = 4,
 cmp_notequal = 5,

 cmp_filter = 6,
 cmp_or = 7,
 cmp_in = 8,
 cmp_notin = 9,

 mark_in = 10,
 mark_notin = 11,
 mark_exists = 12,
 mark_notexists = 13,

 cmp_all = 14,
 cmp_project = 15,
 cmp_joined = 16,
 cmp_left = 17,
 cmp_left_project = 18
} comp_type;

typedef enum commit_action_t {
 CA_COMMIT,
 CA_DELETE,
 CA_PRESERVE,
 CA_DROP
} ca_t;

typedef int sqlid;

typedef struct sql_base {
 int wtime;
 int rtime;
 int stime;
 int allocated;
 int flags;
 int refcnt;
 sqlid id;
 char *name;
} sql_base;

extern void base_init(sql_allocator *sa, sql_base * b, sqlid id, int flags, const char *name);

typedef struct changeset {
 sql_allocator *sa;
 fdestroy destroy;
 struct list *set;
 struct list *dset;
 node *nelm;
} changeset;

extern void cs_new(changeset * cs, sql_allocator *sa, fdestroy destroy);
extern void cs_destroy(changeset * cs);
extern void cs_add(changeset * cs, void *elm, int flag);
extern void *cs_add_with_validate(changeset * cs, void *elm, int flag, fvalidate cmp);
extern void cs_add_before(changeset * cs, node *n, void *elm);
extern void cs_del(changeset * cs, node *elm, int flag);
extern void cs_move(changeset *from, changeset *to, void *data);
extern void *cs_transverse_with_validate(changeset * cs, void *elm, fvalidate cmp);
extern int cs_size(changeset * cs);
extern node *cs_find_name(changeset * cs, const char *name);
extern node *cs_find_id(changeset * cs, sqlid id);
extern node *cs_first_node(changeset * cs);
extern node *cs_last_node(changeset * cs);
extern void cs_remove_node(changeset * cs, node *n);

typedef void *backend_code;
typedef size_t backend_stack;

typedef struct sql_trans {
 char *name;
 int stime;
 int wstime;
 int rtime;
 int wtime;
 int schema_number;
 int schema_updates;
 int active;
 int status;
 list *dropped;
 list *moved_tables;

 changeset schemas;

 sql_allocator *sa;

 struct sql_trans *parent;
 backend_stack stk;
} sql_trans;

typedef struct sql_schema {
 sql_base base;
 sqlid auth_id;
 sqlid owner;
 bit system;

 changeset tables;
 changeset types;
 changeset funcs;
 changeset seqs;
 list *keys;
 list *idxs;
 list *triggers;

 char *internal;
 sql_trans *tr;
} sql_schema;

typedef enum sql_class {
 EC_ANY,
 EC_TABLE,
 EC_BIT,
 EC_CHAR,
 EC_STRING,
 EC_BLOB,
 EC_POS,
 EC_NUM,
 EC_MONTH,
 EC_SEC,
 EC_DEC,
 EC_FLT,
 EC_TIME,
 EC_TIME_TZ,
 EC_DATE,
 EC_TIMESTAMP,
 EC_TIMESTAMP_TZ,
 EC_GEOM,
 EC_EXTERNAL,
 EC_MAX
} sql_class;

typedef struct sql_type {
 sql_base base;

 char *sqlname;
 unsigned int digits;
 unsigned int scale;
 int localtype;
 unsigned char radix;
 unsigned int bits;
 sql_class eclass;
 sql_schema *s;
} sql_type;

typedef struct sql_alias {
 char *name;
 char *alias;
} sql_alias;

typedef struct sql_subtype {
 sql_type *type;
 unsigned int digits;
 unsigned int scale;
} sql_subtype;

typedef struct sql_arg {
 char *name;
 bte inout;
 sql_subtype type;
} sql_arg;

typedef enum sql_ftype {
 F_FUNC = 1,
 F_PROC = 2,
 F_AGGR = 3,
 F_FILT = 4,
 F_UNION = 5,
 F_ANALYTIC = 6,
 F_LOADER = 7
} sql_ftype;

typedef enum sql_flang {
 FUNC_LANG_INT = 0,
 FUNC_LANG_MAL = 1,
 FUNC_LANG_SQL = 2,
 FUNC_LANG_R = 3,
 FUNC_LANG_C = 4,
 FUNC_LANG_J = 5,

 FUNC_LANG_PY = 6,
 FUNC_LANG_MAP_PY = 7,

 FUNC_LANG_PY3 = 10,
 FUNC_LANG_MAP_PY3 = 11,
 FUNC_LANG_CPP = 12
} sql_flang;

typedef struct sql_func {
 sql_base base;

 char *imp;
 char *mod;
 sql_ftype type;
 list *ops;
 list *res;
 int nr;
 int sql;

 sql_flang lang;
 char *query;
 bit semantics;
 bit side_effect;
 bit varres;
 bit vararg;
 bit system;
 int fix_scale;

 sql_schema *s;
 sql_allocator *sa;
 void *rel;
} sql_func;

typedef struct sql_subfunc {
 sql_func *func;
 list *res;
 list *coltypes;
 list *colnames;
 char *sname, *tname;
} sql_subfunc;

typedef enum key_type {
 pkey,
 ukey,
 fkey
} key_type;

typedef struct sql_kc {
 struct sql_column *c;
 int trunc;
} sql_kc;

typedef enum idx_type {
 hash_idx,
 join_idx,
 oph_idx,
 no_idx,
 imprints_idx,
 ordered_idx,
 new_idx_types
} idx_type;

typedef struct sql_idx {
 sql_base base;
 idx_type type;
 struct list *columns;
 struct sql_table *t;
 struct sql_key *key;
 struct sql_idx *po;
 void *data;
} sql_idx;

typedef struct sql_key {
 sql_base base;
 key_type type;
 sql_idx *idx;

 struct list *columns;
 struct sql_table *t;
 int drop_action;
} sql_key;

typedef struct sql_ukey {
 sql_key k;
 list *keys;
} sql_ukey;

typedef struct sql_fkey {
 sql_key k;

 int on_delete;
 int on_update;
 struct sql_ukey *rkey;
} sql_fkey;

typedef struct sql_trigger {
 sql_base base;
 sht time;
 sht orientation;
 sht event;

 struct list *columns;

 struct sql_table *t;
 char *old_name;
 char *new_name;

 char *condition;
 char *statement;
} sql_trigger;

typedef struct sql_sequence {
 sql_base base;
 lng start;
 lng minvalue;
 lng maxvalue;
 lng increment;
 lng cacheinc;
 bit cycle;
 bit bedropped;
 sql_schema *s;
} sql_sequence;

typedef struct sql_column {
 sql_base base;
 sql_subtype type;
 int colnr;
 bit null;
 char *def;
 char unique;
 int drop_action;
 char *storage_type;
 int sorted;
 size_t dcount;
 char *min;
 char *max;

 struct sql_table *t;
 struct sql_column *po;
 void *data;
} sql_column;

typedef enum table_types {
 tt_table = 0,
 tt_view = 1,
 tt_merge_table = 3,
 tt_stream = 4,
 tt_remote = 5,
 tt_replica_table = 6
} table_types;

typedef struct sql_part_value {
 ptr value;
 size_t length;
} sql_part_value;

typedef struct sql_part {
 sql_base base;
 struct sql_table *t;
 sql_subtype tpe;
 bit with_nills;
 union {
  list *values;
  struct sql_range {
   ptr minvalue;
   ptr maxvalue;
   size_t minlength;
   size_t maxlength;
  } range;
 } part;
} sql_part;

typedef struct sql_expression {
 sql_subtype type;
 char *exp;
 list *cols;
} sql_expression;

typedef struct sql_table {
 sql_base base;
 sht type;
 sht access;
 bit system;
 bit bootstrap;
 bte properties;
 temp_t persistence;
 ca_t commit_action;
 char *query;
 int sz;

 sql_ukey *pkey;
 changeset columns;
 changeset idxs;
 changeset keys;
 changeset triggers;
 changeset members;
 int drop_action;

 int cleared;
 void *data;
 struct sql_schema *s;
 struct sql_table *po;

 struct sql_table *p;
 union {
  struct sql_column *pcol;
  struct sql_expression *pexp;
 } part;
} sql_table;

typedef struct sql_moved_table {
 sql_schema *from;
 sql_schema *to;
 sql_table *t;
} sql_moved_table;

typedef struct res_col {
 char *tn;
 char *name;
 sql_subtype type;
 bat b;
 int mtype;
 ptr *p;
} res_col;

typedef struct res_table {
 int id;
 oid query_id;
 mapi_query_t query_type;
 int nr_cols;
 int cur_col;
 const char *tsep;
 const char *rsep;
 const char *ssep;
 const char *ns;
 res_col *cols;
 bat order;
 struct res_table *next;
} res_table;

typedef struct sql_session {
 sql_trans *tr;

 char *schema_name;
 sql_schema *schema;

 char ac_on_commit;

 char auto_commit;
 int level;
 int status;
 backend_stack stk;
} sql_session;

extern void schema_destroy(sql_schema *s);
extern void table_destroy(sql_table *t);
extern void column_destroy(sql_column *c);
extern void key_destroy(sql_key *k);
extern void idx_destroy(sql_idx * i);

extern int base_key(sql_base *b);
extern node *list_find_name(list *l, const char *name);
extern node *list_find_id(list *l, sqlid id);
extern node *list_find_base_id(list *l, sqlid id);

extern sql_key *find_sql_key(sql_table *t, const char *kname);
extern node *find_sql_key_node(sql_schema *s, sqlid id);
extern sql_key *sql_trans_find_key(sql_trans *tr, sqlid id);

extern sql_idx *find_sql_idx(sql_table *t, const char *kname);
extern node *find_sql_idx_node(sql_schema *s, sqlid id);
extern sql_idx *sql_trans_find_idx(sql_trans *tr, sqlid id);

extern sql_column *find_sql_column(sql_table *t, const char *cname);

extern sql_part *find_sql_part(sql_table *t, const char *tname);

extern sql_table *find_sql_table(sql_schema *s, const char *tname);
extern sql_table *find_sql_table_id(sql_schema *s, sqlid id);
extern node *find_sql_table_node(sql_schema *s, sqlid id);
extern sql_table *sql_trans_find_table(sql_trans *tr, sqlid id);

extern sql_sequence *find_sql_sequence(sql_schema *s, const char *sname);

extern sql_schema *find_sql_schema(sql_trans *t, const char *sname);
extern sql_schema *find_sql_schema_id(sql_trans *t, sqlid id);
extern node *find_sql_schema_node(sql_trans *t, sqlid id);

extern sql_type *find_sql_type(sql_schema * s, const char *tname);
extern sql_type *sql_trans_bind_type(sql_trans *tr, sql_schema *s, const char *name);
extern node *find_sql_type_node(sql_schema *s, sqlid id);
extern sql_type *sql_trans_find_type(sql_trans *tr, sqlid id);

extern sql_func *find_sql_func(sql_schema * s, const char *tname);
extern list *find_all_sql_func(sql_schema * s, const char *tname, sql_ftype type);
extern sql_func *sql_trans_bind_func(sql_trans *tr, const char *name);
extern sql_func *sql_trans_find_func(sql_trans *tr, sqlid id);
extern node *find_sql_func_node(sql_schema *s, sqlid id);

extern node *find_sql_trigger_node(sql_schema *s, sqlid id);
extern sql_trigger *sql_trans_find_trigger(sql_trans *tr, sqlid id);

extern void *sql_values_list_element_validate_and_insert(void *v1, void *v2, void *tpe, int* res);
extern void *sql_range_part_validate_and_insert(void *v1, void *v2);
extern void *sql_values_part_validate_and_insert(void *v1, void *v2);

/*
typedef struct {
 BAT *b;
 char* name;
 void* def;
} sql_emit_col;
*/

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
 void* data;
} monetdb_data_blob;

typedef enum {
 monetdb_int8_t, monetdb_int16_t, monetdb_int32_t, monetdb_int64_t, monetdb_size_t,
 monetdb_float, monetdb_double,
 monetdb_str, monetdb_blob,
 monetdb_date, monetdb_time, monetdb_timestamp
} monetdb_types;

typedef struct {
 monetdb_types type;
 void *data;
 size_t count;
 char* name;
} monetdb_column;

typedef struct {
 lng nrows;
 size_t ncols;
 int type;
 lng id;
} monetdb_result;

typedef void* monetdb_connection;
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
extern char* monetdb_startup(char* dbdir, _Bool sequential);
extern _Bool monetdb_is_initialized(void);

extern char* monetdb_get_autocommit(monetdb_connection conn, int* result);
extern char* monetdb_set_autocommit(monetdb_connection conn, int value);
extern char* monetdb_query(monetdb_connection conn, char* query, monetdb_result** result, lng* affected_rows, int* prepare_id);

extern char* monetdb_result_fetch(monetdb_connection conn, monetdb_column** res, monetdb_result* mres, size_t column_index);
extern char* monetdb_result_fetch_rawcol(monetdb_connection conn, res_col** res, monetdb_result* mres, size_t column_index);

extern char* monetdb_clear_prepare(monetdb_connection conn, int id);
extern char* monetdb_send_close(monetdb_connection conn, int id);

extern char* monetdb_append(monetdb_connection conn, const char* schema, const char* table, bat *batids, size_t column_count);
extern char* monetdb_cleanup_result(monetdb_connection conn, monetdb_result* result);
extern char* monetdb_get_table(monetdb_connection conn, sql_table** table, const char* schema_name, const char* table_name);
extern char* monetdb_get_columns(monetdb_connection conn, const char* schema_name, const char *table_name, size_t *column_count, char ***column_names, int **column_types);

extern char* monetdb_shutdown(void);
