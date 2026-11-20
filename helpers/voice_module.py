import speech_recognition as sr

DISTRESS_KEYWORDS = [
    "help", "help me", "bachao", "save me", "emergency", "police",
    "danger", "khatra", "stop", "chodo", "madad", "raksha"
]

def check_distress_phrase(text):
    """Checks if recognized phrase contains distress/danger keywords."""
    if not text:
        return False
    lower = text.lower().strip()
    return any(kw in lower for kw in DISTRESS_KEYWORDS)


def listen_for_command(timeout=5, phrase_time_limit=5):
    """
    Listens via default microphone for a vocal distress command.
    Returns (command_text, is_distress).
    """
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.6)
            print("🎤 Listening for distress command...")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        
        command = recognizer.recognize_google(audio).lower()
        print("Recognized audio:", command)
        is_distress = check_distress_phrase(command)
        return command, is_distress
    except sr.WaitTimeoutError:
        return "", False
    except sr.UnknownValueError:
        return "", False
    except sr.RequestError as exc:
        print(f"Speech recognition service error: {exc}")
        return "", False
    except (OSError, AttributeError, Exception) as exc:
        print(f"Microphone or PyAudio error: {exc}")
        return "", False
