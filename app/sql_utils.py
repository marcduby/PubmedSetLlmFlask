
# imports
import pymysql as mdb
import os
import logging
import sys

# constants 
SCHEMA_GPT = "pubmed_gen"
DB_USER = os.environ.get('DB_USER')
DB_PASSWD = os.environ.get('DB_PASSWD')

# logging
logging.basicConfig(level=logging.INFO, format=f'[%(asctime)s] - %(levelname)s - %(name)s : %(message)s')
handler = logging.StreamHandler(sys.stdout)
logger = logging.getLogger(__name__)

# queries
SQL_SELECT_ABSTRACTS = """
select pubmed_id, abstract, count_reference from pubm_paper_abstract where pubmed_id in ({}) order by count_reference desc limit 20
"""

# methods 
# methods
def get_connection(schema=SCHEMA_GPT):
    ''' 
    get the db connection 
    '''
    conn = mdb.connect(host='localhost', user=DB_USER, password=DB_PASSWD, charset='utf8', db=schema)

    # return
    return conn


def get_map_abstracts(conn, list_pubmed, num_abstracts=350, log=False):
    '''
    get a list of abstract map objects based on the gene inputs
    '''
    # initialize
    map_abstracts = {}
    cursor = conn.cursor()

    # pick the sql based on level
    if log:
        print("searching for abstracts got input search: {}, limit: {}".format(list_pubmed, num_abstracts))

    # get the in sql section
    sql_in = get_sql_in_statement(list_input=list_pubmed, log=log)
    sql_select = SQL_SELECT_ABSTRACTS.format(sql_in)

    # log
    if log:
        print("got sql: \n{}".format(sql_select))

    cursor.execute(sql_select, (list_pubmed))

    # query 
    db_result = cursor.fetchall()
    for row in db_result:
        pmid = row[0]
        abstract = row[1]
        pubmed_count = row[2]
        map_abstracts[pmid] = {"pmid": pmid, 'abstract': abstract, 'pubmed_count': pubmed_count}

    # log
    if log:
        print("got results: {}".format(list_pubmed))
        print("got row count of: {}".format(len(list_pubmed)))
        
    # return
    return map_abstracts


def get_sql_in_statement(list_input, log=False):
    ''' builds the sql in statement '''
    in_sql = None

    # build the sql
    in_sql = ", ".join(list(map(lambda item: '%s', list_input)))

    if log:
        logger.info("got sql '{}'".format(in_sql))

    # return
    return in_sql





