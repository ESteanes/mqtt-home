from umqtt.simple import MQTTClient
from .homeassistantdiscovery import HomeAssistantDiscoveryBuilder
from .homeassistantdiscoverydevice import HomeAssistantDiscoveryDevice
from main.configparsing.output import Output
from main.configparsing.configparser import ConfigParser
from main.configparsing.homeassistantdiscoveryconfig import HomeAssistantDiscoveryConfig


class HomeAssistantMqttClient:
    topic_prefix: str
    outputs: list[Output]
    ha_discovery: HomeAssistantDiscoveryConfig
    location: str
    UUID: str
    mqtt_client: MQTTClient
    
    def __init__(self, UUID: str, parsedConfig: ConfigParser):
        if UUID:
            self.UUID = UUID
        else:
            self.UUID = "testUUID"
        self.topic_prefix = parsedConfig.mqtt_config.topic_prefix
        self.outputs = parsedConfig.output_config
        self.ha_discovery = parsedConfig.mqtt_config.ha_discovery
        self.location = parsedConfig.mqtt_config.location
        self.haDiscoveryPayloads = None
        self.haDiscoveryTopics = None
        self.mqtt_client = MQTTClient(
            client_id=self.UUID,
            server=parsedConfig.mqtt_config.host,
            user=parsedConfig.mqtt_config.user,
            password=parsedConfig.mqtt_config.password)
        if self.ha_discovery.enabled != None:
            self.initHaDiscovery()

    def initHaDiscoveryTopics(self):
        self.haDiscoveryTopics = [self.ha_discovery.discovery_topic_prefix + self.UUID+"/"+output.name+"/config" for output in self.outputs]

    def initHaDiscoveryPayloads(self):
        outputNames = [output.name for output in self.outputs]
        print("list comprehension test: " + "".join(outputNames))
        self.haDiscoveryPayloads = [
            HomeAssistantDiscoveryBuilder()\
            .set_name(output.name)\
            .set_availability_topic(self.topic_prefix + "/status")\
            .set_device(
                HomeAssistantDiscoveryDevice(
                    "Home Assistant MQTT Client",
                    "v0",
                    ["Home Assistant MQTT Client", "Home Assistant MQTT Client-"+self.UUID],
                    "Home Assistant MQTT Client")
                )\
            .set_unique_id(self.UUID)\
               .set_state_topic(self.location+"/output/"+output.name)\
            .set_command_topic(self.location+"/output/"+output.name+"/set")\
            .set_payload_on(output.on_payload)\
            .set_payload_off(output.off_payload)\
            .build().return_map() for output in self.outputs]

    def initHaDiscovery(self):
        self.initHaDiscoveryPayloads()
        self.initHaDiscoveryTopics()
    
    def mqttStatus(self, isAvailable):
        for haDiscovery in self.haDiscoveryPayloads:
            if isAvailable:
                self.publish(
                    haDiscovery["availability_topic"], haDiscovery["payload_available"])
                continue
            self.publish(haDiscovery["availability_topic"], haDiscovery["payload_not_available"])

    def mqttHADiscoveryPost(self):
        for haDiscovery in self.haDiscoveryPayloads:
            self.publish(haDiscovery["availability_topic"],haDiscovery)

    def mqttInitialise(self, isAvailable):
        self.mqtt_client.connect()
        self.mqttStatus(isAvailable)
        
    
    def publish(self, topic: str, payload: any) -> None:
        self.mqtt_client.publish(topic, payload)