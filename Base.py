# Mod Base py
# Description: Every mod need to INHERIT this py to be its inherent property
# LunareZ @A_xie_A
# => Copyright Apathy 3.0 <=
from flet import Page, Control
from abc import ABC, abstractmethod


# Base Class with abstract function to get mod's property
class Base(ABC):
    @property
    @abstractmethod
    def id(self) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def icon(self) -> str:
        pass

    @abstractmethod
    def build(self, page: Page) -> Control:
        pass

    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def destroy(self):
        pass

