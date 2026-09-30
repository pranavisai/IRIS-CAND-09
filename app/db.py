import psycopg

def get_connection(settings):
    return psycopg.connect(settings.database_url)