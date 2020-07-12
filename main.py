from pathlib import Path
import pickle
import socket

import click
from PIL import Image
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

socket.setdefaulttimeout(300)  # 5 minutes (max upload timeout for BIG/multiple images)


def rgb_to_json(red: int, green: int, blue: int, alpha: float = 1.0):
    return {
        "userEnteredFormat": {
            "backgroundColor": {
                "red": round(red / 255.0, 3),
                "green": round(green / 255.0, 3),
                "blue": round(blue / 255.0, 3),
                "alpha": alpha,
            }
        }
    }


def pixelmap_to_row(pixelmap, width, row):
    result = []
    for i in range(width):
        try:
            r, g, b = pixelmap[i, row]
            a = 1.0
        except ValueError:
            r, g, b, a = pixelmap[i, row]
        result.append(rgb_to_json(r, g, b, a))

    return {"values": result}


def image_to_sheet(image):
    filepath = Path(image)
    original_image = Image.open(filepath)
    width, height = original_image.size

    if width > 256 or height > 256:
        confirm = click.confirm(
            f"Image {filepath.name} dimensions ({width}x{height}) is above the "
            "recommended limit of 256.\n"
            "This can result in a very big spreadsheet size with long loading times. \n"
            "Continue anyways?"
        )
    else:
        confirm = True

    if confirm:
        pixelmap = original_image.load()
        return {
            "properties": {"title": filepath.name},
            "data": [
                {
                    "startRow": 0,
                    "startColumn": 0,
                    "rowData": [
                        pixelmap_to_row(pixelmap, width, row) for row in range(height)
                    ],
                    "rowMetadata": [{"pixelSize": 1} for _ in range(height)],
                    "columnMetadata": [{"pixelSize": 1} for _ in range(width)],
                }
            ],
        }
    else:
        return None


@click.command()
@click.argument("images", nargs=-1)
def main(images):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if Path("token.pickle").exists():
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", ["https://www.googleapis.com/auth/spreadsheets"],
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("sheets", "v4", credentials=creds)

    spreadsheet_body = {
        "properties": {"title": "py-sheet-art"},
        "sheets": [image_to_sheet(image) for image in images if image is not None],
    }

    request = service.spreadsheets().create(body=spreadsheet_body)
    request.execute()


if __name__ == "__main__":
    main()
