def GenerateConfig(context):
  """Generate YAML resource configuration."""

  cluster_types_root = ''.join([
      context.env['project'],
      '/',
      context.properties['clusterType']
      ])
  cluster_types = {
      'Service': ''.join([
          cluster_types_root,
          ':',
          '/api/v1/namespaces/{namespace}/services/{name}'
          ]),
      'Deployment': ''.join([
          cluster_types_root,
          ':',
          '/apis/apps/v1/namespaces/{namespace}/deployments/{name}'
          ])
  }

  name_prefix = context.env['deployment'] + '-' + context.env['name']
  port = context.properties['port']

  resources = [{
      'name': name_prefix + '-service',
      'type': cluster_types['Service'],
      'properties': {
          'apiVersion': 'v1',
          'kind': 'Service',
          'namespace': 'default',
          'metadata': {
              'name': name_prefix + '-service',
              'labels': {
                  'id': 'deployment-manager'
              }
          },
          'spec': {
              'type': 'NodePort',
              'ports': [{
                  'port': port,
                  'targetPort': port,
                  'protocol': 'TCP'
              }],
              'selector': {
                  'app': name_prefix
              }
          }
      }
  }, {
      'name': name_prefix + '-deployment',
      'type': cluster_types['Deployment'],
      'properties': {
          'apiVersion': 'apps/v1',
          'kind': 'Deployment',
          'namespace': 'default',
          'metadata': {
              'name': name_prefix + '-deployment'
          },
          'spec': {
              'replicas': 1,
              'selector': {
                  'matchLabels': {
                      'app': name_prefix
                  }
              },
              'template': {
                  'metadata': {
                    'name': name_prefix + '-deployment',
                    'labels': {
                        'app': name_prefix
                    }
                  },
                  'spec': {
                      'containers': [{
                          'name': 'container',
                          'image': context.properties['image'],
                          'env': [
                              {
                                  'name': 'GS_BUCKET',
                                  'value': context.properties['bucket']
                              },
                              {
                                  'name': 'BADGES_TOPIC',
                                  'value': context.properties['topic']
                              }
                          ]
                      }]
                  }
              }
          }
      }
  }]

  return {'resources': resources}