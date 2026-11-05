from ac_dpi_pilot.config import settings
from ac_dpi_pilot.ollama_client import OllamaClient


def main():

    print("=" * 55)
    print("OLLAMA ENVIRONMENT CHECK")
    print("=" * 55)

    client = OllamaClient()

    print("\nConfigured service:")
    print(settings.ollama_base_url)

    try:

        installed_models = client.list_models()

    except Exception as error:

        print("\nOllama connection failed.")
        print(type(error).__name__, str(error))

        return

    print("\nInstalled models:")

    for model in installed_models:

        print("-", model)

    print("\nRequired models:")

    for model in settings.models:

        status = (
            "INSTALLED"
            if model in installed_models
            else "NOT INSTALLED"
        )

        print(f"{model}: {status}")


if __name__ == "__main__":
    main()
