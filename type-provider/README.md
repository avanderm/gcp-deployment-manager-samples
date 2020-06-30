# Type Provider

## Context

Not all services provided by Google Cloud are available in Deployment Manager. However, all services do provide so-called "Discovery Documents", which describe the REST API to create/update/delete/... resources in a particular service. For example, the discovery document for the Cloud Run service is described [here](https://run.googleapis.com/$discovery/rest?version=v1). For the remainder of this document we will focus on Google discovery documents (i.e. related to a Google Cloud service) only, since there are also third party discovery documents for easy integration with Google.


Types in infrastructure as code ultimately resolve to REST API calls. Deployment manager types map one-to-one to REST resources. The lifespan of a type starts with the create (REST) method for a (REST) resource, during its lifespan(REST) methods may be invoked in order to update the (Deployment Manager) resource when properties need to change.Finally a delete (REST) method in case the resource is removed from the infrastructure as code template or if the deployment is deleted altogether.

## Comparison to AWS

In AWS it is the exception rather than the rule that AWS services are not available in CloudFormation. In the end, CloudFormation also is just an interface on top of REST APIs. While Deployment Manager is not as up to date, the [discovery documents](https://developers.google.com/discovery/v1/reference/apis/list) are.

## Deploy

When you create a type provider out of a Google discovery document on your project, Deployment Manager will need credentials for invoking the REST API. Deployment Manager will not do this out of the box, since discovery documents are not limited to Google services and may include third party type providers. It would not be wise to send credentials to untrusted providers.

### Manual

In order to tackle the credentials requirement, we will supply the following input options (YAML file) when we create the provider.

```yaml
options:
  inputMappings:
    - fieldName: Authorization
      location: HEADER
      value: '$.concat("Bearer ", $.googleOauth2AccessToken())'
```

Now the type provider (in this case we use the discovery document for [Cloud Run](https://cloud.google.com/run)) can be created as follows:

```bash
gcloud beta deployment-manager type-providers create [TYPE_PROVIDER] \
    --descriptor-url="https://run.googleapis.com/$discovery/rest?version=v1" \
    --api-options-file=./options.yaml
```

Check that the type provider is created:

```bash
gcloud beta deployment-manager type-providers describe [TYPE_PROVIDER] \
    --project [PROJECT_ID]
```

The resources provided by the type can be inspected using

```bash
gcloud beta deployment-manager types list \
    --provider [TYPE_PROVIDER] \
    --project [PROJECT_ID]
```

And all the properties for a specific type can be shown using

```bash
gcloud beta deployment-manager types describe [TYPE] \
    --provider [TYPE_PROVIDER]
```

To delete the type provider use

```bash
gcloud beta deployment-manager type-providers delete [TYPE_PROVIDER]
```

### Deployment Manager

A type provider can also be deployed using Deployment Manager after configuring `config.yaml`:

```bash
gcloud deployment-manager deployments create <deployment-name> --config config.yaml
```

You can run the same [commands](#manual) to list and describe the available types for your type provider.

## Failures

It is important to supply the authorization in the API options, since the Google discovery document describes a Google service. Without it, attempting to deploy types from the type provider will always inform you that there are missing credentials or Oauth2 tokens.

## References

- [Google Discovery Service](https://developers.google.com/discovery/v1/reference/apis/list)
- [Google Discovery APIs](https://www.googleapis.com/discovery/v1/apis)
- [Adding an API as a Type Provider](https://cloud.google.com/deployment-manager/docs/configuration/type-providers/creating-type-provider)
- [Advanced Configuration Options](https://cloud.google.com/deployment-manager/docs/configuration/type-providers/advanced-configuration-options)
- [Calling a Type Provider in a Configuration](https://cloud.google.com/deployment-manager/docs/configuration/type-providers/calling-type-provider)
- [Type Provider in Deployment Manager](https://binx.io/blog/2019/04/02/creating-type-providers-for-google-deployment-manager/)
- [GCP Goodies Part 1](https://blog.softwaremill.com/gcp-goodies-part-1-google-deployment-manager-basics-747ce637e61b): example of creating a type provider for Kubernetes clusters