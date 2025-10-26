<!-- markdownlint-disable -->

<a href="../../devices/database.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `database.py`




**Global Variables**
---------------
- **TYPE_CHECKING**


---

## <kbd>class</kbd> `DatabaseHandler`




<a href="../../devices/database.py#L71"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(db_file_path: str)
```








---

<a href="../../devices/database.py#L78"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `generate_schema`

```python
generate_schema() → None
```

Define and create the schema for the SQLite database. Add all CREATE TABLE statements here. 

---

<a href="../../devices/database.py#L127"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `heartbeat`

```python
heartbeat()
```





---

<a href="../../devices/database.py#L115"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `log`

```python
log(device: str, data: Any)
```





---

<a href="../../devices/database.py#L122"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `record_image`

```python
record_image(image_data: Dict)
```






---

## <kbd>class</kbd> `SQLiteAPI`
A simple SQLite database interface using only native Python modules. 

<a href="../../devices/database.py#L10"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(db_path: str = 'database.db')
```

Initialize the connection to the SQLite database. 




---

<a href="../../devices/database.py#L65"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `close`

```python
close() → None
```

Close the database connection. 

---

<a href="../../devices/database.py#L34"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `create_table`

```python
create_table(table_name: str, columns: str) → None
```

Create a table if it doesn’t exist. 



**Example:**
  db.create_table("users", "id INTEGER PRIMARY KEY, name TEXT, age INTEGER") 

---

<a href="../../devices/database.py#L60"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `delete`

```python
delete(table: str, condition: str, params: Tuple[Any, ]) → None
```

Delete records from a table based on a condition. 

---

<a href="../../devices/database.py#L17"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `execute`

```python
execute(query: str, params: Tuple[Any, ] = ()) → None
```

Execute a query (INSERT, UPDATE, DELETE, etc.). 

---

<a href="../../devices/database.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `fetch_all`

```python
fetch_all(query: str, params: Tuple[Any, ] = ()) → List[Row]
```

Execute a SELECT query and return all rows. 

---

<a href="../../devices/database.py#L27"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `fetch_one`

```python
fetch_one(query: str, params: Tuple[Any, ] = ()) → Optional[Row]
```

Execute a SELECT query and return one row. 

---

<a href="../../devices/database.py#L43"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `insert`

```python
insert(table: str, data: dict) → None
```

Insert a record into a table. 

---

<a href="../../devices/database.py#L51"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `update`

```python
update(table: str, data: dict, condition: str, params: Tuple[Any, ]) → None
```

Update records in a table based on a condition. 


