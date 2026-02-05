from dotenv import load_dotenv
from imagekitio import ImageKit
import os

# look for presence of .env file
load_dotenv()

imagekit = ImageKit(
    # find the environment variables and load into c
    private_key=os.getenv("IMAGEKIT_PRIVATE_KEY"),
    public_key=os.getenv("IMAGEKIT_PUBLIC_KEY"),
    url_endpoint=os.getenv("IMAGEKIT_URL")
)