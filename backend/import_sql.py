"""
import_sql.py  —  Import dbms_project.sql into TiDB Cloud
Run once:  py import_sql.py
"""
import mysql.connector
import re
import os

SQL_FILE = os.path.join(os.path.dirname(__file__), '..', 'dbms_project.sql')

conn = mysql.connector.connect(
    host='gateway01.ap-southeast-1.prod.alicloud.tidbcloud.com',
    port=4000,
    user='2T1MoCaZ4MFtmuK.root',
    password='ejw69NTTncW3fYjG',
    ssl_disabled=False,
    autocommit=True,
)
cursor = conn.cursor()

# Ensure the database exists and use it
cursor.execute("CREATE DATABASE IF NOT EXISTS Agro")
cursor.execute("USE Agro")
cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

# Read the SQL file
with open(SQL_FILE, 'r', encoding='utf-8') as f:
    raw = f.read()

# Remove lines that switch DB context — we handle that above
raw = re.sub(r'(?im)^\s*create\s+database\s+\w+\s*;', '', raw)
raw = re.sub(r'(?im)^\s*use\s+\w+\s*;', '', raw)

# Drop existing tables in reverse-dependency order so re-runs are clean
drop_order = [
    'Product_Shipments', 'Retail_Outlets', 'Distribution_Centers',
    'Processing_Plants', 'Storage_Facilities', 'Harvests',
    'Pesticide_Applications', 'Irrigation_Systems', 'Soil_Samples',
    'Weather_Readings', 'Livestock', 'Crop_Plantings',
    'Crops', 'Fields', 'Farms',
]
print("Dropping existing tables...")
for tbl in drop_order:
    try:
        cursor.execute(f"DROP TABLE IF EXISTS `{tbl}`")
        print(f"  Dropped {tbl}")
    except Exception as e:
        print(f"  Skip {tbl}: {e}")

# Re-order CREATE TABLE statements so Storage_Facilities comes before Processing_Plants
# Split into individual statements
stmts = [s.strip() for s in raw.split(';') if s.strip()]

create_stmts = []
other_stmts  = []
for s in stmts:
    if re.match(r'(?i)^\s*create\s+table', s):
        create_stmts.append(s)
    else:
        other_stmts.append(s)

# Move Storage_Facilities before Processing_Plants
def tbl_name(s):
    m = re.search(r'(?i)create\s+table\s+`?(\w+)`?', s)
    return m.group(1).lower() if m else ''

create_ordered = []
sf_stmt = next((s for s in create_stmts if tbl_name(s) == 'storage_facilities'), None)
pp_stmt = next((s for s in create_stmts if tbl_name(s) == 'processing_plants'), None)

for s in create_stmts:
    n = tbl_name(s)
    if n == 'processing_plants':
        if sf_stmt and sf_stmt not in create_ordered:
            create_ordered.append(sf_stmt)
        create_ordered.append(s)
    elif n == 'storage_facilities':
        continue  # already inserted above if needed
    else:
        create_ordered.append(s)

final_stmts = create_ordered + other_stmts

print(f"\nExecuting {len(final_stmts)} statements...")
ok = 0
errors = []
for stmt in final_stmts:
    if not stmt.strip():
        continue
    try:
        cursor.execute(stmt)
        # Consume any result set (e.g. SELECT statements)
        try:
            cursor.fetchall()
        except Exception:
            pass
        ok += 1
    except Exception as e:
        msg = str(e)
        errors.append((stmt[:60].replace('\n',' '), msg[:100]))

cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
cursor.close()
conn.close()

print(f"\nDone: {ok} OK | {len(errors)} errors")
if errors:
    print("\nFirst 10 errors:")
    for stmt_preview, err in errors[:10]:
        print(f"  [{stmt_preview}...]  => {err}")

# Quick verification
conn2 = mysql.connector.connect(
    host='gateway01.ap-southeast-1.prod.alicloud.tidbcloud.com',
    port=4000,
    user='2T1MoCaZ4MFtmuK.root',
    password='ejw69NTTncW3fYjG',
    database='Agro',
    ssl_disabled=False,
)
cur2 = conn2.cursor()
cur2.execute("SHOW TABLES")
tables = [r[0] for r in cur2.fetchall()]
print(f"\nTables in Agro ({len(tables)}):")
for t in tables:
    cur2.execute(f"SELECT COUNT(*) FROM `{t}`")
    count = cur2.fetchone()[0]
    print(f"  {t:30s}  {count:>5} rows")
cur2.close()
conn2.close()
print("\nImport complete!")
