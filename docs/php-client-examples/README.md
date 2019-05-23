# Examples using a PHP Client

API Gateway uses standard HTTP requests. The only additional step needed is that all requests must be signed with the required authentication header.

The AWS SDK provides a method that will take any `Psr\Http\Message\RequestInterface`, plus a credentials provider, and decorate the request with the required headers.

There are 3 common ways to provide credentials:
* Using the default provider. In production, this should typically means that the instance/task's role would be used.
* Assuming a role. If the role attached to the instance/task cannot be used directly, you can assume a role that's contained within the Gateway's account.
* You can manually supply an AWS key and secret. This is not recommended.
