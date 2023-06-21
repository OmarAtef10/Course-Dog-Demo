from django.apps import AppConfig
from globals import set_count, get_count

class StartConfig(AppConfig):
    def ready(self) -> None:
        set_count(41)
        print("Set vars correctly")
        