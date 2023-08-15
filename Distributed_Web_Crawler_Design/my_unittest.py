import unittest
from unittest.mock import patch, Mock

class TestURLFetcher(unittest.TestCase):

    @patch("requests.get")
    def test_fetch(self, mock_get):
        mock_get.return_value = Mock(status_code=200, text="sample text")
        fetcher = URLFetcher(["test-agent"])
        data, new_urls = fetcher.fetch("http://example.com")
        self.assertTrue(data)
        self.assertTrue(new_urls)

class TestDataProcessor(unittest.TestCase):

    @patch.object(KafkaProducer, 'send')
    def test_send_urls_to_kafka(self, mock_send):
        kafka_config = {
            'bootstrap_servers': 'localhost:9092',
            'topic_name': 'test_topic'
        }
        cassandra_config = {}
        fetcher = URLFetcher(["test-agent"])
        processor = DataProcessor(kafka_config, cassandra_config, fetcher)

        urls = ["http://example1.com", "http://example2.com"]
        processor.send_urls_to_kafka(urls)
        self.assertEqual(mock_send.call_count, 2)

if __name__ == '__main__':
    unittest.main()
