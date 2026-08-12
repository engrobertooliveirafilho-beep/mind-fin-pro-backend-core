from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from openai import OpenAI

from .config import BrainSettings


SYSTEM_PROMPT = """
Você é o núcleo de pesquisa e direção criativa da Eldora.

MISSÃO
Pesquisar tendências públicas atuais e criar decisões editoriais originais para a persona Eldora,
sem copiar criadores, sem repetir conteúdos, sem degradar a marca e sem alterar sua identidade visual.

ELDORA
Mulher digital brasileira, humana, próxima, elegante, disciplinada, inteligente e aspiracional sem ostentação vazia.
Pilares: evolução, rotina, estudo, saúde, finanças, trabalho, lifestyle, WhatsApp e construção do Grupo Eldora.

REGRAS
1. Baseie toda decisão em evidências atuais encontradas na web.
2. Cite URL e título das fontes.
3. Não trate popularidade como qualidade.
4. Não copie posts, legendas, enquadramentos ou identidade de pessoas específicas.
5. Não invente estatísticas.
6. Não use sexualização gratuita, polêmica artificial ou desinformação.
7. Preserve coerência com a Eldora.
8. Escolha ideias produzíveis por imagem e posteriormente por vídeo.
9. Cada decisão deve indicar exatamente o que variar: cena, roupa, cabelo, maquiagem, objeto, texto e CTA.
10. Rejeite tendências incompatíveis e explique o motivo.
11. Entregue JSON válido, sem markdown.
"""


def build_research_input(settings: BrainSettings) -> str:
    domains = ", ".join(settings.source_domains)
    return f"""
Pesquise tendências públicas recentes relevantes ao Brasil para conteúdo de Instagram, Facebook,
TikTok, YouTube Shorts, Pinterest e WhatsApp Status.

Mercado: {settings.market}
Localidade: {settings.locale}
Fontes prioritárias: {domains}

Investigue:
- formatos e narrativas em crescimento;
- cenas, roupas, cabelos, maquiagem, objetos e composições visuais;
- temas de estudo, rotina, saúde, finanças, empreendedorismo e lifestyle;
- datas, sazonalidade e assuntos oportunos;
- sinais de saturação e tendências que devem ser rejeitadas.

Crie no máximo {settings.max_decisions} decisões criativas.
Cada decisão deve ter confidence de 0 a 1 e somente decisões acima de
{settings.minimum_confidence} devem ser recomendadas.

Retorne exatamente este JSON:
{{
  "evidence": [
    {{
      "source_title": "...",
      "source_url": "...",
      "observation": "...",
      "relevance": 0.0,
      "freshness": "...",
      "category": "..."
    }}
  ],
  "decisions": [
    {{
      "content_id": "...",
      "objective": "...",
      "platform": "...",
      "format": "...",
      "scene": "...",
      "wardrobe": "...",
      "hair": "...",
      "makeup": "...",
      "prop": "...",
      "text_element": "...",
      "caption_angle": "...",
      "cta": "...",
      "evidence_refs": ["URL"],
      "confidence": 0.0,
      "status": "PLANNED"
    }}
  ],
  "rejected_trends": [
    {{
      "trend": "...",
      "reason": "..."
    }}
  ]
}}
"""


def research(settings: BrainSettings) -> dict[str, Any]:
    client = OpenAI()
    response = client.responses.create(
        model=settings.research_model,
        tools=[{"type": "web_search"}],
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_research_input(settings)},
        ],
    )

    text = response.output_text.strip()
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Pesquisa não retornou JSON válido: {exc}") from exc

    payload["_meta"] = {
        "researched_at_utc": datetime.now(timezone.utc).isoformat(),
        "model": settings.research_model,
        "market": settings.market,
        "locale": settings.locale,
    }
    return payload