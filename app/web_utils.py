
# imports
import requests

# constants


# methods
def get_rest_name_for_curie(curie, log=False):
    '''
    get the normalized name for the curie
    '''
    # initialize
    result_name = None
    URL = "https://nodenormalization-sri.renci.org/get_normalized_nodes?curie={}"

    # request
    url = URL.format(curie)

    if log:
        print("querying url: {}".format(url))

    response = requests.get(url)
    json_result = response.json()

    # get the name
    if json_result.get(curie):
        if json_result.get(curie).get('id'):
            if json_result.get(curie).get('id').get('label'):
                result_name = json_result.get(curie).get('id').get('label')

    # return
    return result_name


if __name__ == "__main__":
    test_curie = 'MONDO:0020066'

    # get tbe name
    name = get_rest_name_for_curie(curie=test_curie, log=True)
    print("for curie: {}, got name: {}".format(test_curie, name))

