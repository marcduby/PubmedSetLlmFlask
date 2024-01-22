
# imports
import pymysql as mdb
import os
import logging
import sys

# constants 
SCHEMA_GPT = "web_gpt"
DB_PASSWD = os.environ.get('DB_PASSWD')

# logging
logging.basicConfig(level=logging.INFO, format=f'[%(asctime)s] - %(levelname)s - %(name)s : %(message)s')
handler = logging.StreamHandler(sys.stdout)
logger = logging.getLogger(__name__)

# queries
SQL_SELECT_GENES = """
select gene_code, abstract, pubmed_count from gene_abstract where gene_code in ({}) order by pubmed_count desc
"""

# methods 
# methods
def get_connection(schema=SCHEMA_GPT):
    ''' 
    get the db connection 
    '''
    conn = mdb.connect(host='localhost', user='root', password=DB_PASSWD, charset='utf8', db=schema)

    # return
    return conn


def get_list_abstracts(conn, list_genes, num_abstracts=350, log=False):
    '''
    get a list of abstract map objects based on the gene inputs
    '''
    # initialize
    list_abstracts = []
    cursor = conn.cursor()

    # pick the sql based on level
    if log:
        print("searching for abstracts got input search: {}, limit: {}".format(list_genes, num_abstracts))

    # get the in sql section
    sql_in = get_gene_in_statement(list_input=list_genes, log=log)
    sql_select = SQL_SELECT_GENES.format(sql_in)

    # log
    if log:
        print("got sql: \n{}".format(sql_select))

    cursor.execute(sql_select, (list_genes))

    # query 
    db_result = cursor.fetchall()
    for row in db_result:
        gene = row[0]
        abstract = row[1]
        pubmed_count = row[1]
        list_abstracts.append({"gene": gene, 'abstract': abstract, 'pubmed_count': pubmed_count})

    # log
    if log:
        print("got results: {}".format(list_abstracts))
        print("got row count of: {}".format(len(list_abstracts)))
        
    # return
    return list_abstracts

def get_map_gene_abstracts(conn, list_genes, num_abstracts=350, log=False):
    '''
    get a list of abstract map objects based on the gene inputs
    '''
    # initialize
    map_gene_abstracts = {}
    cursor = conn.cursor()

    # pick the sql based on level
    if log:
        print("searching for abstracts got input search: {}, limit: {}".format(list_genes, num_abstracts))

    # get the in sql section
    sql_in = get_gene_in_statement(list_input=list_genes, log=log)
    sql_select = SQL_SELECT_GENES.format(sql_in)

    # log
    if log:
        print("got sql: \n{}".format(sql_select))

    cursor.execute(sql_select, (list_genes))

    # query 
    db_result = cursor.fetchall()
    for row in db_result:
        gene = row[0]
        abstract = row[1]
        pubmed_count = row[1]
        map_gene_abstracts[gene] = abstract

    # log
    if log:
        print("got results for genes: {}".format(map_gene_abstracts.keys()))
        
    # return
    return map_gene_abstracts

def get_gene_in_statement(list_input, log=False):
    ''' builds the sql in statement '''
    in_sql = None

    # build the sql
    in_sql = ", ".join(list(map(lambda item: '%s', list_input)))

    if log:
        logger.info("got sql '{}'".format(in_sql))

    # return
    return in_sql





