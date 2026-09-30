import psycopg

# Create a database connection from the app's validated settings.
def get_connection(settings):
    return psycopg.connect(settings.database_url)