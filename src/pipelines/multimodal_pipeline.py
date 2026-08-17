from src.pipelines.face_pipeline import get_face_verification_scores
from src.pipelines.voice_pipeline import process_bulk_audio

# Same thresholds already used independently by face_pipeline.predict_attendance
# (distance <= 0.6) and voice_pipeline.identify_speaker (similarity >= 0.65).
# Reused here, not redefined with new tuning, so multimodal behavior stays
# consistent with the existing single-modality flows.
FACE_MATCH_THRESHOLD = 0.6   # lower distance = better match
VOICE_MATCH_THRESHOLD = 0.65  # higher similarity = better match


def verify_multimodal(face_scores, audio_bytes, candidates_voice_dict):
    """
    Combines independently-computed face scores (dict: student_id -> distance)
    with a fresh voice recognition pass over audio_bytes.

    Each modality must independently clear its own confidence threshold.
    Scores are NOT averaged or blended - a student is only marked present
    if BOTH modalities agree. A single matching modality is flagged for
    manual review instead of being auto-marked present.

    Returns: {student_id: {face_score, face_match, voice_score, voice_match,
                            decision, is_present}}
    """
    voice_scores = process_bulk_audio(audio_bytes, candidates_voice_dict) if audio_bytes else {}

    all_ids = set(face_scores.keys()) | set(voice_scores.keys()) | set(candidates_voice_dict.keys())

    report = {}

    for sid in all_ids:
        face_score = face_scores.get(sid)
        voice_score = voice_scores.get(sid)

        face_match = face_score is not None and face_score <= FACE_MATCH_THRESHOLD
        voice_match = voice_score is not None and voice_score >= VOICE_MATCH_THRESHOLD

        if face_match and voice_match:
            decision = "Present (Face + Voice Verified)"
            is_present = True
        elif face_match or voice_match:
            decision = "Flagged for Review (only one modality matched)"
            is_present = False
        else:
            decision = "Absent"
            is_present = False

        report[sid] = {
            'face_score': face_score,
            'face_match': face_match,
            'voice_score': voice_score,
            'voice_match': voice_match,
            'decision': decision,
            'is_present': is_present,
        }

    return report
