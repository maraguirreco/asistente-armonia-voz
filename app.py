import streamlit as st
import librosa
import numpy as np

st.set_page_config(page_title="Asistente de Armonía", page_icon="🎵")

st.title("🎙️ Asistente de Armonía por Voz")
st.write("Graba un tarareo o sube un archivo para descubrir qué acordes le quedan bien a tu melodía.")

# Opción de grabar directamente en el navegador o subir archivo
audio_file = st.file_uploader("Sube un audio (.wav o .mp3)", type=["wav", "mp3"])
recorded_audio = st.audio_input("O graba tu voz aquí directamente:")

# Seleccionamos cuál audio usar
target_audio = recorded_audio if recorded_audio else audio_file

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def hz_to_note_name(frequency):
    if frequency <= 0 or np.isnan(frequency):
        return None
    midi_number = int(round(69 + 12 * np.log2(frequency / 440.0)))
    note_index = midi_number % 12
    octave = (midi_number // 12) - 1
    return f"{NOTE_NAMES[note_index]}{octave}"

if target_audio:
    st.audio(target_audio)
    
    if st.button("🔍 Analizar y Generar Armonías"):
        with st.spinner("Analizando la frecuencia de tu voz..."):
            # Cargar el audio
            y, sr = librosa.load(target_audio, sr=None)
            
            # Extraer tono
            f0, voiced_flag, _ = librosa.pyin(
                y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C6'), sr=sr
            )
            clean_pitches = [f for f, v in zip(f0, voiced_flag) if v and not np.isnan(f)]

            if clean_pitches:
                detected_notes = [hz_to_note_name(f) for f in clean_pitches]
                melody = [detected_notes[0]]
                for note in detected_notes[1:]:
                    if note != melody[-1] and note is not None:
                        melody.append(note)

                st.success(f"**Notas detectadas:** {', '.join(melody[:8])}")
                
                root_note = melody[0]
                base = root_note[:-1] if root_note[-1].isdigit() else root_note

                st.markdown("### 🎼 Progresiones de Acordes Sugeridas")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.subheader("Pop / Comercial")
                    st.info(f"**{base} ➔ G ➔ Am ➔ F**")
                with col2:
                    st.subheader("Emotiva / Triste")
                    st.warning(f"**{base}m ➔ F ➔ C ➔ G**")
                with col3:
                    st.subheader("Jazzy / Neo-Soul")
                    st.success(f"**{base}maj7 ➔ Dm7 ➔ Em7 ➔ Am7**")
            else:
                st.error("No se detectó una melodía clara. Intenta cantar un poco más fuerte o cerca del micrófono.")
