import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost',
        database='omicshub',
        user='postgres',
        password='xxxxxx'
    )
    print('✅ Connected to PostgreSQL!')
    conn.close()
except Exception as e:
    print(f'❌ Error: {e}')
