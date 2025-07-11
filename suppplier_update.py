
'''
更新chemicals.db的suppliers表,并删除重复
'''

import pandas as pd
from config import conn

def get_data_from_excel(EXCEL_PATH):
    # 读取 Excel
    df = pd.read_excel(EXCEL_PATH)
    
    if 'id' not in df.columns or 'new_id' not in df.columns:
        raise ValueError("Excel文件必须包含'id'和'new_id'列")
    return df

def export_pre_update_records(conn, df, table_name, output_path):
    """
    在更新前导出将被修改的记录，包括 old_id 和对应的 new_id
    """
    cursor = conn.cursor()
    records = []

    for _, row in df.iterrows():
        old_id = int(row['id'])
        new_id = int(row['new_id'])

        sql = f"""
            SELECT *, ? AS old_supplier_id, ? AS new_supplier_id
            FROM {table_name}
            WHERE supplier_id = ?
        """
        cursor.execute(sql, (old_id, new_id, old_id))
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]

        for r in rows:
            records.append(dict(zip(cols, r)))

    if records:
        df_out = pd.DataFrame(records)
        df_out.to_excel(output_path, index=False)
        print(f"{table_name} 变更前的记录已导出到 {output_path}")
    else:
        print(f"{table_name} 无需更新的记录")

    cursor.close()

def update_supplier_id(df, table_name):
    cursor = conn.cursor()
    try:
        for _, row in df.iterrows():
            old_id = int(row['id'])
            new_id = int(row['new_id'])

            sql = f"""
                UPDATE {table_name}
                SET supplier_id = ?
                WHERE supplier_id = ?
            """
            cursor.execute(sql, (new_id, old_id))

        conn.commit()
        print(f"{table_name} 表更新完成。")

    except Exception as e:
        conn.rollback()
        print(f"{table_name} 表更新出错，已回滚：", e)
        raise  # 可选：抛出异常以便上层处理
    except Exception as e:
        conn.rollback()
        print("出错，已回滚：", e)

    finally:
        conn.close()

def delete_supplier_by_id(df, export_path):
    """
    删除 suppliers 表中指定 id 的记录，并在删除前导出这些记录到 Excel
    """
    cursor = conn.cursor()
    try:
        ids_to_delete = tuple(df['id'].dropna().astype(int))
        if ids_to_delete:
            placeholder = ','.join(['?'] * len(ids_to_delete))

            # 🔸 删除前导出记录
            select_sql = f"SELECT * FROM suppliers WHERE id IN ({placeholder})"
            suppliers_to_delete = pd.read_sql_query(select_sql, conn, params=ids_to_delete)

            if not suppliers_to_delete.empty:
                suppliers_to_delete.to_excel(export_path, index=False)
                print(f"已导出待删除的 suppliers 记录到: {export_path}")
            else:
                print("未找到匹配的 suppliers 记录，无需导出。")

            # 🔸 执行删除
            cursor.execute(f"DELETE FROM suppliers WHERE id IN ({placeholder})", ids_to_delete)
            conn.commit()
            print("suppliers 表记录已删除。")

        else:
            print("没有有效的 id 可删除。")

    except Exception as e:
        conn.rollback()
        print("出错，已回滚：", e)

    finally:
        cursor.close()

if __name__ == '__main__':
    # Excel 文件路径
    EXCEL_PATH = './data/suppliers_to_be_delete-2.xlsx'
    df = get_data_from_excel(EXCEL_PATH)
    # print(df)
    table_name = "quots"
    output_path = f"./data/updated_records_{table_name}.xlsx"
    # export_pre_update_records(conn, df, table_name=table_name, output_path=output_path)
    # update_supplier_id(df=df,table_name=table_name)
    export_path='./data/suppliers_be_deleted-2.xlsx'
    delete_supplier_by_id(df=df,export_path=export_path)
