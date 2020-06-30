def generate_config(context):
    """
    Create a type provider from a Google discovery document and ensure credentials are passed upon
    invoking REST methods from the document.
    """
    resources = []

    properties = {
        'descriptorUrl': context.properties['descriptorUrl'],
        'options': {
            'inputMappings': [
                {
                    'fieldName': 'Authorization',
                    'location': 'HEADER',
                    'value': '$.concat("Bearer ", $.googleOauth2AccessToken())'
                }
            ]
        }
    }

    resources.append({
        'name': context.properties['typeProviderName'],
        'type': 'deploymentmanager.v2beta.typeProvider',
        'properties': properties
    })

    return {
        'resources': resources
    }
