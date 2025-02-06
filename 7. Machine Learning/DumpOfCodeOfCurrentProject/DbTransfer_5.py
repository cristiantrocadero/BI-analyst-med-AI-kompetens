# Description: This script is responsible for transferring the processed data 
# from MLModelReturns_4 to the MySQL database.

import MLModelReturns_4
import mysql.connector

def db_connection():
    """
    Establishes a connection to the MySQL database.
    Returns:
        connection: MySQL database connection object.
    """
    try:
        cnxn = mysql.connector.connect(
            host="localhost",  # Hostname
            user="root",       # Username
            password="dinmamma",  # Password
            database="ArtiklarDB"  # Database name
        )
        print("Connected to the database.")
        return cnxn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def article_exists(link, cnxn):
    """
    Checks if an article already exists in the database using its link.
    Args:
        link (str): The article link to check.
        cnxn: MySQL database connection object.
    Returns:
        bool: True if the article exists, False otherwise.
    """
    cursor = cnxn.cursor()
    query = "SELECT COUNT(*) FROM news WHERE link = %s"
    cursor.execute(query, (link,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] > 0

def insert_data(data, cnxn):
    """
    Inserts new articles into the 'news' table while avoiding duplicates.
    Args:
        data (list): List of dictionaries representing articles.
        cnxn: MySQL database connection object.
    """
    cursor = cnxn.cursor()
    insert_sql = """
    INSERT INTO news (
        title, summary, link, published, topic, politik, utbildning, religion,
        miljo, ekonomi, livsstilfritt, samhallekonflikter, halsa, idrott, vetenskapteknik
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    data_tuples = []
    for item in data:
        if not article_exists(item['link'], cnxn):  # Check if the article already exists
            categories = item['topic']
            topic_string = ",".join(categories)  # Convert the list to a comma-separated string
            data_tuples.append((
                item['title'], item['summary'], item['link'], item['published'], topic_string,
                1 if 'Politik' in categories else 0,
                1 if 'Utbildning' in categories else 0,
                1 if 'Religion' in categories else 0,
                1 if 'Miljo' in categories else 0,
                1 if 'Ekonomi' in categories else 0,
                1 if 'LivsstilFritt' in categories else 0,
                1 if 'SamhalleKonflikter' in categories else 0,
                1 if 'Halsa' in categories else 0,
                1 if 'Idrott' in categories else 0,
                1 if 'VetenskapTeknik' in categories else 0
            ))

    try:
        if data_tuples:  # Check if there are new articles to add
            cursor.executemany(insert_sql, data_tuples)
            cnxn.commit()
            print(f"{cursor.rowcount} new rows added to the database.")
        else:
            print("No new articles to add.")
    except mysql.connector.Error as err:
        print(f"Error inserting data: {err}")
    finally:
        cursor.close()

def main():
    """
    Main function to handle database operations.
    """
    MLModelReturns_4.main()  # Ensure MLModelReturns_4 is run first
    validDict = MLModelReturns_4.validDict  # Retrieve processed data from MLModelReturns_4

    print('-----Starting DbTransfer_5.py-----')
    # Connect to the database
    cnxn = db_connection()
    if cnxn:
        # Insert new data into the database
        insert_data(validDict, cnxn)
        cnxn.close()
        print("Database operations completed.")
    else:
        print("No database connection could be established.")

if __name__ == "__main__":
    main()
