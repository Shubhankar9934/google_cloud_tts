from google.cloud import texttospeech
from pydub import AudioSegment
import os
import glob

# Initialize Text-to-Speech client
client = texttospeech.TextToSpeechClient()

# Define the conversation
conversation = [
    ("Agent", "Hello! Thank you for reaching out to ABC Corp. today. My name is Michael. How can I assist you with your account today?"),
    ("Customer", "Hi, I’m calling because I’m struggling to keep up with my payments, and I’m not sure what to do."),
    ("Agent", "I’m really sorry to hear that you’re going through this, and I want to make sure we find a solution that works for you. Let’s take a look at your account and see what options are available. Can I please confirm your full name and the last four digits of your account number to get started?"),
    ("Customer", "Sure, my name is Daniel Jane and the last four digits are 1234."),
    ("Agent", "Thank you for confirming that. I’ve pulled up your account, and I see that you have an outstanding balance of [Amount Due]. I know this situation can be stressful, but I’m confident we can work together to get things back on track."),
    ("Customer", "Yeah, it’s been tough. I just lost my job recently, so it’s hard to make the payments."),
    ("Agent", "I completely understand, and I want you to know that we’re here to help. It's great that you’ve reached out today. Let’s explore some options that could make it easier for you. I see you qualify for a 3 Pay plan, where we can break the balance into three manageable payments. Would that be something you’re interested in?"),
    ("Customer", "That sounds like a good option, but I’m not sure if I can even afford that right now."),
    ("Agent", "I understand your concerns. We can work with you to adjust the payments if needed, and we’ll make sure there are no additional fees or charges if we get things set up today. Our goal is to make it easier for you to stay current and avoid any further stress down the line. Let’s start with the 3 Pay plan, and we can adjust from there if necessary. Does that sound like a plan?"),
    ("Customer", "Okay, I think I can make that work. How do I get started?"),
    ("Agent", "Great! We’ll start by scheduling your first payment for [Date]. I’ll just need to confirm a few details before we proceed. Would you like to make the payment now over the phone? We accept payments through credit card or direct bank transfer. I recommend using the phone option because it’s quick and secure."),
    ("Customer", "I’d prefer to use my bank account. Can we do that?"),
    ("Agent", "Of course! I can help you set that up right now. I’ll guide you through the process step by step. Once we process the first payment, we’ll confirm the schedule for the remaining two payments."),
    ("Customer", "That works for me."),
    ("Agent", "Excellent! Let’s move forward. I’ll process your first payment now, and you’ll receive a confirmation email shortly. Just to recap, we’ve set up the 3 Pay plan, starting with the first payment on [Date], and the other two payments will follow on [Dates]. I’ll also send you a confirmation with the payment details."),
    ("Customer", "Got it. Thank you for your help!"),
    ("Agent", "You’re very welcome! I’m really glad we could find a solution that works for you. To make sure everything goes smoothly, I’ll also double-check your contact details. Is this still your current phone number and email address? [Verify Contact Information]"),
    ("Customer", "Yes, that’s correct."),
    ("Agent", "Great! We’ve got everything updated. Just to summarize: your 3 Pay plan is set up, and your first payment will be processed today. You’ll receive confirmation shortly, and we’ll check in with you before the next payments are due. If anything changes, or if you need further assistance, don’t hesitate to reach out."),
    ("Customer", "Thank you again. I really appreciate it!"),
    ("Agent", "It was my pleasure. We’re here to support you every step of the way. Have a great day, and take care!")
]




def synthesize_text(text, speaker, line_num):
    # Prepare the SSML input
    ssml_text = f"<speak>{text}</speak>"
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)

    # Select voice parameters
    if speaker == "Agent":
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Neural2-J",
            ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=1.0,
            pitch=0.0
        )
    else:
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Neural2-F",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=1.0,
            pitch=0.0
        )

    # Synthesize speech
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    # Save audio to WAV file
    filename = f"{line_num:02d}_{speaker}.wav"
    with open(filename, "wb") as out:
        out.write(response.audio_content)
    print(f"Generated {filename}")

# Generate audio files
line_num = 1
for speaker, text in conversation:
    synthesize_text(text, speaker, line_num)
    line_num += 1

# Load background noise
background = AudioSegment.from_file("background_noise.wav")
background = background - 20  # Reduce background noise volume

# Initialize conversation audio
conversation_audio = AudioSegment.empty()

# Combine audio files with effects
for i in range(1, line_num):
    for speaker in ["Agent", "Customer"]:
        filename = f"{i:02d}_{speaker}.wav"
        if os.path.exists(filename):
            audio = AudioSegment.from_wav(filename)
            # Apply telephone effect
            audio = audio.low_pass_filter(3400).high_pass_filter(300)
            # Adjust volume
            if speaker == "Agent":
                audio = audio - 1.0
            else:
                audio = audio + 1.0
            # Add to conversation
            conversation_audio += audio + AudioSegment.silent(duration=500)

# Overlay background noise onto the conversation
# Ensure background is long enough
if len(background) < len(conversation_audio):
    # Loop the background to match the length
    loops = int(len(conversation_audio) / len(background)) + 1
    background = background * loops
    background = background[:len(conversation_audio)]

combined = conversation_audio.overlay(background)

# Export the final audio
combined.export("full_conversation_with_noise.wav", format="wav")
print("Full conversation with background noise saved as full_conversation_with_noise.wav")

# Clean up individual audio files
files = glob.glob('*.wav')
for f in files:
    if f != 'full_conversation_with_noise.wav':
        os.remove(f)
print("Cleaned up individual audio files.")
