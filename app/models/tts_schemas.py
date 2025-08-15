from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech")
    language: str = Field(..., description="Target language (e.g., 'Telugu', 'Hindi')")
    voice_name: Optional[str] = Field(None, description="Specific voice to use (uses default if not provided)")
    speaker_name: Optional[str] = Field(None, description="Speaker name for reference only")
    speaker_index: int = Field(0, description="Speaker index for reference only")
    speaking_rate: float = Field(1.0, ge=0.25, le=4.0, description="Speech rate (0.25 to 4.0)")
    pitch: float = Field(0.0, ge=-20.0, le=20.0, description="Voice pitch (-20.0 to 20.0)")
    volume_gain_db: float = Field(0.0, ge=-96.0, le=16.0, description="Volume gain (-96.0 to 16.0)")
    audio_format: str = Field("MP3", description="Audio format (MP3 or WAV)")

class TTSResponse(BaseModel):
    success: bool
    audio_content: Optional[str] = Field(None, description="Base64 encoded audio content")
    content_type: Optional[str] = Field(None, description="MIME type of audio content")
    language: str
    language_code: Optional[str] = None
    voice_name: Optional[str] = None
    text: str
    audio_format: Optional[str] = None
    parameters: Optional[Dict[str, float]] = None
    speaker_name: Optional[str] = None
    detected_gender: Optional[str] = None
    error: Optional[str] = None

class LessonAudioRequest(BaseModel):
    lesson_id: int = Field(..., description="ID of the lesson to generate audio for")
    language: str = Field(..., description="Target language")
    speaking_rate: float = Field(1.0, ge=0.25, le=4.0, description="Speech rate")

class VocabularyAudio(BaseModel):
    word: str
    target_script: str
    audio: str = Field(..., description="Base64 encoded audio")
    content_type: str

class SentenceAudio(BaseModel):
    english: str
    target_script: str
    audio: str = Field(..., description="Base64 encoded audio")
    content_type: str

class DialogueAudio(BaseModel):
    speaker: str
    english: str
    target_script: str
    audio: str = Field(..., description="Base64 encoded audio")
    content_type: str
    voice_used: Optional[str] = None
    detected_gender: Optional[str] = None

class LessonAudioResponse(BaseModel):
    success: bool
    vocabulary: List[VocabularyAudio] = []
    example_sentences: List[SentenceAudio] = []
    story_dialogue: List[DialogueAudio] = []
    errors: List[str] = []

class SupportedLanguagesResponse(BaseModel):
    languages: Dict[str, Dict[str, Any]]