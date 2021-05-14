from unittest import mock
import response_formatters
import copy

@mock.patch('data_providers.Response', autospec=True)
def test_format_lpa_collection_by_id_with_empty_response(response):
    """
    We expect the original response to be returned, amended to represent a 404 Not Found.

    :param response:
    :return:
    """
    response.is_empty.return_value = True

    code = mock.PropertyMock()
    payload = mock.PropertyMock()

    type(response).code = code
    type(response).payload = payload

    result = response_formatters.format_lpa_collection_by_id({
        'resource': '/lpa-online-tool',
    }, response)

    # We expect the original response to be returned
    assert result is response

    # With the follow two things set
    code.assert_called_once_with(404)
    payload.assert_called_once_with({})


@mock.patch('data_providers.Response', autospec=True)
def test_format_lpa_collection_by_id_with_only_results_expected_fields(response):
    response.is_empty.return_value = False

    test_data = {
        'should-not-be-returned-1': 'test',
        'onlineLpaId': 'test',
        'receiptDate': 'test',
        'registrationDate': 'test',
        'rejectedDate': 'test',
        'cancellationDate': 'test',
        'invalidDate': 'test',
        'withdrawnDate': 'test',
        'dispatchDate': 'test',
        'status': 'test',
        'should-not-be-returned-2': 'test',
    }

    test_case = copy.deepcopy(test_data)

    payload = mock.PropertyMock()
    type(response).payload = payload

    # We expect the payload to be wrapped in an array
    payload.return_value = [test_data]

    result = response_formatters.format_lpa_collection_by_id({
        'resource': '/lpa-online-tool',
    }, response)

    # Theses two items should have been removed
    del test_case['should-not-be-returned-1']
    del test_case['should-not-be-returned-2']

    assert result is response
    payload.assert_called_with(test_case)
    assert 2 == payload.call_count


@mock.patch('data_providers.Response', autospec=True)
def test_format_lpa_collection_by_id_with_sirius_uids(response):
    response.is_empty.return_value = False

    test_data = {
        'onlineLpaId': 'test',
        'receiptDate': 'test',
        'registrationDate': 'test',
        'rejectedDate': 'test',
        'cancellationDate': 'test',
        'invalidDate': 'test',
        'withdrawnDate': 'test',
        'dispatchDate': 'test',
        'status': 'test',
        'uId': '7000-8423-8541',
        'attorneys': [
            {
                'uId': '7000-8423-4136',
            }
        ],
        'donor': {
            'uId': '7000-8423-9674',
        }
    }

    test_case = copy.deepcopy(test_data)

    payload = mock.PropertyMock()
    type(response).payload = payload

    # We expect the payload to be wrapped in an array
    payload.return_value = [test_data]

    result = response_formatters.format_lpa_collection_by_id({
        'resource': '/use-an-lpa',
    }, response)

    # Amend test case to that's expected
    test_case['uId'] = '700084238541'
    test_case['donor']['uId'] = '700084239674'
    test_case['attorneys'][0]['uId'] = '700084234136'

    assert result is response
    payload.assert_called_with(test_case)
    assert 2 == payload.call_count
