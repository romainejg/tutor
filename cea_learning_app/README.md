# CEA Learning App

A Streamlit MVP for daily scenario-based Controlled Environment Agriculture (CEA) practice.

## Features

- Role-specific practice for **Plant Scientist**, **Product Developer**, and **Grower**
- Dynamic scenario generation, evaluation, and tutoring
- SQLite persistence for attempts, scores, concept mastery, and daily recommendation
- Adaptive recommendation engine prioritizing weak concepts
- Deterministic **Mock/Demo mode** when no API key is set

## Tech Stack

- Python 3.10+
- Streamlit
- SQLite
- OpenAI Python SDK v1+
- pandas
- python-dotenv

## Project Structure

```text
cea_learning_app/
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── README.md
├── core/
├── data/
└── prompts/
```

## Setup

1. Create and activate a virtual environment:
   - macOS/Linux:
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     ```
   - Windows:
     ```powershell
     python -m venv .venv
     .venv\Scripts\activate
     ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment:
   ```bash
   cp .env.example .env
   ```
   Then add your `OPENAI_API_KEY`.
4. Run app:
   ```bash
   streamlit run app.py
   ```

## API Key and Mock Mode

`config.py` loads API key in this order:
1. `os.getenv("OPENAI_API_KEY")`
2. `st.secrets["OPENAI_API_KEY"]`

If key is missing, app automatically runs in deterministic mock mode for:
- Scenario generation
- Response evaluation
- Tutor feedback

Mock scenario is an Intermediate Plant Scientist case on inner-leaf tipburn with:
- EC 1.8
- pH 5.8
- Temperature shift from 20°C to 24°C
- High overnight humidity

## Curriculum Framework

Each role has 5 modules and multiple concepts, initialized in `core/curriculum.py` and seeded into SQLite by `DatabaseManager`.

## Adaptive Rules (MVP)

Implemented in `core/adaptive_engine.py`:
- If overall score is high across recent attempts, increase mastery.
- If score is low (`<70`) or concept is repeatedly missed, decrease/hold mastery.
- Daily recommendation prioritizes weak concepts first.

## Architecture

- `OpenAIService` centralizes all OpenAI API and mock JSON behavior
- `ScenarioGenerator`, `ResponseEvaluator`, and `Tutor` depend on `OpenAIService`
- `LearningSession` coordinates full flow:
  scenario → response → evaluation → tutor feedback → adaptive update

## Data Model and Persistence

Tables are auto-created in `data/app.db` on startup:
- roles
- modules
- concept_mastery
- scenarios
- responses
- evaluations
- tutor_feedback
- daily_recommendations

JSON fields are serialized with `json.dumps()` and loaded with `json.loads()`.

## Future Extensions

- Scenario deduplication and richer spaced repetition policy
- Better analytics and longitudinal streak tracking
- Multi-user support and auth
- Exportable learner reports
