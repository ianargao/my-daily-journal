# My Diary — Flask + MySQL

This version uses MySQL instead of SQLite while keeping the same UI design.

## 1. Create the database

Open MySQL Workbench and run:

```sql
CREATE DATABASE IF NOT EXISTS diary_db;
USE diary_db;
```

Then run the complete `diary_db.sql` file included in this folder.

## 2. Check MySQL credentials

Open `app.py` and update:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "diary_db"
}
```

If your MySQL root account has a password, put it in `"password"`.

Example:

```python
"password": "1234"
```

## 3. Install Python packages

PowerShell:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 4. Start MySQL

If using XAMPP, start **MySQL** from the XAMPP Control Panel.

If using MySQL Workbench with a MySQL Server installation, make sure the MySQL service is running.

## 5. Run Flask

```powershell
python app.py
```

Open:

http://127.0.0.1:5000

## Database relationship

users
  |
  | 1-to-many
  v
diary_entries

One user can have many diary entries.

## CRUD

Create  -> New Entry
Read    -> Dashboard / All Entries / View Entry
Update  -> Edit Entry
Delete  -> Delete Entry
