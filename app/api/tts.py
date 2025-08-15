from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.utils.database import get_db
from app.models.tts_schemas import (
    TTSRequest, 
    TTSResponse, 
    LessonAudioRequest, 
    LessonAudioResponse,
    SupportedLanguagesResponse
)
from app.services.tts_service import tts_service
from app.api import crud

router = APIRouter(prefix="/tts", tags=["Text-to-Speech"])

@router.get("/supported-languages", response_model=SupportedLanguagesResponse)
async def get_supported_languages():
    """Get all supported languages and their voice options for TTS"""
    try:
        languages = tts_service.get_supported_languages()
        return SupportedLanguagesResponse(languages=languages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching supported languages: {str(e)}")

@router.post("/synthesize", response_model=TTSResponse)
async def synthesize_text(request: TTSRequest):
    """
    Convert text to speech using Google Cloud TTS
    
    - **text**: Text to convert to speech
    - **language**: Target language (e.g., "Telugu", "Hindi", "Kannada")
    - **voice_name**: Optional specific voice to use (uses default voice if not provided)
    - **speaking_rate**: Speech rate from 0.25 to 4.0 (default: 1.0)
    - **pitch**: Voice pitch from -20.0 to 20.0 (default: 0.0)
    - **volume_gain_db**: Volume gain from -96.0 to 16.0 (default: 0.0)
    - **audio_format**: Audio format "MP3" or "WAV" (default: "MP3")
    """
    try:
        result = tts_service.synthesize_speech(
            text=request.text,
            language=request.language,
            voice_name=request.voice_name,
            speaking_rate=request.speaking_rate,
            pitch=request.pitch,
            volume_gain_db=request.volume_gain_db,
            audio_format=request.audio_format
        )
        
        return TTSResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error synthesizing speech: {str(e)}")

@router.get("/synthesize-audio")
async def synthesize_text_to_audio(
    text: str,
    language: str,
    voice_name: str = None,
    speaker_name: str = None,
    speaking_rate: float = 1.0,
    pitch: float = 0.0,
    volume_gain_db: float = 0.0,
    audio_format: str = "MP3"
):
    """
    Convert text to speech and return raw audio file
    
    - **text**: Text to convert to speech
    - **language**: Target language
    - **voice_name**: Optional specific voice to use
    - **speaker_name**: Optional speaker name for gender-based voice selection
    - **speaking_rate**: Speech rate (default: 1.0)
    - **pitch**: Voice pitch (default: 0.0)
    - **volume_gain_db**: Volume gain (default: 0.0)
    - **audio_format**: Audio format "MP3" or "WAV" (default: "MP3")
    
    This endpoint returns the audio file directly instead of base64 encoded JSON
    """
    try:
        result = tts_service.synthesize_speech(
            text=text,
            language=language,
            voice_name=voice_name,
            speaker_name=speaker_name,
            speaking_rate=speaking_rate,
            pitch=pitch,
            volume_gain_db=volume_gain_db,
            audio_format=audio_format
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "TTS synthesis failed"))
        
        # Decode base64 audio content
        import base64
        audio_content = base64.b64decode(result["audio_content"])
        
        # Return audio file with proper headers
        return Response(
            content=audio_content,
            media_type=result["content_type"],
            headers={
                "Content-Disposition": f"attachment; filename=tts_audio.{audio_format.lower()}",
                "Content-Length": str(len(audio_content))
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating audio: {str(e)}")

@router.post("/lesson-audio", response_model=LessonAudioResponse)
async def generate_lesson_audio(request: LessonAudioRequest, db: Session = Depends(get_db)):
    """
    Generate audio for all components of a lesson (vocabulary, sentences, story)
    
    - **lesson_id**: ID of the lesson to generate audio for
    - **language**: Target language
    - **speaking_rate**: Speech rate for all audio (default: 1.0)
    """
    try:
        # Get lesson from database
        lesson = crud.get_desi_lesson(db, lesson_id=request.lesson_id)
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        
        # Convert lesson to format expected by TTS service
        lesson_data = crud.convert_db_lesson_to_response_format(lesson)
        lesson_dict = lesson_data.dict()["desi_lesson"]
        
        # Generate audio for all lesson components
        audio_result = tts_service.synthesize_lesson_audio(
            lesson_data=lesson_dict,
            language=request.language
        )
        
        return LessonAudioResponse(**audio_result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating lesson audio: {str(e)}")

@router.get("/lesson-audio/{lesson_id}")
async def generate_lesson_audio_get(
    lesson_id: int,
    language: str,
    speaking_rate: float = 1.0,
    db: Session = Depends(get_db)
):
    """
    Generate audio for lesson components using GET request
    
    This is a convenience endpoint that works the same as POST /lesson-audio
    """
    try:
        request = LessonAudioRequest(
            lesson_id=lesson_id,
            language=language,
            speaking_rate=speaking_rate
        )
        return await generate_lesson_audio(request, db)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating lesson audio: {str(e)}")

@router.post("/vocabulary-audio")
async def generate_vocabulary_audio(
    word: str,
    language: str,
    voice_name: str = None,
    speaking_rate: float = 0.8
):
    """
    Generate audio specifically for vocabulary words with optimized settings
    
    - **word**: Vocabulary word in target script
    - **language**: Target language
    - **voice_name**: Optional specific voice
    - **speaking_rate**: Slower rate for vocabulary learning (default: 0.8)
    """
    try:
        result = tts_service.synthesize_speech(
            text=word,
            language=language,
            voice_name=voice_name,
            speaking_rate=speaking_rate,
            pitch=0.0,
            volume_gain_db=2.0  # Slightly louder for vocabulary
        )
        
        return TTSResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating vocabulary audio: {str(e)}")

@router.post("/sentence-audio")
async def generate_sentence_audio(
    sentence: str,
    language: str,
    voice_name: str = None,
    speaking_rate: float = 0.9
):
    """
    Generate audio specifically for example sentences with optimized settings
    
    - **sentence**: Sentence in target script
    - **language**: Target language  
    - **voice_name**: Optional specific voice
    - **speaking_rate**: Slightly slower rate for sentence learning (default: 0.9)
    """
    try:
        result = tts_service.synthesize_speech(
            text=sentence,
            language=language,
            voice_name=voice_name,
            speaking_rate=speaking_rate,
            pitch=0.0,
            volume_gain_db=1.0
        )
        
        return TTSResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating sentence audio: {str(e)}")

@router.post("/dialogue-audio")
async def generate_dialogue_audio(
    text: str,
    language: str,
    speaker_name: str,
    speaking_rate: float = 1.0
):
    """
    Generate audio for dialogue
    
    - **text**: Dialogue text in target script
    - **language**: Target language
    - **speaker_name**: Name of the speaker (used for gender-based voice selection)
    - **speaking_rate**: Speech rate (default: 1.0)
    """
    try:
        result = tts_service.synthesize_speech(
            text=text,
            language=language,
            speaker_name=speaker_name,
            speaking_rate=speaking_rate,
            pitch=0.0,
            volume_gain_db=0.0
        )
        
        # Add speaker information to response
        if result["success"]:
            result["speaker_name"] = speaker_name
        
        return TTSResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating dialogue audio: {str(e)}")