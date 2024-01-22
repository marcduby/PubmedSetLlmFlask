
# imports
import os 
import openai
import json

# constants
KEY_CHATGPT = os.environ.get('CHAT_KEY')
openai.api_key = KEY_CHATGPT
MODEL_CHATGPT="gpt-3.5-turbo-0301"

# prompts
PROMPT_PUBMED= """
As a biology researcher, read through the below abstracts and using only those, describe the biological association between {} and {}
{}
"""

# PROMPT_THERAPEUTICS = """
# Below are the abstracts from different research papers on the genes {}. 
# Please read through the abstracts and as a genetics researcher write a 200 word summary that synthesizes the key findings on possible therapeutics for diseases linked to the genes {}
# {}
# """

# PROMPT_BIOLOGY = """
# Below are the biological research summaries on the genes {}. 
# Please read through the summaries and as a genetics researcher write a 300 word summary that synthesizes the key findings on the common biology of the genes {}
# {}
# """
# PROMPT_BIOLOGY = """
# Below are the abstracts from different research papers on the genes {}. 
# Please read through the abstracts and as a genetics researcher write a 200 word summary that synthesizes the key findings on the common biology of the genes {}
# {}
# """

# methods
def get_prompt(prompt_template, str_subject, str_object, str_abstract, log=False):
    '''
    build out the prompt
    '''
    # result = prompt.format({'genes': str_gene, 'abstracts': str_gene})
    result = prompt_template.format(str_subject, str_object, str_abstract)

    # log
    if log:
        print("got prompt: {}".format(result))

    # return
    return result

def call_llm(prompt_template, str_subject, str_object, str_abstract, log=False):
    '''
    call chat gpt 
    '''
    # initialize
    str_chat = ""

    # get the prompt
    str_prompt = get_prompt(prompt_template=prompt_template, str_subject=str_subject, str_object=str_object, str_abstract=str_abstract, log=log)

    # get the result
    str_chat = call_chatgpt(str_query=str_prompt, log=True)

    # log
    if log:
        print("for subject: {}, object: {} - got result: \n{}".format(str_subject, str_object, str_chat))

    # return
    return str_chat

def call_chatgpt(str_query, log=False):
    '''
    makes the api call to chat gpt service
    '''
    # initialize
    str_result = ""
    list_conversation = []

    # build the payload
    # list_conversation.append({'role': 'system', 'content': MODEL_PROMPT_SUMMARIZE.format(str_query)})
    list_conversation.append({'role': 'system', 'content': str_query})

    if log:
        print("using chat input: {}\n".format(json.dumps(list_conversation, indent=1)))

    # query
    response = openai.ChatCompletion.create(
        model = MODEL_CHATGPT,
        messages = list_conversation
    )

    # get the response
    str_response = response.choices
    # log
    if log:
        print("got chatGPT response: {}".format(str_response))

    # get the text response
    str_result = str_response[0].get('message').get('content')

    # return
    return str_result


def call_abstract_llm_recurisve(prompt_template, str_subject, str_object, list_abstracts, max_tokens=4000, to_shuffle=True, log=False):
    ''' 
    method to call llm recursively depending on token size
    logic:
    - split into manageable abstract strings (token length)
    - for each string, call the LLM
    - if there is only one LLM call, return result
    - if more than one string, do recursive call
    '''
    # initialize
    list_of_concatenated_abstracts = []
    list_llm_result = []

    # log
    if log:
        print("recursive {} token LLM call for suject: {}, object: {} and abstract list size: {}".format(max_tokens, str_subject, str_object, len(list_abstracts)))

    # shuffle list if needed

    # loop and build map entries
    count_tokens = 0
    list_temp_abstract = []
    for value_abstract in list_abstracts:
        # if less than max tokens, add abstract
        if count_tokens + len(value_abstract.split()) < max_tokens:
            list_temp_abstract.append(value_abstract)
            count_tokens = count_tokens + len(value_abstract.split())

            if log:
                print("Added to tokens length: {}".format(count_tokens))

        else:
            # add to to list of list
            list_of_concatenated_abstracts.append(get_delimited_string(list_items=list_temp_abstract, delimiter="\n"))

            # reinitialize
            count_tokens = len(value_abstract.split())
            list_temp_abstract = [value_abstract]

            if log:
                print("Reset tokens length to: {}".format(count_tokens))

    # add last entry to map
    if count_tokens > 0:
        list_of_concatenated_abstracts.append(get_delimited_string(list_items=list_temp_abstract, delimiter="\n"))

    # llm call and put result in map
    for value_abstract in list_of_concatenated_abstracts:
        result_llm_abstract = call_llm(prompt_template=prompt_template, str_subject=str_subject, str_object=str_object, str_abstract=value_abstract, log=log)
        # result_abstract = "gene set: {}\n".format(key_gene)
        list_llm_result.append(result_llm_abstract)

    # if map lenghth is 1, then return, or else recursive call with each element
    if len(list_llm_result) == 1:
        return list_llm_result
    
    else:
        return call_abstract_llm_recurisve(prompt_template=prompt_template, str_subject=str_subject, str_object=str_object, list_abstracts=list_llm_result, 
                                           max_tokens=max_tokens, to_shuffle=to_shuffle, log=log)
        

def get_delimited_string(list_items, delimiter=",", log=False):
    ''' 
    creates a comma delimited string from the given list
    '''
    return delimiter.join(list_items)



