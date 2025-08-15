import os
import base64
import tempfile
from typing import Optional, Dict, Any
from google.cloud import texttospeech
from google.oauth2 import service_account
import json
from pathlib import Path

class TTSService:
    def __init__(self):
        self.client = self._initialize_client()
        
        # Language mapping for South Asian languages with gender-specific voices
        self.language_mappings = {
            "Telugu": {
                "language_code": "te-IN",
                "default_voice": "te-IN-Standard-A",
                "female_voices": ["te-IN-Standard-A", "te-IN-Standard-C"],
                "male_voices": ["te-IN-Standard-B", "te-IN-Standard-D"]
            },
            "Hindi": {
                "language_code": "hi-IN", 
                "default_voice": "hi-IN-Standard-A",
                "female_voices": ["hi-IN-Standard-A", "hi-IN-Standard-D", "hi-IN-Standard-E"],
                "male_voices": ["hi-IN-Standard-B", "hi-IN-Standard-C", "hi-IN-Standard-F"]
            },
            "Kannada": {
                "language_code": "kn-IN",
                "default_voice": "kn-IN-Standard-A",
                "female_voices": ["kn-IN-Standard-A", "kn-IN-Standard-C"],
                "male_voices": ["kn-IN-Standard-B", "kn-IN-Standard-D"]
            },
            "Tamil": {
                "language_code": "ta-IN",
                "default_voice": "ta-IN-Standard-A",
                "female_voices": ["ta-IN-Standard-A", "ta-IN-Standard-C"],
                "male_voices": ["ta-IN-Standard-B", "ta-IN-Standard-D"]
            },
            "Gujarati": {
                "language_code": "gu-IN",
                "default_voice": "gu-IN-Standard-A",
                "female_voices": ["gu-IN-Standard-A", "gu-IN-Standard-C"],
                "male_voices": ["gu-IN-Standard-B", "gu-IN-Standard-D"]
            },
            "Marathi": {
                "language_code": "mr-IN",
                "default_voice": "mr-IN-Standard-A",
                "female_voices": ["mr-IN-Standard-A", "mr-IN-Standard-C"],
                "male_voices": ["mr-IN-Standard-B"]
            },
            "Bengali": {
                "language_code": "bn-IN",
                "default_voice": "bn-IN-Standard-A",
                "female_voices": ["bn-IN-Standard-A", "bn-IN-Standard-C"],
                "male_voices": ["bn-IN-Standard-B", "bn-IN-Standard-D"]
            },
            "Punjabi": {
                "language_code": "pa-IN",
                "default_voice": "pa-IN-Standard-A",
                "female_voices": ["pa-IN-Standard-A", "pa-IN-Standard-C"],
                "male_voices": ["pa-IN-Standard-B", "pa-IN-Standard-D"]
            },
            "Malayalam": {
                "language_code": "ml-IN",
                "default_voice": "ml-IN-Standard-A",
                "female_voices": ["ml-IN-Standard-A", "ml-IN-Standard-C"],
                "male_voices": ["ml-IN-Standard-B", "ml-IN-Standard-D"]
            },
            "English": {
                "language_code": "en-US",
                "default_voice": "en-US-Standard-A",
                "female_voices": ["en-US-Standard-A", "en-US-Standard-C", "en-US-Standard-E", "en-US-Standard-F"],
                "male_voices": ["en-US-Standard-B", "en-US-Standard-D", "en-US-Standard-I", "en-US-Standard-J"]
            },
            "Urdu": {
                "language_code": "ur-IN",
                "default_voice": "ur-IN-Standard-A",
                "female_voices": ["ur-IN-Standard-A"],
                "male_voices": ["ur-IN-Standard-B"]
            },
            # Note: Odia and Assamese are not currently supported by Google Cloud TTS
            # Using Hindi as fallback for these languages since they are closely related
            "Odia": {
                "language_code": "hi-IN",
                "default_voice": "hi-IN-Standard-A",
                "female_voices": ["hi-IN-Standard-A", "hi-IN-Standard-B"],
                "male_voices": ["hi-IN-Standard-C", "hi-IN-Standard-D"],
                "fallback_note": "Using Hindi voice as Odia is not supported by Google TTS"
            },
            "Assamese": {
                "language_code": "hi-IN",
                "default_voice": "hi-IN-Standard-A",
                "female_voices": ["hi-IN-Standard-A", "hi-IN-Standard-B"],
                "male_voices": ["hi-IN-Standard-C", "hi-IN-Standard-D"],
                "fallback_note": "Using Hindi voice as Assamese is not supported by Google TTS"
            }
        }
        
        # Indian names for gender detection
        self.indian_male_names = {
            "Arun", "Arjun", "Amit", "Anish", "Ashwin", "Aditya", "Aniket", "Abhishek",
            "Raj", "Ravi", "Rohan", "Rahul", "Rajesh", "Raman", "Rakesh", "Ramesh",
            "Vikram", "Vivek", "Vikas", "Vinay", "Vimal", "Varun", "Vishal", "Vijay",
            "Suresh", "Sanjay", "Sandeep", "Satish", "Suman", "Subhash", "Sagar", "Shyam",
            "Manoj", "Mahesh", "Mohan", "Mukesh", "Manohar", "Manish", "Mohit", "Milan",
            "Kiran", "Krishna", "Karthik", "Kishore", "Kartik", "Kamal", "Kumar", "Kapil",
            "Deepak", "Dev", "Dinesh", "Dhruv", "Darshan", "Dhawal", "Daksh", "Divya",
            "Nikhil", "Nishant", "Naveen", "Naresh", "Nitesh", "Nitin", "Nilesh", "Naval",
            "Gaurav", "Gopal", "Girish", "Ganesh", "Govind", "Gagan", "Gautam", "Gunjan",
            "Harsh", "Hemant", "Hari", "Hitesh", "Hiren", "Hardik", "Haresh", "Himanshu",
            "Jatin", "Jayesh", "Jigar", "Jignesh", "Jagdish", "Janak", "Jaidev", "Jagmohan",
            "Lalit", "Lokesh", "Lucky", "Laxman", "Lakhan", "Leela", "Lalan", "Lalchand",
            "Bhavin", "Bharat", "Bhavesh", "Bharath", "Bhanu", "Bhushan", "Bhupesh", "Bhargav",
            "Chetan", "Chirag", "Chandan", "Chandresh", "Chintan", "Chaitanya", "Charan", "Chaman",
            "Paresh", "Pawan", "Pradeep", "Prakash", "Pankaj", "Pramod", "Pranav", "Pritesh",
            "Tarun", "Tushar", "Tejas", "Tanuj", "Tapas", "Trilok", "Tarang", "Tanmay",
            "Yogesh", "Yash", "Yatin", "Yashpal", "Yugal", "Yuvraj", "Yogendra", "Yagnesh"
        }
        
        self.indian_female_names = {
            "Priya", "Pooja", "Preeti", "Pallavi", "Payal", "Pratiksha", "Priyanka", "Poonam",
            "Anita", "Asha", "Aarti", "Anjali", "Aparna", "Aditi", "Aruna", "Anushka",
            "Sunita", "Sudha", "Sneha", "Swati", "Shalini", "Shilpa", "Shruti", "Sanya",
            "Meera", "Maya", "Manisha", "Madhuri", "Mala", "Manju", "Malini", "Mohini",
            "Kavitha", "Kamala", "Kiran", "Kalyani", "Kalpana", "Kanchan", "Komal", "Kriti",
            "Deepika", "Divya", "Devika", "Diya", "Damini", "Durga", "Daksha", "Darsha",
            "Nisha", "Nikita", "Neha", "Naina", "Namrata", "Nandini", "Natasha", "Navya",
            "Geeta", "Gita", "Gayatri", "Ganga", "Garima", "Gitika", "Gunjan", "Gouri",
            "Rekha", "Radha", "Ritu", "Ruchi", "Rashmi", "Rohini", "Ragini", "Renuka",
            "Vidya", "Vinita", "Vimala", "Vandana", "Varsha", "Vasudha", "Veena", "Vibha",
            "Lalita", "Lata", "Laxmi", "Leela", "Lila", "Lakshmi", "Latha", "Lavanya",
            "Bharati", "Bhavna", "Bindiya", "Bina", "Babita", "Bela", "Bhagyashree", "Bhumi",
            "Chitra", "Chhaya", "Chandni", "Champa", "Charu", "Chinmay", "Chandrika", "Chetna",
            "Heera", "Hema", "Hina", "Hiral", "Harsha", "Hasina", "Harika", "Himani",
            "Jaya", "Jyoti", "Jasmine", "Juhi", "Jhanvi", "Janaki", "Jinal", "Jigisha",
            "Tanvi", "Tara", "Tulsi", "Tejal", "Trupti", "Twinkle", "Tanuja", "Tarika",
            "Urmila", "Usha", "Uma", "Ujjwala", "Upasana", "Urvashi", "Utkarsha", "Unnati",
            "Yamini", "Yashoda", "Yogita", "Yukti", "Yuvika", "Yashika", "Yamuna", "Yami"
        }
    
    def _initialize_client(self) -> texttospeech.TextToSpeechClient:
        """Initialize Google Cloud TTS client with service account credentials"""
        try:
            # Path to the service account key file (updated for new project structure)
            credentials_path = Path(__file__).parent.parent.parent / "config" / "google_tts.json"
            
            if not credentials_path.exists():
                raise FileNotFoundError(f"Google TTS credentials file not found at {credentials_path}")
            
            # Load credentials from the JSON file
            credentials = service_account.Credentials.from_service_account_file(
                str(credentials_path),
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            
            # Initialize the client
            client = texttospeech.TextToSpeechClient(credentials=credentials)
            return client
            
        except Exception as e:
            print(f"Error initializing TTS client: {e}")
            raise
    
    def get_supported_languages(self) -> Dict[str, Dict[str, Any]]:
        """Get all supported languages and their voice options"""
        return self.language_mappings
    
    def is_fallback_language(self, language: str) -> bool:
        """Check if a language is using a fallback voice"""
        if language in self.language_mappings:
            return "fallback_note" in self.language_mappings[language]
        return False
    
    def get_fallback_info(self, language: str) -> str:
        """Get fallback information for a language"""
        if language in self.language_mappings and "fallback_note" in self.language_mappings[language]:
            return self.language_mappings[language]["fallback_note"]
        return ""
    
    def detect_gender_from_name(self, name: str) -> str:
        """
        Detect gender from Indian name (case-insensitive)
        
        Args:
            name: Speaker name to analyze
            
        Returns:
            'male', 'female', or 'neutral' if unknown
        """
        # Clean the name (remove titles, extra spaces, etc.) and make it title case
        clean_name = name.strip().split()[0].title() if name else ""
        
        if clean_name in self.indian_male_names:
            return "male"
        elif clean_name in self.indian_female_names:
            return "female"
        else:
            return "neutral"
    
    def get_voice_for_speaker(self, speaker_name: str, language: str) -> str:
        """
        Get appropriate voice based on speaker's gender and language
        
        Args:
            speaker_name: Name of the speaker
            language: Target language
            
        Returns:
            Voice name appropriate for the speaker's gender
        """
        if language not in self.language_mappings:
            return self.language_mappings.get("English", {}).get("default_voice", "en-US-Standard-A")
        
        lang_config = self.language_mappings[language]
        gender = self.detect_gender_from_name(speaker_name)
        
        # Select voice based on detected gender
        if gender == "male" and "male_voices" in lang_config:
            # Use first male voice (can be randomized if desired)
            return lang_config["male_voices"][0]
        elif gender == "female" and "female_voices" in lang_config:
            # Use first female voice (can be randomized if desired)
            return lang_config["female_voices"][0]
        else:
            # Use default voice for neutral/unknown gender
            return lang_config["default_voice"]
    
    def synthesize_speech(
        self, 
        text: str, 
        language: str, 
        voice_name: Optional[str] = None,
        speaker_name: Optional[str] = None,
        speaking_rate: float = 1.0,
        pitch: float = 0.0,
        volume_gain_db: float = 0.0,
        audio_format: str = "MP3"
    ) -> Dict[str, Any]:
        """
        Synthesize speech from text using Google Cloud TTS
        
        Args:
            text: Text to convert to speech
            language: Target language (e.g., "Telugu", "Hindi")
            voice_name: Specific voice to use (optional, uses default if not provided)
            speaker_name: Name of speaker for gender-based voice selection (optional)
            speaking_rate: Speech rate (0.25 to 4.0)
            pitch: Voice pitch (-20.0 to 20.0)
            volume_gain_db: Volume gain (-96.0 to 16.0)
            audio_format: Audio format ("MP3" or "WAV")
            
        Returns:
            Dictionary containing audio content and metadata
        """
        try:
            # Validate language
            if language not in self.language_mappings:
                raise ValueError(f"Language '{language}' is not supported. Available languages: {list(self.language_mappings.keys())}")
            
            lang_config = self.language_mappings[language]
            language_code = lang_config["language_code"]
            
            # Voice selection priority: explicit voice_name > speaker-based gender voice > default voice
            if voice_name:
                selected_voice = voice_name
            elif speaker_name:
                selected_voice = self.get_voice_for_speaker(speaker_name, language)
            else:
                selected_voice = lang_config["default_voice"]
            
            # Validate parameters
            speaking_rate = max(0.25, min(4.0, speaking_rate))
            pitch = max(-20.0, min(20.0, pitch))
            volume_gain_db = max(-96.0, min(16.0, volume_gain_db))
            
            # Configure synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Configure voice parameters with appropriate gender
            detected_gender = "neutral"
            ssml_gender = texttospeech.SsmlVoiceGender.NEUTRAL
            
            if speaker_name:
                detected_gender = self.detect_gender_from_name(speaker_name)
                if detected_gender == "male":
                    ssml_gender = texttospeech.SsmlVoiceGender.MALE
                elif detected_gender == "female":
                    ssml_gender = texttospeech.SsmlVoiceGender.FEMALE
            
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                name=selected_voice,
                ssml_gender=ssml_gender
            )
            
            # Configure audio format
            if audio_format.upper() == "WAV":
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                    speaking_rate=speaking_rate,
                    pitch=pitch,
                    volume_gain_db=volume_gain_db
                )
                content_type = "audio/wav"
            else:  # Default to MP3
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=speaking_rate,
                    pitch=pitch,
                    volume_gain_db=volume_gain_db
                )
                content_type = "audio/mpeg"
            
            # Perform the text-to-speech request
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Encode audio content as base64 for JSON response
            audio_base64 = base64.b64encode(response.audio_content).decode('utf-8')
            
            return {
                "success": True,
                "audio_content": audio_base64,
                "content_type": content_type,
                "language": language,
                "language_code": language_code,
                "voice_name": selected_voice,
                "text": text,
                "audio_format": audio_format.upper(),
                "detected_gender": detected_gender,
                "speaker_name": speaker_name,
                "parameters": {
                    "speaking_rate": speaking_rate,
                    "pitch": pitch,
                    "volume_gain_db": volume_gain_db
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "language": language,
                "text": text
            }
    
    def synthesize_lesson_audio(self, lesson_data: Dict[str, Any], language: str) -> Dict[str, Any]:
        """
        Generate audio for all components of a lesson
        
        Args:
            lesson_data: Complete lesson data from database
            language: Target language
            
        Returns:
            Dictionary with audio for vocabulary, sentences, and story
        """
        audio_content = {
            "vocabulary": [],
            "example_sentences": [],
            "story_dialogue": [],
            "success": True,
            "errors": []
        }
        
        try:
            # Generate audio for vocabulary items
            if "vocabulary" in lesson_data:
                for vocab_item in lesson_data["vocabulary"]:
                    if "target_script" in vocab_item:
                        audio_result = self.synthesize_speech(
                            text=vocab_item["target_script"],
                            language=language,
                            speaking_rate=0.8  # Slower for vocabulary learning
                        )
                        if audio_result["success"]:
                            audio_content["vocabulary"].append({
                                "word": vocab_item.get("english", ""),
                                "target_script": vocab_item["target_script"],
                                "audio": audio_result["audio_content"],
                                "content_type": audio_result["content_type"]
                            })
                        else:
                            audio_content["errors"].append(f"Failed to generate audio for vocabulary: {vocab_item.get('english', '')}")
            
            # Generate audio for example sentences
            if "example_sentences" in lesson_data:
                for sentence in lesson_data["example_sentences"]:
                    if "target_script" in sentence:
                        audio_result = self.synthesize_speech(
                            text=sentence["target_script"],
                            language=language,
                            speaking_rate=0.9  # Slightly slower for sentences
                        )
                        if audio_result["success"]:
                            audio_content["example_sentences"].append({
                                "english": sentence.get("english", ""),
                                "target_script": sentence["target_script"],
                                "audio": audio_result["audio_content"],
                                "content_type": audio_result["content_type"]
                            })
                        else:
                            audio_content["errors"].append(f"Failed to generate audio for sentence: {sentence.get('english', '')}")
            
            # Generate audio for story dialogue
            if "short_story" in lesson_data and "dialogue" in lesson_data["short_story"]:
                for dialogue_item in lesson_data["short_story"]["dialogue"]:
                    if "target_script" in dialogue_item:
                        speaker_name = dialogue_item.get("speaker", "")
                        audio_result = self.synthesize_speech(
                            text=dialogue_item["target_script"],
                            language=language,
                            speaker_name=speaker_name
                        )
                        if audio_result["success"]:
                            audio_content["story_dialogue"].append({
                                "speaker": speaker_name,
                                "english": dialogue_item.get("english", ""),
                                "target_script": dialogue_item["target_script"],
                                "audio": audio_result["audio_content"],
                                "content_type": audio_result["content_type"],
                                "voice_used": audio_result["voice_name"],
                                "detected_gender": audio_result.get("detected_gender", "neutral")
                            })
                        else:
                            audio_content["errors"].append(f"Failed to generate audio for dialogue: {speaker_name}")
            
            if audio_content["errors"]:
                audio_content["success"] = False
                
        except Exception as e:
            audio_content["success"] = False
            audio_content["errors"].append(f"Error generating lesson audio: {str(e)}")
        
        return audio_content

# Global TTS service instance
tts_service = TTSService()