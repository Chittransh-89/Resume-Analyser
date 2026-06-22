"""CareerBuddy AI Brain"""

from openai import OpenAI
from config2 import Config
from embeddings_store import EmbeddingsStore
from web_search import WebSearcher
import re

class CareerBuddyBrain:

    def __init__(self):
        Config.validate()
        self.client = OpenAI(
            api_key=Config.GITHUB_TOKEN,
            base_url=Config.GITHUB_BASE_URL,
        )
        self.model_name = Config.GITHUB_MODEL
        self.system_prompt = """You are CareerBuddy, a friendly tech career advisor.

LANGUAGE RULES:
- Default: English  
- Hindi only if explicitly asked

LINK HANDLING:
- You will receive SEARCH LINKS section with Google/YouTube search URLs
- These search URLs are VALID and SAFE to share with users
- Format them nicely: [🔍 Search Topic](url) or [📺 YouTube: Topic](url)
- Explain to user: "Ye link click karke latest results dekho"
- Use ONLY the URLs provided — NEVER invent URLs
- NEVER write: undefined / null / [url] / (link) / placeholder

RESPONSE STYLE:
- Clear and practical
- Bullets for lists  
- Emojis sparingly
- Mention that search links give LATEST results
"""

        self.web_triggers = [
        # High confidence - ye definitely search chahte hain
        "salary", "package", "ctc", "lpa",
        "hiring", "jobs", "openings", "vacancy",
        "trending", "demand", "market",
        "youtube", "video", "tutorial", "course",
        "free resources", "website",
        "find me", "look up", "search for",
        "companies hiring", "startups",
        "news", "update", "recent",
        "roadmap", "resources to learn",
        "how to become", "getting started",
        "playlist", "recommend", "suggest",
        "best way to learn", "free course",
        "projects for", "practice platform",
        
        # ❌ REMOVED - ye bahut generic the
        # "learn", "how to", "start", "free",
        # "online", "platform", "guide", "beginner",
        # "path", "books", "projects", "practice",
        # "search", "link", "recommend"
    ]

        print(f"🤖 Model loaded: {self.model_name}")
        print("🧠 Initializing knowledge base...")
        self.store = EmbeddingsStore()
        self.store.initialize()
        self.searcher = WebSearcher()
        self.chat_history = []
        print("✅ CareerBuddy ready!\n")

    # ══════════════════════════════════════
    def needs_web_search(self, query):
        q = query.lower().strip()
        
        # ✅ Pehle check - chhoti general queries skip karo
        skip_patterns = [
            "hi", "hello", "hey", "hii",
            "how are you", "what's up", "sup",
            "thanks", "thank you", "ok", "okay",
            "bye", "goodbye", "good morning",
            "good evening", "good night",
            "who are you", "what are you",
            "your name", "help", "what can you do",
        ]
        
        for skip in skip_patterns:
            if q == skip or q.startswith(skip):
                return False
        
        # ✅ Bahut chhoti query hai to search mat karo
        if len(q.split()) <= 3 and not any(t in q for t in ["salary", "jobs", "hiring", "roadmap"]):
            return False
        
        # ✅ Ab triggers check karo
        for t in self.web_triggers:
            if t in q:
                return True
        
        return False

    # ══════════════════════════════════════
    def get_context(self, user_query):
        return self.store.get_relevant_context(
            query=user_query,
            n_results=Config.MAX_SEARCH_RESULTS
        )

    # ══════════════════════════════════════
    def get_web_context(self, user_query):
        try:
            results = self.searcher.search_career_resources(user_query)

            web = (
                results.get("web") or
                results.get("organic") or
                results.get("results") or
                []
            )
            yt = (
                results.get("youtube") or
                results.get("videos") or
                []
            )

            context = ""

            if web:
                context += "\nSEARCH LINKS (use these as-is, they are valid Google/YouTube search pages):\n"
                for r in web:
                    title   = r.get("title") or r.get("name") or "Resource"
                    url     = r.get("url") or r.get("link") or r.get("href") or ""
                    snippet = r.get("snippet") or r.get("description") or r.get("body") or ""

                    if url and url.startswith("http"):
                        context += f"- {title}\n  URL: {url}\n  Info: {snippet}\n"

            if yt:
                context += "\nYOUTUBE SEARCH LINKS:\n"
                for v in yt:
                    title = v.get("title") or v.get("name") or "Video Search"
                    url   = v.get("url") or v.get("link") or v.get("href") or ""

                    if url and url.startswith("http"):
                        context += f"- {title}\n  URL: {url}\n"

            print(f"📝 Web context:\n{context[:500]}")
            return context.strip()

        except Exception as e:
            print(f"❌ Web error: {e}")
            import traceback
            traceback.print_exc()
            return ""

    # ══════════════════════════════════════
    def build_messages(self, user_query, rag_context, web_context=""):
        combined = f"RAG:\n{rag_context}"

        if web_context:
            combined += f"""

    ═══ SEARCH LINKS (VERIFIED) ═══
    {web_context}
    ════════════════════════════════

    IMPORTANT RULES FOR LINKS:
    1. Upar diye gaye URLs Google/YouTube SEARCH pages hain — ye 100% valid hain
    2. In URLs ko EXACTLY as-is use karo (copy-paste karo)
    3. Format: [🔍 Search: Topic Name](URL) ya [📺 Watch on YouTube](URL)
    4. Ye search links user ko latest results dikhayenge — isliye helpful hain
    5. NEVER write: undefined / null / [url] / placeholder
    6. Apne aap se koi URL mat banao — sirf upar wale use karo

    EXAMPLE GOOD RESPONSE:
    ✅ Python sikhne ke liye:
    - [🔍 Best Python Tutorials](https://www.google.com/search?q=best+python+tutorials)
    - [📺 Python Course on YouTube](https://www.youtube.com/results?search_query=python+course)

    EXAMPLE BAD RESPONSE:
    ❌ Python Course: undefined
    ❌ [Click Here](placeholder)
    """
        else:
            combined += """

    NO WEB DATA AVAILABLE:
    - Koi URL mat likho
    - Plain text mein resource names suggest karo
    - User ko bolo "Google par search karo" but link mat banao
    - undefined / null BANNED hai
    """

        messages = [{
            "role": "system",
            "content": f"{self.system_prompt}\n\nCONTEXT:\n{combined}"
        }]

        if self.chat_history:
            messages.extend(self.chat_history[-6:])

        messages.append({"role": "user", "content": user_query})
        return messages

    # ══════════════════════════════════════
    def chat(self, user_query, use_web_search=None):
        try:
            rag_context = self.get_context(user_query)
            web_context = ""

            should_search = (
                use_web_search if use_web_search is not None
                else self.needs_web_search(user_query)
            )

            if should_search:
                print(f"🌐 Web search: {user_query}")
                web_context = self.get_web_context(user_query)

            messages = self.build_messages(user_query, rag_context, web_context)

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=Config.TEMPERATURE,
                max_tokens=Config.MAX_TOKENS,
            )

            answer = response.choices[0].message.content
            answer = self._clean_response(answer)

            self.chat_history.append({"role": "user", "content": user_query})
            self.chat_history.append({"role": "assistant", "content": answer})

            if len(self.chat_history) > Config.MAX_CHAT_HISTORY:
                self.chat_history = self.chat_history[-Config.MAX_CHAT_HISTORY:]

            # ✅ Links context se nikalo, answer se nahi
            all_links   = self._extract_web_links(web_context)
            yt_links    = self._extract_youtube_links(web_context)
            google_links = [l for l in all_links if "google.com" in l]
            
            # ✅ Debug
            print(f"🔗 Google links: {len(google_links)}")
            print(f"🎥 YT links:     {len(yt_links)}")

            return {
                "response"       : answer,
                "used_web_search": should_search,
                "google_links"   : google_links,   # ✅ alag key
                "youtube_links"  : yt_links        # ✅ alag key
            }

        except Exception as e:
            return {
                "response"       : f"❌ Error: {str(e)}",
                "used_web_search": False,
                "google_links"   : [],
                "youtube_links"  : []
            }

    # ══════════════════════════════════════
    def _clean_response(self, text):
        """undefined/null links remove karo"""

        # [Text](undefined) → Text
        text = re.sub(r'\[([^\]]+)\]\(undefined\)', r'\1', text)

        # [Text](null) → Text
        text = re.sub(r'\[([^\]]+)\]\(null\)', r'\1', text)

        # [Text]() → Text
        text = re.sub(r'\[([^\]]+)\]\(\s*\)', r'\1', text)

        # Bare undefined / null words
        text = re.sub(r'\bundefined\b', '', text)
        text = re.sub(r'\bnull\b', '', text)

        # Extra blank lines clean karo
        text = re.sub(r'\n{3,}', '\n\n', text)

        print("✅ Response cleaned")
        return text.strip()

    # ══════════════════════════════════════
    def _extract_youtube_links(self, text):
        """YouTube links extract karo - search + direct dono"""
        if not text:
            return []

        patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',           # direct video
            r'https?://youtu\.be/[\w-]+',                                  # short link
            r'https?://(?:www\.)?youtube\.com/playlist\?list=[\w-]+',     # playlist
            r'https?://(?:www\.)?youtube\.com/results\?search_query=[\w%+.-]+',  # ✅ search page
        ]

        links = []
        for pattern in patterns:
            links.extend(re.findall(pattern, text))

        return list(dict.fromkeys(links))

    def _extract_web_links(self, text):
        if not text:
            return []

        # Markdown links pehle extract karo [text](url)
        markdown_urls = re.findall(r'\[([^\]]+)\]\((https?://[^\s\)]+)\)', text)

        # Bare URLs
        bare_urls = re.findall(r'(?<!\()(https?://[^\s\)\]\,\"\'<>]+)', text)

        all_links = [url for _, url in markdown_urls] + bare_urls

        cleaned = []
        for link in all_links:
            link = re.sub(r'[.,;:!?)\]]+$', '', link)  # trailing chars remove
            if link.startswith('http'):
                cleaned.append(link)

        return list(dict.fromkeys(cleaned))
    # ══════════════════════════════════════
    def reset_chat(self):
        self.chat_history = []
        return "Cleared!"

    def get_history(self):
        return self.chat_history


# ══════════════════════════════════════
if __name__ == "__main__":
    brain = CareerBuddyBrain()

    print("\n🔍 Methods check:")
    print(f"  get_context:       {hasattr(brain, 'get_context')}")
    print(f"  get_web_context:   {hasattr(brain, 'get_web_context')}")
    print(f"  needs_web_search:  {hasattr(brain, 'needs_web_search')}")
    print(f"  _clean_response:   {hasattr(brain, '_clean_response')}")
    print(f"  _extract_yt_links: {hasattr(brain, '_extract_youtube_links')}")

    test_questions = ["free resources to learn Python"]

    for i, q in enumerate(test_questions, 1):
        print(f"\n{'='*60}\n❓ Q{i}: {q}\n{'='*60}")
        result = brain.chat(q)
        print(result["response"])