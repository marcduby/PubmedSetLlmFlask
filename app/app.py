# imports
from flask import Flask, render_template, request, flash
import sql_utils 
import ml_utils
import web_utils

app = Flask(__name__)
app.secret_key = "test_pubm_gpt"

@app.route("/genes")
def index():
    return render_template("index.html")


@app.route("/pmid_json", methods=["POST","GET"])
def submit_genes():
    # initialize 
    list_pubmed = []
    map_result = {}
    input_pubmed = None 
    list_errors = []
    input_subject = None
    input_object = None
    result_llm = None
    name_subject = None
    name_object = None 
    debug = True
    map_abstracts = {}

    if request.method == 'GET':
        input_pubmed = str(request.args.get("pmid"))
        if request.args.get("subject"):
            input_subject = request.args.get("subject")
        if request.args.get("object"):
            input_object = request.args.get("object")
    # log
    print("got request: {} with pmid inputs: {}, subject: {}, object: {}".format(request.method, input_pubmed, input_subject, input_object))

    # convert pubmed input to list
    if input_pubmed:
        list_temp = input_pubmed.split(",")

        for value in list_temp:
            pmid = value.strip()
            print("got pmid: -{}-".format(pmid))
            list_pubmed.append(pmid)
        
    # check for input errors
    if not input_subject:
        list_errors.append("no subject specified")
    if not input_object:
        list_errors.append("no object specified")

    # if subject, object and pmids, then process
    if input_subject and input_object and len(list_pubmed) > 0:
        # get subject and object names
        name_subject = web_utils.get_rest_name_for_curie(curie=input_subject, log=debug)
        name_object = web_utils.get_rest_name_for_curie(curie=input_object, log=debug)

        # retrieve the pmid abstracts
        conn = sql_utils.get_connection()
        # list_abstracts = get_list_abstracts(conn=conn, list_genes=list_select, log=True)
        map_abstracts = sql_utils.get_map_abstracts(conn=conn, list_pubmed=list_pubmed, log=True)

        # call the LLM
        list_abstracts = []
        for value in map_abstracts.values():
            print(value)
            list_abstracts.append(value.get('abstract'))
        result_llm = ml_utils.call_abstract_llm_recurisve(prompt_template=ml_utils.PROMPT_PUBMED, str_subject=name_subject, str_object=name_object,
                                                          list_abstracts=list_abstracts, log=True)

        # add result

    # build result
    map_result['input_pmid'] = list_pubmed
    map_result['input_subject'] = {input_subject: name_subject}
    map_result['input_object'] = {input_object: name_object}
    map_result['errors'] = list_errors
    map_result['result_llm'] = result_llm

    # add abstracts if debug
    if debug:
        map_result['abstracts'] = list(map_abstracts.values())

    # return
    return map_result



    # list_genes = []
    # list_genes_missing = []
    # list_temp = []
    # list_abstracts = []
    # abstract_gpt = "no abstract"
    # prompt_gpt = "no prompt"
    # list_gene_llm = []
    # list_abstract_llm = []
    # biology_abstract = ""
    # pathway_abstract = ""
    # input_genes = ""
    # map_abstracts = {}

    # # get the input
    # if request.method == 'POST':
    #     input_genes = str(request.form["input_gene_set"])
  
    # else:
    #     if request.args.get('input_gene_set'):
    #         input_genes = str(request.args.get('input_gene_set'))

    # print("got request: {} with inputs: {}".format(request.method, input_genes))


    # # split the genes into list
    # if input_genes:
    #     list_temp = input_genes.split(",")
    #     list_select = []

    #     for value in list_temp:
    #         gene = value.strip()
    #         print("got gene: -{}-".format(gene))
    #         list_select.append(gene)

    #     # get the data
    #     conn = get_connection()
    #     # list_abstracts = get_list_abstracts(conn=conn, list_genes=list_select, log=True)
    #     map_gene_abstracts = get_map_gene_abstracts(conn=conn, list_genes=list_select, log=True)

    #     if map_gene_abstracts and len(map_gene_abstracts) > 0:
    #         # build the prompt inputs
    #         str_gene = ",".join(map_gene_abstracts.keys())
    #         # str_abstract = "\n".join(list_abstract_llm)

    #         print("found summaries for genes: {}".format(str_gene))
    #         # print("\ngot abstracts: {}".format(str_abstract))

    #         # call the LLM
    #         # biology_abstract = ml_utils.call_llm(prompt_template=ml_utils.PROMPT_BIOLOGY, str_gene=str_gene, str_abstract=str_abstract, log=True)
    #         biology_abstract = ml_utils.call_gene_abstract_llm_recurisve(prompt_template=ml_utils.PROMPT_BIOLOGY, map_gene_abstracts=map_gene_abstracts, max_tokens=2500, log=True)
    #         print("\n\ngot biology LLM result: \n{}".format(biology_abstract))

    #         list_gene_llm = list(map_gene_abstracts.keys())
    #         # # call the LLM
    #         # pathway_abstract = ml_utils.call_llm(prompt_template=ml_utils.PROMPT_PATHWAYS, str_gene=str_gene, str_abstract=str_abstract, log=True)
    #         # print("\n\ngot biology LLM result: \n{}".format(biology_abstract))

    # else:
    #     print("no input genes")

    # # add data for return 
    # flash(list_select, 'list_genes_input')
    # flash(list_gene_llm, 'list_genes_used')
    # flash(biology_abstract, 'abstract_biology')
    # flash(pathway_abstract, 'abstract_pathway')
    # # flash(list_genes_missing, 'list_missing')
    # # flash(prompt_gpt, 'prompt')
    # # flash(abstract_gpt, 'abstract')

    # return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8083)
