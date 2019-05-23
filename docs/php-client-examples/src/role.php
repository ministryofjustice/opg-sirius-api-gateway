<?php
include_once '../vendor/autoload.php';

use Aws\Credentials\CredentialProvider;
use GuzzleHttp\Client;
use GuzzleHttp\Psr7\Request;
use Aws\Signature\SignatureV4;
use Aws\Sts\StsClient;


$assumeRoleCredentials = CredentialProvider::assumeRole([
    'client' => new StsClient([
        'region' => 'eu-west-1',
        'version' => '2011-06-15'
    ]),
    'assume_role_params' => [
        'RoleArn' => 'arn:aws:iam::948424592557:role/api-gateway-access',
        'RoleSessionName' => 'test_session',
    ]
]);


$s4 = new SignatureV4('execute-api', 'eu-west-1');


$request = new Request('GET', 'https://api.dev.sirius.opg.digital/v1/lpa-online-tool/lpas/A15423875412');


$signed_request = $s4->signRequest($request, $assumeRoleCredentials()->wait());


try {

    $response = (new Client)->send($signed_request);
    echo $response->getBody()."\n\n";

} catch (\GuzzleHttp\Exception\ClientException $e) {
    echo $e->getResponse()->getBody()."\n";
} catch (\Exception $e) {
    echo $e->getMessage();
} catch (\TypeError $e) {
    echo $e->getMessage();
}
