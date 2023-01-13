import xml.etree.ElementTree as ET
import os


class AckXML:
    @staticmethod
    def read(caminho: str, arquivo: str) -> tuple:
        tree = ET.parse(os.path.join(caminho, arquivo))
        root = tree.getroot()
        return root[0].text, root[1].text
