from ..mqtt.MqttConfig import MqttConfig
from .Output import Output
import json

class ConfigParser:
    wifi_config: str
    mqtt_config: MqttConfig
    output_config: list[Output]
    def load(self, path_to_file):
        with open(path_to_file, "r") as stream:
            config = json.loads(stream.read())
            self.wifi_config = config['pi']
            self.mqtt_config = MqttConfig(**config['mqtt'])
            if config['digital_outputs']:
                self.output_config = [
                    Output(
                        x['name'],
                        x['pin'],
                        x['on_payload'],
                        x['off_payload']
                    ) for x in config['digital_outputs']]
            else:
                print("No digital outputs")
            try:
                print(config)
            except json.JSONDecodeError as exc:
                print(exc)
