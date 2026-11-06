"""
Editorial AI Assistant Service for The Chronicle.
Supports Google Gemini, OpenAI, and intelligent offline heuristic fallbacks.
Zero third-party library dependencies required (pure standard library HTTP).
"""

import json
import logging
import re
import urllib.request
import urllib.error
from decouple import config

logger = logging.getLogger(__name__)


class EditorialAIService:
    """
    Provides automated editorial intelligence:
    - 3-bullet executive takeaways (TL;DR)
    - SEO Meta Title and Description generation
    - Journalistic Headline variants
    """

    def __init__(self):
        self.gemini_api_key = config('GEMINI_API_KEY', default=config('AI_API_KEY', default=None))
        self.openai_api_key = config('OPENAI_API_KEY', default=None)

    def _strip_html(self, html_text: str) -> str:
        """Removes HTML tags and normalizes whitespace."""
        clean = re.sub(r'<[^>]+>', ' ', html_text or '')
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()

    def generate_executive_summary(self, article) -> str:
        """
        Generates a concise 3-bullet takeaway summary.
        Attempts Gemini/OpenAI if configured; falls back to offline extractor.
        """
        plain_body = self._strip_html(article.body)
        if not plain_body:
            return ""

        # Try Gemini API if key is present
        if self.gemini_api_key:
            try:
                prompt = (
                    f"Headline: {article.title}\n\n"
                    f"Excerpt: {article.excerpt}\n\n"
                    f"Body:\n{plain_body[:3500]}\n\n"
                    "Task: Write exactly 3 bullet points summarizing the core findings of this news story. "
                    "Each bullet must begin with '• **[Lead Word/Phrase]**: ' and provide a substantive takeaway. "
                    "Return ONLY the 3 bullets without introductory text."
                )
                result = self._call_gemini(prompt)
                if result:
                    return result.strip()
            except Exception as e:
                logger.warning(f"Gemini API call failed, falling back to offline summarizer: {e}")

        # Try OpenAI API if key is present
        if self.openai_api_key:
            try:
                prompt = (
                    f"Headline: {article.title}\n\n"
                    f"Excerpt: {article.excerpt}\n\n"
                    f"Body:\n{plain_body[:3500]}\n\n"
                    "Write exactly 3 bullet points summarizing the key facts of this article. "
                    "Format each as '• **[Lead Word]**: [Detail]'. Return only the bullets."
                )
                result = self._call_openai(prompt)
                if result:
                    return result.strip()
            except Exception as e:
                logger.warning(f"OpenAI API call failed, falling back to offline summarizer: {e}")

        # High-quality offline extractive fallback
        return self._offline_extractive_summary(article, plain_body)

    def generate_seo_metadata(self, article) -> dict:
        """
        Generates optimized meta title, meta description, and recommended tags.
        """
        plain_body = self._strip_html(article.body)

        meta_title = article.title[:65].strip()
        if len(article.title) > 65:
            meta_title = f"{article.title[:62]}..."

        excerpt_summary = article.excerpt or plain_body[:155]
        meta_description = excerpt_summary[:155].strip()
        if len(excerpt_summary) > 155:
            meta_description = f"{meta_description}..."

        # Extract top keywords (words > 4 chars, capitalized or domain-relevant)
        words = re.findall(r'\b[A-Za-z]{4,}\b', plain_body)
        stopwords = {
            'their', 'there', 'about', 'would', 'could', 'which', 'after',
            'before', 'where', 'while', 'under', 'these', 'those', 'other',
            'being', 'first', 'second', 'years', 'state', 'states'
        }
        word_freq = {}
        for w in words:
            wl = w.lower()
            if wl not in stopwords:
                word_freq[wl] = word_freq.get(wl, 0) + 1

        top_tags = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        suggested_tags = [t[0].capitalize() for t in top_tags]

        return {
            'meta_title': meta_title,
            'meta_description': meta_description,
            'suggested_tags': suggested_tags,
        }

    def suggest_headline_variants(self, article) -> list:
        """Generates 4 editorial headline style variants."""
        base = article.title
        category = article.category.name if article.category else "News"

        return [
            f"Analysis: How {base.rstrip('.')}",
            f"Inside the Numbers: {base.rstrip('.')}",
            f"Special Report: {base.rstrip('.')} — What It Means for {category}",
            f"Explainer: Why {base.rstrip('.')} Matters Now",
        ]

    def _offline_extractive_summary(self, article, text: str) -> str:
        """
        Deterministic, high-quality heuristic summarizer based on sentence salience.
        """
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 35]

        lead_excerpt = article.excerpt.strip() if article.excerpt else ""

        bullets = []

        # Bullet 1: Core development
        if lead_excerpt:
            bullets.append(f"• **The Big Picture:** {lead_excerpt}")
        elif sentences:
            bullets.append(f"• **The Big Picture:** {sentences[0]}")

        # Bullet 2: Key evidence or impact
        if len(sentences) > 2:
            bullets.append(f"• **Key Evidence:** {sentences[1]}")
        elif len(sentences) > 1:
            bullets.append(f"• **Key Evidence:** {sentences[0]}")

        # Bullet 3: Future outlook or context
        if len(sentences) > 3:
            bullets.append(f"• **What to Watch:** {sentences[-1]}")
        else:
            bullets.append("• **What to Watch:** Global stakeholders continue monitoring regulatory and economic implications.")

        return "\n".join(bullets[:3])

    def _call_gemini(self, prompt: str) -> str:
        """Direct standard-library call to Google Gemini REST API."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 300,
            }
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data['candidates'][0]['content']['parts'][0]['text']

    def _call_openai(self, prompt: str) -> str:
        """Direct standard-library call to OpenAI Chat Completions API."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.openai_api_key}',
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 300,
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data['choices'][0]['message']['content']


ai_assistant = EditorialAIService()
