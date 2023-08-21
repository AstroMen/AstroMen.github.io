import app_data_pb2


class AppDataSerializer:
    def __init__(self):
        self.data_proto = app_data_pb2.AppData()

    def serialize(self, data_dict):
        self.data_proto.app_name = data_dict.get('App Name', '')
        self.data_proto.download_count = data_dict.get('Download Count', '')
        self.data_proto.app_description = data_dict.get('App Description', '')
        # ... Fill other fields ...
        return self.data_proto.SerializeToString()

    def deserialize(self, serialized_data):
        self.data_proto.ParseFromString(serialized_data)
        # Convert the protobuf message to a Python dict for easier access
        data_dict = {
            'App Name': self.data_proto.app_name,
            'Download Count': self.data_proto.download_count,
            'App Description': self.data_proto.app_description,
            # ... Extract other fields ...
        }
        return data_dict


'''
serializer = AppDataSerializer()

# Serializing
data = {...}  # your scraped data
serialized_data = serializer.serialize(data)

# Deserializing
received_data = serializer.deserialize(serialized_data)
'''