from database.repository import save_dataframe


def load(df):

    save_dataframe(df)
    print("Database berhasil diperbarui")