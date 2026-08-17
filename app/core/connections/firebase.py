import logging

import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

from app.core.settings import settings
from app.exceptions.firebase import (
    FirebaseConnectionException,
    FirebaseClientNotInitializedException,
)

firebase_app: firebase_admin.App | None = None
logger = logging.getLogger(__name__)


def connect_firebase() -> None:
    """
    Initialize the Firebase Admin SDK.

    This should be called when the application starts.
    """
    try:
        global firebase_app

        if firebase_app is not None:
            logger.info("Firebase is already initialized")
            return

        firebase_credentials = credentials.Certificate(
            settings.FIREBASE_CREDENTIALS_PATH
        )

        firebase_app = firebase_admin.initialize_app(
            firebase_credentials
        )

        logger.info("Firebase connection was successful")

    except Exception as e:
        logger.exception("Failed to connect to Firebase")
        raise FirebaseConnectionException from e


def get_firebase_app() -> firebase_admin.App:
    """
    Return the initialized Firebase application.
    """
    if firebase_app is None:
        logger.error("Firebase application has not been initialized")
        raise FirebaseClientNotInitializedException()

    return firebase_app


def get_firebase_messaging() -> messaging:
    """
    Return the Firebase Cloud Messaging module.

    Ensures Firebase has been initialized before FCM operations.
    """
    get_firebase_app()

    return messaging


def disconnect_firebase() -> None:
    """
    Delete the Firebase Admin SDK application.

    This should be called when the application shuts down.
    """
    try:
        global firebase_app

        if firebase_app is not None:
            firebase_admin.delete_app(firebase_app)
            firebase_app = None

            logger.info("Firebase connection was closed")

    except Exception as e:
        logger.exception("Failed to disconnect from Firebase")
        raise FirebaseConnectionException from e