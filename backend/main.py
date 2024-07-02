
from fastapi import FastAPI, File, UploadFile
import speech_recognition as sr
from pydub import AudioSegment
import os


app = FastAPI()   #приложение, являющееся экземпляром класса FastAPI


@app.post('/recognize')                                                                       #декоратор для обработки POST-запроса по адресу
async def recognize_audio(file: UploadFile = File(...)) -> dict:                              #данная аннотация говорит о том, что мы работаем с загружаемым файлом
    """
    Данная функция получает на вход аудиофайл, который пробует распознать, и возвращает текстовое представление аудиофайла.

    Args:
        file (UploadFile): Входной файл является загружаемым.
    Return:
        text (Dict): Возвращаем текстовую информацию в виде словаря.
    """
    file_location = f'temp_{file.filename}'                                                   #создаём временное имя для файла
    with open(file_location, 'wb') as file_object:                                            #открываем файл для записи в бинарном режиме
        file_object.write(file.file.read())                                                   #записываем содержимое полученного файла
    file_extension = file.filename.split('.')[-1].lower()                                     #получаем формат файла
    try:                                                                                      #блок для отлова возможных ошибок
        if file_extension != 'wav':                                                           #если формат не .wav
            audio = AudioSegment.from_file(file_location, format=file_extension)              #загружаем аудиофайл с указанием его формата
            audio = audio.set_channels(1).set_frame_rate(16000)                               #преобразуем аудио в моно (1 канал) и устанавливаем частоту дискретизации 16000 герц (необходимо для улучшения качества распознавания речи)
            temp_wav_path = 'temp.wav'                                                        #определяем временный путь для сохранения преорбазованного аудиофайла в формате .wav
            audio.export(temp_wav_path, format='wav')                                         #экспортируем преобразованное аудио в формат .wav и сохраняем по временному пути
        else:                                                                                 #иначе
            temp_wav_path = file_location                                                     #просто сохраняем аудиофайл
        recognizer = sr.Recognizer()                                                          #создаём объект-распознаватель речи
        with sr.AudioFile(temp_wav_path) as source:                                           #открываем аудиофайл
            audio_data = recognizer.record(source)                                            #и записываем его содержимое
            try:                                                                              #блок для отлова возможных ошибок
                text_from_audio = recognizer.recognize_google(audio_data, language='ru-RU')   #пробуем преобразовать данные аудиофайла с помощью сервисом Google
                return {'text': text_from_audio}                                              #возвращаем полученный текст
            except sr.UnknownValueError:                                                      #если ошибка связана с речью или шумом
                return {'text': 'Не удалось распознать аудио!'}                               #сообщение
            except sr.RequestError as e:                                                      #если ошибка при запросе
                return {'text': f'Возникла неожиданная ошибка: {e}'}                          #сообщение
    finally:                                                                                  #этот блок выполняется независимо от наличия ошибок
        if os.path.exists(temp_wav_path):                                                     #удаление временного файла
            os.remove(temp_wav_path)
        if os.path.exists(file_location):                                                     #удаление загруженного файла
            os.remove(file_location)
