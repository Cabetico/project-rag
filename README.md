### Generate uv env

```bash
uv venv
```

* Activate env
  
  ```bash
    source .venv/bin/activate
  ```  

* For using the venv in jupyter notebook, installing kernel
```bash
uv pip install ipykernel
python -m ipykernel install --user --name=.venv --display-name "Python (uv .venv)"
```

* uninstalling kernel
```bash
    jupyter kernelspec list
```

```bash
    jupyter kernelspec uninstall .venv
```

### *Encounter Issue*

Gunicorn workers were doing race condition between mulltiple workers hitting Qdrant (`get_collection()`) before Qdrant server was up

* Summary
Here’s what’s happening:

* Your Gunicorn worker starts up, imports rag.py.

* `rag.py`  calls `ingest.load_index()` at import time.

* That function tries to `get_collection()`, doesn’t find it immediately (race condition between multiple workers hitting Qdrant), so it goes ahead and creates it.

* Another worker does the same thing at the same time → duplicate `create_collection` → `409 Conflict`.

* Gunicorn sees a worker crash → exits the master with code 3.

### *Solution* 

* **this chunk of code at `app.py`** 
```
# ✅ Initialize collection only once before workers start
with app.app_context():
    ingest.load_index()
``` 
* **run initialization exactly once before Gunicorn forks workers**

Create a small init step (run once) that calls `ingest.load_index()` and only then starts Gunicorn. This guarantees one-time init and avoids worker races. `entrypoint.sh`


### CURL

```
curl -X POST http://localhost:8000/question \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the meaning of life?"}'
```

```
curl -X POST http://localhost:8000/question \
  -H "Content-Type: application/json" \
  -d '{"question": "which are the policies?"}'
```

### Postgres service

* test connection with `test_pg_connection.py`, once inside the container with `docker exec -it <container_name> bash` you need to start the env
with `source .venv/bin/activate` after that run `python test_pg_connection.py`. Remember the `python:3.12-slim` does not have the libraries, it's the
`.venv` the virtual enviroment with the needed libraries. after testint the connection the output should be 


```bash
  ✅ Connected to Postgres: ('PostgreSQL 16.3 (Debian 16.3-1) on x86_64-pc-linux-gnu...',)
```


### PGadmin

🔑 Access

* Open `http://localhost:5050`

* Login with:

  * Email: `admin@admin.com`

  * Password: `admin`

➕ **Add a Postgres server in pgAdmin**

1. Once inside pgAdmin, click **Add New Server**.

2. In **General → Name**: `Postgres (docker)` (or any label).

3. In **Connection**:

    * Host name/address: **postgres** (this matches the service name in Docker Compose)

    * Port: **5432**

    * Database: **course_assistant** (from your env file)

    * Username: **your_username**

    * Password: **your_password**
  

### Feedback

```bash
ID="6e1cc7c4-c194-43f3-8c26-0ceaa29107fd"

FEEDBACK_DATA='{
  "conversation_id": "'${ID}'",
  "feedback": 1
}'

curl -X POST -H "Content-Type: application/json" -d "${FEEBACK_DATA}" ${URL}/feedback
```