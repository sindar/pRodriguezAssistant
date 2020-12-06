import os, requests, time, sys
import subprocess

class AzureTTS:
    def __init__(self, keys_path):
        self.keys_path = keys_path
        self.subscription_key = self.__read_subscription_key()
        self.access_token = self.__get_token(self.subscription_key)

    def __read_subscription_key(self):
        service_region = "northeurope"
        subscription_key = None

        try:
            with open(self.keys_path + '/subscription-'+ service_region + '.key') as key_file:
                    subscription_key = key_file.read().rstrip('\n\r')
        except:
            print("Error reading subscription key file!")

        if subscription_key is None:
            print("Subscription key is empty!")

        return subscription_key

    def __get_token(self, subscription_key):
        access_token = None
        fetch_token_url = 'https://northeurope.api.cognitive.microsoft.com/sts/v1.0/issueToken'
        headers = {
            'Ocp-Apim-Subscription-Key': subscription_key
        }
        response = requests.post(fetch_token_url, headers=headers)
        access_token = str(response.text)
        return access_token

    def text_to_speech(self, sentence):
        if self.subscription_key == None:
            self.subscription_key = self.__read_subscription_key()        
        if self.subscription_key != None and self.access_token == None:
            self.access_token = self.__get_token(self.subscription_key)

        if self.subscription_key == None or self.access_token == None:
            return None

        constructed_url = "https://northeurope.voice.speech.microsoft.com/cognitiveservices/v1?deploymentId=c418a752-7ca8-4f0d-9d4c-a17d59dd9a98"
        headers = {
            'Authorization': 'Bearer ' + str(self.access_token),
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'riff-16khz-16bit-mono-pcm',
            'User-Agent': 'Bender'
        }

        body = "<speak version=\"1.0\" xmlns=\"http://www.w3.org/2001/10/synthesis\" \
            xmlns:mstts=\"http://www.w3.org/2001/mstts\" \
            xml:lang=\"en-US\"><voice name=\"Bender\">"\
            + sentence + "</voice></speak>"   

        response = requests.post(constructed_url, headers=headers, data=body)
        if response.status_code == 200:
            temp_wav = '/dev/shm/azure_tts.wav'
            with open(temp_wav, 'wb') as audio:
                audio.write(response.content)
                print("\nStatus code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")
            return temp_wav
        else:
            print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
            return None