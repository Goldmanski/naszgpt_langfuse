# NaszGPT

NaszGPT to aplikacja chatbotowa wykorzystująca modele językowe OpenAI. Aplikacja została zbudowana w Pythonie z wykorzystaniem Streamlit i umożliwia prowadzenie oraz zarządzanie rozmowami z chatbotem.

## Funkcjonalności

- prowadzenie rozmów z chatbotem,
- tworzenie nowych konwersacji,
- zapisywanie historii rozmów,
- przełączanie pomiędzy zapisanymi konwersacjami,
- definiowanie osobowości i sposobu zachowania chatbota,
- wykorzystanie modeli językowych OpenAI,
- monitorowanie wywołań modeli za pomocą Langfuse.

## Technologie

- **Python** – język programowania,
- **Streamlit** – interfejs użytkownika aplikacji,
- **OpenAI API** – komunikacja z modelem językowym,
- **Langfuse** – monitoring i obserwacja wywołań LLM,
- **python-dotenv** – zarządzanie zmiennymi środowiskowymi.

## Struktura projektu

```text
.
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Wymagania

Do uruchomienia projektu potrzebne są:

- Python 3.11 lub nowszy,
- klucz API OpenAI.

## Instalacja

### 1. Sklonowanie repozytorium

```bash
git clone https://github.com/Goldmanski/naszgpt_langfuse.git
cd naszgpt_langfuse
```

### 2. Utworzenie środowiska wirtualnego

```bash
python -m venv .venv
```

Aktywacja środowiska w systemie Windows:

```bash
.venv\Scripts\activate
```

### 3. Instalacja zależności

```bash
pip install -r requirements.txt
```

## Konfiguracja

Utwórz w głównym katalogu projektu plik `.env` i dodaj swój klucz API OpenAI:

```env
OPENAI_API_KEY=your_api_key
```

Plik `.env` jest wykluczony z repozytorium za pomocą `.gitignore` i nie powinien być publikowany.

## Uruchomienie

Uruchom aplikację za pomocą:

```bash
streamlit run app.py
```

Po uruchomieniu Streamlit udostępni aplikację lokalnie w przeglądarce.

## Langfuse

Projekt wykorzystuje Langfuse do monitorowania działania aplikacji i wywołań modeli językowych.

Integracja pozwala obserwować przebieg wywołań LLM oraz analizować ich działanie podczas korzystania z aplikacji.

## Status projektu

Projekt jest rozwijany w ramach nauki Data Science i AI Engineering.