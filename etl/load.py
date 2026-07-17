from database.repository import save_dataframe

def load(df, session):
    save_dataframe(df, session)
    print("Database berhasil diperbarui")