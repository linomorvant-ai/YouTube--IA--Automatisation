import json
import os
from pathlib import Path
from openai import OpenAI
from config import settings

SYSTEM_PROMPT = """Tu es le directeur créatif d'une chaîne YouTube pour enfants.
Tu dois produire des histoires originales, cohérentes et adaptées à l'âge demandé.
N'utilise jamais de personnages, univers ou textes protégés comme s'ils étaient les nôtres.
Évite violence graphique, sexualisation, contenu dangereux, défis dangereux, haine,
insultes et informations inadaptées aux enfants.

Tu dois retourner UNIQUEMENT un JSON valide correspondant au schéma demandé.
Ne mets aucun markdown autour du JSON.
"""

class CreativeDirector:
    def __init__(self):
        self.provider = settings.llm_provider

        if self.provider == "openai":
            if not settings.openai_api_key:
                raise RuntimeError("OPENAI_API_KEY is missing.")
            self.client = OpenAI(api_key=settings.openai_api_key)

        elif self.provider == "pollinations":
            if not settings.pollinations_api_key:
                raise RuntimeError("POLLINATIONS_API_KEY is missing.")
            self.client = OpenAI(
                base_url="https://gen.pollinations.ai/v1",
                api_key=settings.pollinations_api_key,
            )
        else:
            raise RuntimeError(f"Unknown LLM_PROVIDER: {self.provider}")

    def _model(self):
        return settings.openai_model if self.provider == "openai" else settings.pollinations_text_model

    def _call_json(self, prompt):
        response = self.client.chat.completions.create(
            model=self._model(),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)

    def load_history(self):
        from db import get_recent_productions
        return get_recent_productions(limit=30)

    def create_production(self, history):
        history_text = json.dumps(history, ensure_ascii=False)
        prompt = f"""
Crée une production complète pour une vidéo YouTube Kids en {settings.language},
pour des enfants de {settings.target_age}, durée cible entre
{settings.video_duration_min} et {settings.video_duration_max} secondes.

Nombre de scènes : exactement {settings.scene_count}.

Historique des productions récentes :
{history_text}

Ne réutilise pas les mêmes intrigues ou titres récents.

La production doit contenir :
- title
- target_age
- duration_seconds
- style
- characters
- scenes
- thumbnail_prompt
- youtube

Pour chaque personnage, donne une character bible détaillée.
Pour chaque scène :
- id
- duration_seconds
- characters
- location
- action
- narration
- dialogue
- visual_prompt
- camera
- lighting
- style
- sound_effects
- music
- transition

Les prompts visuels doivent répéter les attributs importants des personnages
pour maximiser leur cohérence d'une scène à l'autre.

Le champ youtube doit contenir :
- title
- description
- tags

Le JSON doit être directement exploitable par un programme.
"""
        return self._call_json(prompt)
