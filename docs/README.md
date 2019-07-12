# Overview

Services in OPG’s digital estate have traditionally been built as siloed systems, with limited automated interaction needed between them. As the estate has grown, and as we focus more on providing a digital first service, the need for services to communicate has emerged.

The OPG Sirius API Gateway demonstrates a pattern, and an implementation of that pattern, for OPG Services to communicate with each other via an API.

# The Pattern - aims

1 - The endpoint should expose data in its simplest form to the consuming service. I.e. the Gateway should tailor its endpoints and responses such that the consuming service needs to know as little as possible about Sirius. In this manner, the Gateway acts to a form of facade layer over Sirius; or could be viewed as a type of Frontend for Backend.

2 - Following on from above, the Gateway should decouple requests and responses from the internals of how Sirius handles those things. That is to say that the Gateway should provide a clear, versioned system boundary, with a contract, behind which Sirius should be free to refactor and evolve as needed.

3 - Access to Gateway endpoints needs to be authenticated, and specified requests authorised. In this we followed the Secure Systems of Secure Zones principle, thus we make no reliance on network controls for security between services. Instead all requests must be individually signed. The Gateway is then responsible for authenticating the request based on its signature, and ensure the calling service is authorised to access the specified endpoint called.

4 - The Gateway pattern fits into the larger scope of work of decomposing Sirius into smaller parts. The Gateway itself can be viewed as a Microservice, representing a back-end for front-end integration pattern. Clear boundaries should be maintained between the Gateway and other Sirius services. The Gateway should retain complete autonomy over its own data, the cache.

# The Implementation 

1 - The exposed endpoints of the API are built using AWS’ API Gateway. This provides:
* IAM based authentication and authorisation. Specifically role base, removing the need for stored credentials on consuming services.
* Support for connection throttling out of the box.
* High availability.
* Minimal infrastructure management.

2 - The API Gateway invokes a lambda to handle the request. This allows for:
* The request to be executed within Sirius’ VPC.
* Complete freedom to define the needed interactions required with Sirius’ internal components.
* Further to the above, a clear location where changes should be made to retain compatibility with Sirius as it changes.

3 - The Gateway includes a caching layer, using DynamoDB. This allows for:
* Continued access to this cache in the event other Sirius components become unavailable.
* Leading to an overall higher availability. 


# Lambda

For Lambda docs, see [here](../lambdas/docs).
