import streamlit as st
import librosa
import numpy as np

st.set_page_config(page_title="Asistente de Armonía", page_icon="🎵")

st.title("🎙️ Asistente de Armonía por Voz")
st.write("Graba un tarareo para descubrir qué acordes le quedan bien a tu melodía.")

# 1. Selector de modo / instrumento
instrumento = st.radio(
    "Selecciona el modo de armonía:",
    ["🎹 Estándar (Piano / Guitarra)", "🪕 Modo Ukelele"],
    horizontal=True
)

audio_file = st.file_uploader("Sube un audio (.wav o .mp3)", type=["wav", "mp3"])
recorded_audio = st.audio_input("O graba tu voz aquí directamente:")

target_audio = recorded_audio if recorded_audio else audio_file

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Diccionario de posiciones para Ukelele (Afinación Estándar G-C-E-A)
# Los números son los trastes de izquierda a derecha: G - C - E - A (0 = cuerda al aire)
UKULELE_FINGERINGS = {
    'C': '0 - 0 - 0 - 3',   'C#': '1 - 1 - 1 - 4', 'D': '2 - 2 - 2 - 0',
    'D#': '3 - 3 - 3 - 1',  'E': '1 - 4 - 0 - 2',   'F': '2 - 0 - 1 - 0',
    'F#': '3 - 1 - 2 - 1',  'G': '0 - 2 - 3 - 2',   'G#': '5 - 3 - 4 - 3',
    'A': '2 - 1 - 0 - 0',   'A#': '3 - 2 - 1 - 1',  'B': '4 - 3 - 2 - 2',
    'Cm': '0 - 3 - 3 - 3',  'Dm': '2 - 2 - 1 - 0',  'Em': '0 - 4 - 3 - 2',
    'Fm': '1 - 0 - 1 - 3',  'Gm': '0 - 2 - 3 - 1',  'Am': '2 - 0 - 0 - 0',
    'Bm': '2 - 2 - 2 - 2'
}

def hz_to_note_name(frequency):
    if frequency <= 0 or np.isnan(frequency):
        return None
    midi_number = int(round(69 + 12 * np.log2(frequency / 440.0)))
    note_index = midi_number % 12
    octave = (midi_number // 12) - 1
    return f"{NOTE_NAMES[note_index]}{octave}"

def get_uke_pos(chord_name):
    return UKULELE_FINGERINGS.get(chord_name, "Trastes estándar")

if target_audio:
    st.audio(target_audio)
    
    if st.button("🔍 Analizar y Generar Armonías"):
        with st.spinner("Analizando la frecuencia de tu voz..."):
            y, sr = librosa.load(target_audio, sr=None)
            
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
                
                # Cálculo de acordes según teoría básica
                idx = NOTE_NAMES.index(base)
                dom = NOTE_NAMES[(idx + 7) % 12]       # Grado V (Dominante)
                rel_m = NOTE_NAMES[(idx + 9) % 12] + "m" # Grado vi (Relativo menor)
                sub_d = NOTE_NAMES[(idx + 5) % 12]     # Grado IV (Subdominante)

                st.markdown("### 🎼 Progresiones Sugeridas")

                if "Ukelele" in instrumento:
                    st.info("💡 **Guía de trastes en Ukelele:** Los números corresponden a la posición de tus dedos en las cuerdas **[G - C - E - A]** (0 es cuerda al aire).")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("🪕 Pop Acústico / Folk")
                        st.markdown(f"**Progresión:** `{base} ➔ {dom} ➔ {rel_m} ➔ {sub_d}`")
                        st.code(
                            f"{base}: [{get_uke_pos(base)}]\n"
                            f"{dom}: [{get_uke_pos(dom)}]\n"
                            f"{rel_m}: [{get_uke_pos(rel_m)}]\n"
                            f"{sub_d}: [{get_uke_pos(sub_d)}]"
                        )
                    with col2:
                        st.subheader("🌴 Island Feel / Reggae")
                        st.markdown(f"**Progresión:** `{base} ➔ {sub_d} ➔ {dom} ➔ {base}`")
                        st.code(
                            f"{base}: [{get_uke_pos(base)}]\n"
                            f"{sub_d}: [{get_uke_pos(sub_d)}]\n"
                            f"{dom}: [{get_uke_pos(dom)}]\n"
                            f"{base}: [{get_uke_pos(base)}]"
                        )
                else:
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
