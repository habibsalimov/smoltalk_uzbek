Get started
You can use TranslationLLM through the Cloud Translation API, with the TextTranslation request by specifying the modelID “translation-llm”. This works with our terminology control (such as company product names) through the Glossary feature, and can model outputs to be customized through our Adaptive Translation feature.

Before you begin
You must enable the Cloud Translation API for your project. For more information on enabling APIs, see the Service Usage documentation.

For more information on getting set up on Google Cloud, see Get set up on Google Cloud.

Try Translation LLM
In AI Studio
To use TranslationLLM in Vertex AI Studio, click Open Vertex AI Studio, and select the translation task in the left hand navigation.

For the most feature support on translation use cases, Use the Translation API - Advanced edition.

In API (Translation)
For translations, the input can be plain text or HTML. Cloud Translation API doesn't translate any HTML tags in the input, only text that appears between the tags. The output retains the (untranslated) HTML tags, with the translated text between the tags to the extent possible due to differences between the source and target languages.

Before trying this sample, follow the Python setup instructions in the Cloud Translation quickstart using client libraries. For more information, see the Cloud Translation Python API reference documentation.

To authenticate to Cloud Translation, set up Application Default Credentials. For more information, see Set up authentication for a local development environment.

You can specify which model to use for translation by using the model query parameter.

To use the translation LLM, specify general/translation-llm as the model ID.
from google.cloud import translate

def translate_text_with_model(
    text: str = "YOUR_TEXT_TO_TRANSLATE",
    project_id: str = "YOUR_PROJECT_ID",
    model_id: str = "YOUR_MODEL_ID",
) -&gt; translate.TranslationServiceClient:
    """Translates a given text using Translation custom model."""


    client = translate.TranslationServiceClient()


    location = "us-central1"
    parent = f"projects/{project_id}/locations/{location}"
    model_path = f"{parent}/models/{model_id}"


    # Supported language codes: https://cloud.google.com/translate/docs/languages
    response = client.translate_text(
        request={
            "contents": [text],
            "target_language_code": "ja",
            "model": model_path,
            "source_language_code": "en",
            "parent": parent,
            "mime_type": "text/plain",  # mime types: text/plain, text/html
        }
    )
    # Display the translation for each input text provided
    for translation in response.translations:
        print(f"Translated text: {translation.translated_text}")


    return response

    For using TranslationLLM with the Glossary feature on Translation API, see documentation.

In Vertex API
Use the Vertex AI API and translation LLM to translate text.

Before trying this sample, follow the Python setup instructions in the Cloud Translation quickstart using client libraries. For more information, see the Cloud Translation Python API reference documentation. To authenticate to Cloud Translation, set up Application Default Credentials. For more information, see Set up authentication for a local development environment.

from google.cloud import aiplatform

def translate():
  # Create a client
  endpoint = aiplatform.Endpoint('projects/PROJECT_ID/locations/LOCATION/publishers/google/models/cloud-translate-text')
  # Initialize the request
  instances=[{
      "source_language_code": 'SOURCE_LANGUAGE_CODE',
      "target_language_code": 'TARGET_LANGUAGE_CODE',
      "contents": ["SOURCE_TEXT"],
      "model": "projects/PROJECT_ID/locations/LOCATION/models/general/translation-llm"
  }]
  # Make the request
  response = endpoint.predict(instances=instances)
  # Handle the response
  print(response)

  For more information, see documentation.

Try Adaptive Translation (TranslationLLM with output customization)
In AI Studio
In Google cloud console, open Vertex AI Studio, and select the translation task in the left hand navigation, once in the translation task view, select in the model field, select TranslationLLM, and next to the language pair, select Add Examples.

Note: Examples must be submitted in the form of parallel sentences in the source and target language that represents the ideal translation result, eg.; “The quick brown fox jumps over the lazy dog. ; El veloz zorro marrón salta sobre el perro perezoso. And should include at least 5 sentence pairs, and up to 10k sentences in the file.

In API (Translation)
For more information, see documentation.

Language support
The most updated list is listed in our documentation

