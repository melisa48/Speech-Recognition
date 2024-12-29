import speech_recognition as sr
import time
from datetime import datetime

class LanguageManager:
    def __init__(self):
        self.languages = {
            '1': {'code': 'en-US', 'name': 'English'},
            '2': {'code': 'tr-TR', 'name': 'Turkish'},
            '3': {'code': 'es-ES', 'name': 'Spanish'},
            '4': {'code': 'fr-FR', 'name': 'French'},
            '5': {'code': 'de-DE', 'name': 'German'},
            '6': {'code': 'ja-JP', 'name': 'Japanese'}
        }
        self.current_language = self.languages['1']

    def change_language(self):
        print("\nAvailable languages:")
        for key, lang in self.languages.items():
            print(f"{key}. {lang['name']} ({lang['code']})")
        
        while True:
            choice = input("\nEnter number for desired language (1-6) or 'c' to cancel: ")
            if choice.lower() == 'c':
                print(f"\nKeeping current language: {self.current_language['name']}")
                return
            
            if choice in self.languages:
                self.current_language = self.languages[choice]
                print(f"\nLanguage changed to: {self.current_language['name']}")
                return
            print("Invalid choice. Please try again.")

def test_microphone():
    """Test microphone levels and sensitivity"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nTesting microphone...")
        print("Please speak for 5 seconds...")
        audio = recognizer.listen(source, timeout=5)
        try:
            energy = audio.frame_data.__len__()
            print(f"Microphone energy level: {energy}")
            if energy < 100000:
                print("Warning: Microphone input level seems low")
                print("Tips: Speak closer to the microphone or increase microphone volume")
            else:
                print("Microphone level seems good")
        except Exception as e:
            print(f"Error testing microphone: {e}")
    return recognizer

def listen_and_recognize(lang_manager, recognizer=None):
    """
    Function to capture audio from microphone and convert it to text
    Parameters:
        lang_manager: LanguageManager instance handling language settings
        recognizer: Optional pre-configured recognizer instance
    Returns:
        The recognized text or error message
    """
    if recognizer is None:
        recognizer = sr.Recognizer()
    
    # More sensitive recognition parameters
    recognizer.energy_threshold = 300  # Lower threshold for better sensitivity
    recognizer.dynamic_energy_threshold = True
    recognizer.dynamic_energy_adjustment_damping = 0.15
    recognizer.dynamic_energy_ratio = 1.5
    recognizer.pause_threshold = 0.5  # Shorter pause threshold
    
    with sr.Microphone() as source:
        print("\nAdjusting for ambient noise... Please wait...")
        recognizer.adjust_for_ambient_noise(source, duration=3)  # Longer adjustment period
        
        print(f"\nListening... Speak now! (Language: {lang_manager.current_language['name']})")
        print("Commands:")
        print("- Press 'l' + Enter to change language")
        print("- Press 'q' + Enter to quit")
        print("- Press 't' + Enter to test microphone")
        
        try:
            # Check for keyboard input
            user_input = input("")
            if user_input.lower() == 'l':
                return "CHANGE_LANGUAGE"
            if user_input.lower() == 'q':
                return "QUIT"
            if user_input.lower() == 't':
                return "TEST_MIC"
            
            print("Listening for speech...")
            audio = recognizer.listen(source, timeout=7, phrase_time_limit=7)
            print("Processing speech...")
            
            # Try multiple recognition attempts with different sensitivity
            try:
                text = recognizer.recognize_google(audio, language=lang_manager.current_language['code'])
            except sr.UnknownValueError:
                # If first attempt fails, try with adjusted parameters
                recognizer.energy_threshold = 200  # Even lower threshold
                try:
                    text = recognizer.recognize_google(audio, language=lang_manager.current_language['code'])
                except sr.UnknownValueError:
                    return "Could not understand the audio. Tips:\n- Speak closer to the microphone\n- Speak more clearly\n- Press 't' to test microphone"
            
            result = f"You said: {text}"
            
            # Save transcription with debug info
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("transcriptions.txt", "a", encoding="utf-8") as file:
                file.write(f"[{timestamp}] ({lang_manager.current_language['code']}) {text}\n")
            
            return result
            
        except sr.WaitTimeoutError:
            return "No speech detected. Press 'l' to change language or try speaking again."
        except sr.RequestError as e:
            return f"Error: {e}. Please check your internet connection."

def main():
    """
    Main function to run the speech recognition program
    """
    print("\nEnhanced Multilingual Speech Recognition Program")
    print("---------------------------------------------")
    print("Commands:")
    print("- Press 'l' + Enter to change language")
    print("- Press 'q' + Enter to quit")
    print("- Press 't' + Enter to test microphone")
    print("- Press Ctrl+C to exit anytime")
    
    lang_manager = LanguageManager()
    recognizer = test_microphone()  # Initial microphone test
    
    while True:
        try:
            result = listen_and_recognize(lang_manager, recognizer)
            
            if result == "CHANGE_LANGUAGE":
                lang_manager.change_language()
                continue
            
            if result == "QUIT":
                print("\nExiting program...")
                break
                
            if result == "TEST_MIC":
                recognizer = test_microphone()
                continue
                
            print("\n" + result + "\n")
            
        except KeyboardInterrupt:
            print("\nExiting program...")
            break

if __name__ == "__main__":
    main()