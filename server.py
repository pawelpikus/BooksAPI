import flask
from flask import render_template, jsonify, request
import sqlite3
from sqlite3 import Error

app = flask.Flask(__name__)
app.config["DEBUG"] = True


def create_connection(db_file):
    """ create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn):
    """ create a table books
        :param conn: Connection object
        :return:
    """
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS books
                    (id integer PRIMARY KEY , 
                    title text NOT NULL, 
                    author text NOT NULL, 
                    first_sentence text NOT NULL,
                    year_published integer );''')

    except Error as e:
        print(e)


def insert_row(conn, book):
    """
        Create a new book
        :param conn:
        :param book:
        :return:
    """
    sql = '''INSERT OR IGNORE INTO books(id, title, author, first_sentence, year_published)
            VALUES(?,?,?,?,?)'''

    cur = conn.cursor()
    cur.execute(sql, book)


def dict_factory(cursor, row):
    """return items from the database as dictionaries rather than lists—
    these work better when we output them to JSON
    :param: cursor
    :param: row
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def db_main():
    database = './books.db'
    conn = create_connection(database)
    if conn is not None:
        create_table(conn)
    else:
        print('Error! Cannot create the database connection.')

    with conn:
        book1 = (0, 'A Fire Upon the Deep', 'Vernor Vinge', 'The coldsleep itself was dreamless.',
                '1992')
        book2 = (1, 'The Ones Who Walk Away From Omelas', 'Ursula K. Le Guin',
                 'With a clamor of bells that set the swallows soaring, the Festival',
                 '1973')
        book3 = (2, 'Dhalgren', 'Samuel R. Delany', 'to wound the autumnal city.', '1975')
        insert_row(conn, book1)
        insert_row(conn, book2)
        insert_row(conn, book3)


# routing
@app.route("/")
def home():
    return render_template('home.html')


@app.route("/api/v1/books/all", methods=["GET"])
def api_all():
    conn = create_connection('books.db')
    conn.row_factory = dict_factory
    c = conn.cursor()
    all_books = c.execute('SELECT * FROM books;').fetchall()
    return jsonify(all_books)


@app.route("/api/v1/books", methods=["GET"])
def api_filter():
    query_params = request.args
    id = query_params.get('id')
    published = query_params.get('published')
    author = query_params.get('author')

    query = 'SELECT * FROM books WHERE'
    to_filter = []

    if id:
        query += ' id=? AND'
        to_filter.append(id)
    if published:
        query += ' published=? AND'
        to_filter.append(published)
    if author:
        query += ' author=? AND'
        to_filter.append(author)

    if not (id or published or author):
        return page_not_found(404)

    query = query[:-4] + ';'

    conn = create_connection('books.db')
    conn.row_factory = dict_factory
    c = conn.cursor()
    results = c.execute(query, to_filter).fetchall()

    return jsonify(results)


@app.errorhandler(404)
def page_not_found(e):
    return '<h1>404</h1><p>Page not found.</p>', 404


if __name__ == "__main__":
    db_main()
    app.run()
