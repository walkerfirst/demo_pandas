'''
清洗chemiclas.db数据库中的suppliers表,将重复的name筛选出来存放入excel,并建议合适的替代
'''

import sqlite3,re
import pandas as pd
from collections import defaultdict
from config import conn
# 连接数据库

cursor = conn.cursor()

# 查询所有 name 字段
cursor.execute("SELECT id, name FROM suppliers WHERE name IS NOT NULL")
rows = cursor.fetchall()

# 根据前四个字符分组
groups = defaultdict(list)
for row_id, name in rows:
    prefix = name[:4]
    groups[prefix].append({'id': row_id, 'name': name, 'prefix': prefix})

result_rows = []
for prefix, items in groups.items():
    if len(items) <= 1:
        continue

    for item in items:
        name = item['name']
        excluded = (name.strip() != name) or ('\u2002' in name) or ('&#8194;' in name) or ('，' in name) or  (re.search(r'\d', name) is not None)
        item['excluded'] = excluded

    clean_items = [item for item in items if not item['excluded']]
    if not clean_items:
        continue

    new_item = max(clean_items, key=lambda x: len(x['name']))
    new_name = new_item['name']
    new_id = new_item['id']

    for item in items:
        item['new'] = new_name
        item['new_id'] = new_id
        result_rows.append(item)

df = pd.DataFrame(result_rows)
output_file = 'duplicate_suppliers_with_exclusion.xlsx'
df.to_excel(output_file, index=False)

print(f"保存成功：{output_file}")
conn.close()