def generate_config(context):
    """
    Create a type provider from a Google discovery document and ensure credentials are passed upon
    invoking REST methods from the document.
    """
    name_prefix = '{deployment}-{name}'.format(
        deployment=context.env['deployment'],
        name=context.env['name']
    )
    cluster_name = name_prefix
    type_name = '{name_prefix}-type'.format(name_prefix=name_prefix)

    resources = [
        {
            'name': cluster_name,
            'type': 'container.v1.cluster',
            'properties': {
                'zone': context.properties['zone'],
                'cluster': {
                    'name': cluster_name,
                    'initialNodeCount': context.properties['initialNodeCount'],
                    'nodeConfig': {
                        'oauthScopes': [
                            'https://www.googleapis.com/auth/{role}'.format(role=role) for role in [
                                'compute',
                                'devstorage.read_only',
                                'pubsub',
                                'logging.write',
                                'trace.append',
                                'monitoring'
                            ]
                        ]
                    }
                }
            }
        }
    ]

    properties = {
        'descriptorUrl': 'https://$(ref.{cluster_name}.endpoint)/openapi/v2'.format(cluster_name=cluster_name),
        'options': {
            'validationOptions': {
                'schemaValidation': 'FAIL'
            },
            'inputMappings': [
                {
                    'fieldName': 'name',
                    'location': 'PATH',
                    'methodMatch': '^(GET|DELETE|PUT|PATCH|POST)$',
                    'value': '$.resource.properties.metadata.name'
                },
                {
                    'fieldName': 'namespace',
                    'location': 'PATH',
                    'methodMatch': '^(GET|DELETE|PUT|PATCH|POST)$',
                    'value': '$.resource.properties.metadata.namespace'
                },
                {
                    'fieldName': 'metadata.resourceVersion',
                    'location': 'BODY',
                    'methodMatch': '^(PUT|PATCH)$',
                    'value': '$.resource.self.metadata.resourceVersion'
                },
                {
                    'fieldName': 'Authorization',
                    'location': 'HEADER',
                    'value': '$.concat("Bearer ", $.googleOauth2AccessToken())'
                }
            ]
        },
        'collectionOverrides': [
            {
                'collection': '/api/v1/namespaces/{namespace}/services/{name}',
                'options': {
                    'inputMappings': [
                        {
                            'fieldName': 'spec.clusterIP',
                            'location': 'BODY',
                            'methodMatch': '^(PUT|PATCH)$',
                            'value': '$.resource.self.spec.clusterIP'
                        }
                    ]
                }
            }
        ]
    }

    resources.append({
        'name': type_name,
        'type': 'deploymentmanager.v2beta.typeProvider',
        'properties': properties
    })

    outputs = [
        {
            'name': 'clusterType',
            'value': type_name
        }
    ]

    return {
        'resources': resources,
        'outputs': outputs
    }
