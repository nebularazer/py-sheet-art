# py-sheet-art

generates a google sheet from an image

## creating oauth credentials

0. Create a project at console.developers.google.com
1. Enable API Access for a Project if you haven’t done it yet.
2. Go to “APIs & Services > OAuth Consent Screen.” Click the button for “Configure Consent Screen” and follow the directions to give your app a name; you don’t need to fill out anything else on that screen. Click Save.
3. Go to “APIs & Services > Credentials”
4. Click “+ Create credentials” at the top, then select “OAuth client ID”.
5. Select “Desktop app”, name the credentials and click “Create”. Click “Ok” in the “OAuth client created” popup.
6. Download the credentials by clicking the Download JSON button in “OAuth 2.0 Client IDs” section.
7. Save the downloaded file as credentials.json.

## usage
```bash 
# install dependencies using poetry
poetry install
# run
python main.py image1.jpg image2.png ...
```
