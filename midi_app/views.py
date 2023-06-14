from django.shortcuts import render
from django.http import JsonResponse
import mido
from mido import MidiFile
from music21 import converter, chord, note
import json
import tempfile
from django.core.files.uploadedfile import InMemoryUploadedFile
from music21.duration import Duration


def midi_to_tab_text(midi_file):
    stream = converter.parse(midi_file, format='midi')
    tracks_tabs = []

    min_duration = None
    min_duration_str = ''
    for part in stream.parts:
        notes = part.flat.notes.stream()
        tab_text = ""

        first_element_offset = None
        for element in notes:
            if isinstance(element, note.Note) or isinstance(element, chord.Chord):
                if min_duration is None or element.duration.quarterLength < min_duration.quarterLength:
                    min_duration = element.duration
                if first_element_offset is None:
                    first_element_offset = element.offset

        # Конвертируем минимальную длительность в обозначение длительности
        min_duration_str = min_duration.fullName

        # Добавляем начальные пробелы на основе смещения первого элемента
        initial_spaces = int(first_element_offset / min_duration.quarterLength)
        tab_text += "<td></td>" * initial_spaces

        for element in notes:
            if isinstance(element, note.Note):
                tab_text += f'<td>{element.pitch.unicodeNameWithOctave.upper()}</td>'
            elif isinstance(element, chord.Chord):
                tab_text += '<td>'
                for pitch in element.pitches:
                    tab_text += f'{pitch.unicodeNameWithOctave.upper()} '
                tab_text += '</td>'

            # Вычисляем количество нижних подчеркиваний, соответствующих длительности паузы
            num_spaces = int(element.duration.quarterLength / min_duration.quarterLength) - 1
            tab_text += "<td></td>" * num_spaces

        tracks_tabs.append(tab_text.strip())

    return min_duration_str, tracks_tabs


def upload_midi(request):
    if request.method == 'POST':
        midi_file = request.FILES['midi_file']

        # Если файл загружен в память, сохраняем его во временный файл
        if isinstance(midi_file, InMemoryUploadedFile):
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                for chunk in midi_file.chunks():
                    temp_file.write(chunk)
                temp_file.flush()
                min_duration, tab_text = midi_to_tab_text(temp_file.name)
        else:
            min_duration, tab_text = midi_to_tab_text(midi_file.temporary_file_path())

        return JsonResponse({'min_duration': min_duration, 'tracks_tabs': tab_text})
    return render(request, 'midi_app/upload_midi.html')
