import xml.etree.ElementTree as ET
import os


class VideoXML:
    @staticmethod
    def create(caminho: str, arquivo: str, dto: dict) -> None:
        root = ET.Element("video")

        arquivo_element = ET.SubElement(root, "codigo")
        arquivo_element.text = dto['codigo']

        arquivo_element = ET.SubElement(root, "arquivo")
        arquivo_element.text = dto['arquivo']

        titulo_element = ET.SubElement(root, "titulo")
        titulo_element.text = dto['titulo']

        grupo_element = ET.SubElement(root, "grupo")
        grupo_element.text = dto['grupo']

        operador_element = ET.SubElement(root, "operador")
        operador_element.text = dto['operador']

        markin_element = ET.SubElement(root, "markIn")
        markin_element.text = dto['markIn']

        markout_element = ET.SubElement(root, "markOut")
        markout_element.text = dto['markOut']

        remover_element = ET.SubElement(root, "remover")
        remover_element.text = dto['remover']

        tree = ET.ElementTree(root)
        tree.write(os.path.join(caminho, arquivo), encoding='iso-8859-1', xml_declaration=True)

    @staticmethod
    def read(caminho: str, arquivo: str) -> tuple:
        tree = ET.parse(os.path.join(caminho, arquivo))
        root = tree.getroot()
        return root[0].text, root[1].text, root[2].text, root[3].text, \
               root[4].text, root[5].text, root[6].text, root[7].text
