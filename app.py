import streamlit as st
import librosa
import numpy as np
from collections import Counter

st.set_page_config(page_title="Asistente de Armonía", page_icon="🎵")

st.title("🎙️ Asistente de Armonía por Voz")
st.write("Analizamos tu melodía y tu registro vocal para darte acordes acordes a tu tono.")

audio_file = st.file_uploader("Sube un audio (.wav o .mp3)", type=["wav", "mp3"])
recorded_audio = st.audio_input("O graba tu voz directamente:")

target_audio = recorded_audio if recorded_audio else audio_file

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def hz_to_note_info(frequency):
    if frequency <= 0 or np.isnan(frequency):
        return None, None
    midi_number = int(round(69 + 12 * np.log2(frequency / 440.0)))
    note_index = midi_number % 12
    return NOTE_NAMES[note_index], midi_number

def get_vocal_range(avg_hz):
    """Determina el tipo de registro vocal según la frecuencia media."""
    if avg_hz < 165:
        return "Grave (Bajo / Contralto)", "🕯️ Tono Cálido / Profundo"
    elif 165 <= avg_hz <= 260:
        return "Medio (Tenor / Mezzosoprano)", "✨ Tono Equilibrado / Natural"
    else:
        return "Agudo (Soprano / Tenor Alto)", "🚀 Tono Brillante / Agudo"

if target_audio:
    st.audio(target_audio)
    
    if st.button("🔍 Analizar Voz y Armonizar"):
        with st.spinner("Analizando tu tono y tesitura vocal..."):
            y, sr = librosa.load(target_audio, sr=None)
            
            f0, voiced_flag, _ = librosa.pyin(
                y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C6'), sr=sr
            )
            clean_pitches = [f for f, v in zip(f0, voiced_flag) if v and not np.isnan(f)]

            if clean_pitches:
                # 1. Detección de Registro Vocal
                avg_hz = np.mean(clean_pitches)
                tipo_registro, descripcion = get_vocal_range(avg_hz)
                
                # 2. Extracción de Notas y Centro Tonal Dominante
                note_list = []
                for f in clean_pitches:
                    note, _ = hz_to_note_info(f)
                    if note:
                        note_list.append(note)

                # La nota más repetida se asume como el Centro Tonal (Tónica)
                most_common_notes = Counter(note_list).most_common(1)
                tonic_note = most_common_notes[0][0]
                
                st.markdown("---")
                st.subheader("📊 Análisis Vocal")
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Registro Detectado", tipo_registro)
                    st.caption(f"Frecuencia media: {int(avg_hz)} Hz | {descripcion}")
                with c2:
                    st.metric("Tonalidad Ideal para tu Voz", f"Tónica en {tonic_note}")
                    st.caption(f"Notas más usadas: {', '.join(set(note_list[:6]))}")

                # 3. Lógica de Acordes
                idx = NOTE_NAMES.index(tonic_note)
                dom = NOTE_NAMES[(idx + 7) % 12]       # Grado V
                rel_m = NOTE_NAMES[(idx + 9) % 12] + "m" # Grado vi
                sub_d = NOTE_NAMES[(idx + 5) % 12]     # Grado IV

                st.markdown("---")
                st.markdown("### 🎼 Progresiones Adaptadas")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.subheader("Pop Comercial")
                    st.info(f"**{tonic_note} ➔ {dom} ➔ {rel_m} ➔ {sub_d}**")
                with col2:
                    st.subheader("Balada / Triste")
                    st.warning(f"**{rel_m} ➔ {sub_d} ➔ {tonic_note} ➔ {dom}**")
                with col3:
                    st.subheader("Jazzy / Neo-Soul")
                    st.success(f"**{tonic_note}maj7 ➔ {sub_d}maj7 ➔ {rel_m}7 ➔ {dom}7**")
            else:
                st.error("No se detectó una melodía clara. Intenta tararear con mayor volumen.")
