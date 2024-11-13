from google.cloud import texttospeech
from pydub import AudioSegment
import os
import glob

# Initialize Text-to-Speech client
client = texttospeech.TextToSpeechClient()

conversation = [
    ("Agent", """
    <speak>
        Hello, thank you for calling ABC Corp.
        <break time="600ms"/>
        My name is John.
        <break time="400ms"/>
        How can I assist you today?
    </speak>
    """),
    ("Customer", """
    <speak>
        Hi, I’m calling 
        <break time="400ms"/>
        because I’ve missed a few payments and I’m not sure what to do next.
    </speak>
    """),
    ("Agent", """
    <speak>
        <prosody pitch="-1st" rate="medium">
            I can see your account has some missed payments.
        </prosody>
        Let me pull up the details.
        <break time="600ms"/>
        It looks like your current balance is <prosody pitch="+1st">$100.</prosody>
        <break time="600ms"/>
        I understand this can be concerning.
        Are you ready to discuss a way to bring your account current?
    </speak>
    """),
    ("Customer", """
    <speak>
        I’m not sure if I can pay the full amount right now.
        <break time="400ms"/>
        What can we do?
    </speak>
    """),
    ("Agent", """
    <speak>
        Well, you’re currently on the XYZ Plan,
        <break time="400ms"/>
        and it looks like you’re late on some payments.
        <break time="600ms"/>
        I need to collect the <prosody pitch="+1st">Total Minimum Due</prosody> today,
        <break time="400ms"/>
        and we may need to address the balance on the closed accounts as well.
        <break time="600ms"/>
        Let me be clear—your balance needs to be paid as soon as possible,
        <break time="400ms"/>
        or you risk further actions on your account.
    </speak>
    """),
    ("Customer", """
    <speak>
        I really don’t know if I can pay that amount right now.
    </speak>
    """),
    ("Agent", """
    <speak>
        <prosody pitch="-1st" rate="medium">
            Understandable.
        </prosody>
        I’m going to offer you a couple of solutions.
        <break time="600ms"/>
        You’re eligible for a <prosody pitch="+1st">Late Fee Waiver</prosody> and a <prosody pitch="+1st">Match-A-Pay</prosody> option.
        <break time="600ms"/>
        This means I can reduce some fees if we can settle a smaller portion now
        <break time="400ms"/>
        and schedule future payments for the rest.
        <break time="600ms"/>
        We can break it down into more manageable amounts if necessary.
    </speak>
    """),
    ("Customer", """
    <speak>
        That sounds like it might help,
        <break time="400ms"/>
        but I still don’t know if I can do it right now.
    </speak>
    """),
    ("Agent", """
    <speak>
        <prosody pitch="-1st" rate="medium">
            It’s critical that we get this resolved today.
        </prosody>
        <break time="600ms"/>
        If you can pay a portion of the Total Minimum Due now,
        <break time="400ms"/>
        I can set up a payment plan for the remaining balance.
        <break time="600ms"/>
        This will avoid any future penalties or further action on the account.
    </speak>
    """),
    ("Customer", """
    <speak>
        Okay, I think I can pay part of it now,
        <break time="400ms"/>
        but I need to know exactly what the next steps will be.
    </speak>
    """),
    ("Agent", """
    <speak>
        I’ll walk you through it.
        <break time="600ms"/>
        You’ll make a partial payment today—let’s say <prosody pitch="+1st">[Amount],</prosody>
        <break time="400ms"/>
        and I will set up a <prosody pitch="+1st">3-Pay plan</prosody> for the remaining balance.
        <break time="600ms"/>
        This will allow you to pay over three months.
        <break time="400ms"/>
        After this first payment, you will be on track to bring your account current and avoid additional fees.
    </speak>
    """),
    ("Customer", """
    <speak>
        Alright, that seems fair.
        <break time="400ms"/>
        Let’s proceed with that.
    </speak>
    """),
    ("Agent", """
    <speak>
        <prosody pitch="+1st" rate="medium">
            Excellent.
        </prosody>
        <break time="600ms"/>
        First, let me confirm your preferred payment method.
        <break time="400ms"/>
        Would you like to make the payment now by phone,
        <break time="600ms"/>
        or would you prefer another method?
    </speak>
    """),
    ("Customer", """
    <speak>
        I’ll do it over the phone now.
    </speak>
    """),
    ("Agent", """
    <speak>
        Great! 
        <break time="600ms"/>
        I’ll take care of that for you.
        <break time="400ms"/>
        Once we process this payment, I’ll send you a confirmation email with all the details,
        <break time="600ms"/>
        including your 3-Pay plan schedule.
        <break time="400ms"/>
        Is the payment information we have on file still correct,
        <break time="400ms"/>
        or do you need to update anything?
    </speak>
    """),
    ("Customer", """
    <speak>
        It’s correct.
    </speak>
    """),
    ("Agent", """
    <speak>
        Perfect! 
        <break time="600ms"/>
        I’m processing the payment now.
        <break time="400ms"/>
        Your first payment will be next month,
        <break time="600ms"/>
        and the next two payments will be scheduled three months after.
        <break time="600ms"/>
        You’ll also receive a confirmation email shortly,
        <break time="400ms"/>
        along with the payment schedule.
    </speak>
    """),
    ("Customer", """
    <speak>
        Thank you for making this easier.
    </speak>
    """),
    ("Agent", """
    <speak>
        <prosody pitch="+1st" rate="medium">
            You’re welcome.
        </prosody>
        <break time="600ms"/>
        Just to confirm:
        <break time="400ms"/>
        we’ve arranged for your partial payment today
        <break time="400ms"/>
        and scheduled the 3-Pay plan to help you get back on track.
        <break time="600ms"/>
        If anything changes or you need further assistance,
        <break time="400ms"/>
        don’t hesitate to reach out.
    </speak>
    """),
    ("Customer", """
    <speak>
        Thanks again. I appreciate the help.
    </speak>
    """),
    ("Agent", """
    <speak>
        <prosody pitch="+1st" rate="medium">
            It was my pleasure!
        </prosody>
        <break time="600ms"/>
        You’re all set, and we’re here to assist you whenever needed.
        <break time="400ms"/>
        Have a great day!
    </speak>
    """)
]







def synthesize_text(ssml_text, speaker, line_num):
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
            speaking_rate=0.95,
            pitch=-1.0
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
for speaker, ssml_text in conversation:
    synthesize_text(ssml_text, speaker, line_num)
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
