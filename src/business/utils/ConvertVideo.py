import subprocess
import os


class ConvertVideo:
    @staticmethod
    def get_duration(video_file: str) -> str:
        convert_file = 'ffmpeg.exe'

        if not os.path.isfile(convert_file):
            raise FileNotFoundError(f"Falha ao encontrar executável {convert_file}")

        command = ['ffmpeg', '-i', video_file]
        ffmpeg = subprocess.Popen(command, shell=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
        result = ffmpeg.communicate()
        str_result = result[1].decode("utf-8")
        position = str_result.find("Duration")
        return str_result[position+10:position+21]
