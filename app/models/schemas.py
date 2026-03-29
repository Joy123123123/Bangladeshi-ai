from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ClassLevel(int, Enum):
    CLASS_9 = 9
    CLASS_10 = 10
    CLASS_11 = 11
    CLASS_12 = 12


class SubjectCode(str, Enum):
    BANGLA = "bangla"
    ENGLISH = "english"
    MATH = "math"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"
    ICT = "ict"
    HISTORY = "history"
    GEOGRAPHY = "geography"
    ECONOMICS = "economics"
    CIVICS = "civics"
    AGRICULTURE = "agriculture"
    HOME_SCIENCE = "home_science"
    BUSINESS = "business"
    HIGHER_MATH = "higher_math"
    GENERAL_SCIENCE = "general_science"
    GENERAL = "general"


class ExamType(str, Enum):
    SSC = "SSC"
    HSC = "HSC"
    BUET = "BUET"
    DU = "DU"
    MEDICAL = "Medical"
    BCS = "BCS"
    GENERAL = "General"


class AIModel(str, Enum):
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    GROK = "grok"
    AUTO = "auto"


class BoardType(str, Enum):
    DHAKA = "Dhaka"
    RAJSHAHI = "Rajshahi"
    CHITTAGONG = "Chittagong"
    SYLHET = "Sylhet"
    BARISAL = "Barisal"
    KHULNA = "Khulna"
    COMILLA = "Comilla"
    DINAJPUR = "Dinajpur"
    JESSORE = "Jessore"
    MYMENSINGH = "Mymensingh"


# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, description="User message (Bangla or Banglish)")
    class_level: Optional[ClassLevel] = Field(None, description="NCTB class level (9-12)")
    subject: Optional[SubjectCode] = Field(SubjectCode.GENERAL, description="Subject area")
    exam_type: Optional[ExamType] = Field(ExamType.GENERAL, description="Exam type for admission prep")
    board: Optional[BoardType] = Field(BoardType.DHAKA, description="Education board")
    data_saver_mode: bool = Field(False, description="Enable low-data mode for mobile users")
    preferred_model: AIModel = Field(AIModel.AUTO, description="Preferred AI model")
    session_id: Optional[str] = Field(None, description="User session identifier")
    include_rag: bool = Field(True, description="Include RAG context from question banks")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "পদার্থবিজ্ঞানে নিউটনের গতিসূত্র কী?",
                "class_level": 10,
                "subject": "physics",
                "exam_type": "SSC",
                "board": "Dhaka",
                "data_saver_mode": False,
                "preferred_model": "auto",
                "include_rag": True,
            }
        }


class FeedbackRequest(BaseModel):
    session_id: str
    message_id: str
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    comment: Optional[str] = Field(None, max_length=500)


# ---------------------------------------------------------------------------
# Response Models
# ---------------------------------------------------------------------------

class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class ChatResponse(BaseModel):
    message: str
    session_id: str
    model_used: str
    subject: Optional[str] = None
    class_level: Optional[int] = None
    rag_used: bool = False
    tokens_used: Optional[int] = None


class StreamChunk(BaseModel):
    content: str
    done: bool = False
    error: Optional[str] = None


class SubjectInfo(BaseModel):
    code: str
    name_bn: str
    name_en: str


class NCTBContextResponse(BaseModel):
    class_level: int
    subject: str
    board: str
    system_prompt: str
    syllabus_topics: List[str] = []


class HealthResponse(BaseModel):
    status: str
    version: str
    models_available: List[str]


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
