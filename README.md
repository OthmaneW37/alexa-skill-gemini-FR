# Alexa Skill with Gemini Pro - French Version

This repository contains the complete source code for an Alexa skill that integrates with Google's Gemini Pro API. This skill allows you to have a powerful conversational assistant, capable of answering a wide range of questions, directly on your Alexa devices.

This project has been corrected, improved, and is ready for deployment.

## Features

-   **Conversational AI**: Interact with the powerful Gemini Pro model.
-   **Robust Error Handling**: The skill is designed to handle errors gracefully.
-   **Easy to Deploy**: Follow the steps below to get your skill up and running in minutes.
-   **Bilingual Support**: Configured for French (`fr-FR`) and English (`en-US`), with French as the primary language.

## Prerequisites

Before you begin, you will need:

1.  **An Amazon Developer Account**: To create the Alexa skill.
2.  **An AWS Account**: To host the Lambda function that will run the skill's backend.
3.  **A Google Cloud Platform (GCP) Account**: To obtain a Gemini API key.
    -   **Important**: You must have an active billing account on GCP for the API key to work. The free tier is generous, but a valid payment method is required.

---

## Step-by-Step Installation

### Step 1: Get a Google Gemini API Key

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project or select an existing one.
3.  Enable the **"Vertex AI API"** for your project.
4.  Go to **Credentials** and create a new **API Key**.
5.  **Copy this key securely**. You will need it in the next steps.

### Step 2: Configure the Lambda Function on AWS

1.  **Clone this repository**:
    ```bash
    git clone https://github.com/OthmaneW37/alexa-skill-gemini-FR.git
    cd alexa-skill-gemini-FR
    ```

2.  **Prepare the deployment package**:
    -   Navigate to the `lambda` directory.
    -   Install the dependencies in a new `package` directory:
        ```bash
        pip install -r requirements.txt -t ./package
        ```
    -   Copy the content of the `lambda` directory into the `package` directory:
        ```bash
        cp lambda_function.py utils.py ./package/
        ```
    -   Create a ZIP file from the `package` directory's content:
        ```bash
        cd package
        zip -r ../lambda_deployment_package.zip .
        ```

3.  **Create the Lambda Function**:
    -   Go to the [AWS Lambda Console](https://console.aws.amazon.com/lambda/).
    -   Click **"Create function"**.
    -   Select **"Author from scratch"**.
    -   **Function name**: `alexa-skill-gemini-fr` (or a name of your choice).
    -   **Runtime**: **Python 3.9** (or a more recent version).
    -   **Architecture**: `x86_64`.
    -   Click **"Create function"**.

4.  **Upload the code and configure the environment**:
    -   In the **"Code source"** section, click **"Upload from"** and select **".zip file"**. Upload the `lambda_deployment_package.zip` file you created.
    -   Go to the **"Configuration"** tab, then **"Environment variables"**.
    -   Add a new variable:
        -   **Key**: `GOOGLE_API_KEY`
        -   **Value**: *Paste the Gemini API key you obtained earlier.*

5.  **Add the Alexa Trigger**:
    -   In the function's overview, click **"Add trigger"**.
    -   Select **"Alexa Skills Kit"**.
    -   You will need to provide your Skill ID later. You can leave this for now and come back to it.
    -   Copy the **ARN** of your Lambda function (at the top right). You will need it for the Alexa skill configuration.

### Step 3: Create the Alexa Skill

1.  Go to the [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask).
2.  Click **"Create Skill"**.
3.  **Skill name**: "Assistant Gemini".
4.  **Primary locale**: French (France).
5.  **Choose a model**: **Custom**.
6.  **Choose a method to host**: **Provision your own**.
7.  Click **"Create Skill"**.

8.  **Configure the Endpoint**:
    -   Go to the **"Endpoint"** section.
    -   Select **"AWS Lambda ARN"**.
    -   Paste the ARN of your Lambda function in the **"Default Region"** field.

9.  **Build the Interaction Model**:
    -   Go to the **"Interaction Model"** section, then **"JSON Editor"**.
    -   Drag and drop the `interactionModels/custom/fr-FR.json` file from this repository into the editor.
    -   Click **"Save Model"**, then **"Build Model"**. This may take a few minutes.

### Step 4: Test Your Skill

1.  In the Alexa Developer Console, go to the **"Test"** tab.
2.  Enable testing for **"Development"**.
3.  You can now interact with your skill:
    -   **Start the skill**: "Ouvre mon assistant" (or the invocation name you chose).
    -   **Ask a question**: "explique-moi la a a théorie de la relativité".

Congratulations! Your Alexa skill powered by Gemini is now functional.

---

## Troubleshooting

### `Erreur Google : 404` dans la console de test Alexa

C'est l'erreur la plus courante et elle indique presque toujours un problème avec votre **clé API Google**. Voici comment la résoudre :

1.  **Vérifiez la clé API** :
    *   Assurez-vous que la clé que vous avez copiée dans la variable d'environnement `GOOGLE_API_KEY` de votre fonction Lambda est **exactement** la même que celle de votre console Google Cloud. Il ne doit y avoir aucun caractère manquant ou supplémentaire.

2.  **Activez la bonne API** :
    *   Dans votre projet Google Cloud, vérifiez que l'**"API Vertex AI"** est bien activée. Si elle ne l'est pas, la clé ne sera pas autorisée à effectuer des appels.

3.  **Vérifiez les restrictions de la clé API** :
    *   Dans la console Google Cloud, sous **"Identifiants"**, vérifiez si votre clé API a des restrictions (par exemple, limitée à certaines adresses IP ou à des referrers HTTP).
    *   Pour un environnement Lambda, il est souvent plus simple de n'avoir **aucune restriction**. Pour les tests, supprimer les restrictions est le moyen le plus rapide de confirmer si c'est la source du problème.

4.  **Compte de facturation** :
    *   L'accès à l'API Gemini nécessite un **compte de facturation actif** associé à votre projet Google Cloud, même si vous êtes dans les limites du niveau gratuit. Assurez-vous d'avoir un moyen de paiement valide configuré.

### Le déploiement échoue dans la console Alexa

Si votre code ne se déploie pas après avoir modifié le fichier `lambda/requirements.txt`, c'est probablement parce que l'environnement de déploiement d'Alexa Skills Kit est très strict.

*   **Solution** : N'ajoutez pas de bibliothèques complexes comme `google-generativeai`. Le projet est conçu pour fonctionner avec la bibliothèque `requests`, qui est fiable. Tenez-vous-en au fichier `requirements.txt` fourni.
