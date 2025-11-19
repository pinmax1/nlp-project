import json
import numpy as np
import faiss
from sklearn.preprocessing import normalize
from tqdm import tqdm
import os
from bs4 import BeautifulSoup
import html
import re
from typing import List, Dict, Any, Optional
import ollama

from api.config import ServerConfig

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

class SteamDBManager:
    def __init__(self, server_config: ServerConfig) -> None:
        self.logger = server_config.logger_config.get_logger("SteamDBManager")
        self.steamdb_path: str = server_config.STEAMDB_PATH
        self.model_name: str = server_config.INDEX_MODEL_NAME
        self.embeddings_path: str = server_config.EMBEDDINGS_PATH
        self.data: List[Dict[str, Any]] = self._load_data()
        self._filter_games()
        self.ollama_client = ollama.Client(host=server_config.OLLAMA_HOST)

        if os.path.exists(self.embeddings_path):
            self.embeddings: np.ndarray = self._load_embeddings()
        else:
            self.embeddings: np.ndarray = self._generate_embeddings()
            self._save_embeddings(self.embeddings)

        self.index: faiss.Index = self._create_faiss_index(self.embeddings)

    DESCRIPTION_TAGS: Dict[str, str] = {
        # === CORE GENRES ===
        r"\brpg\b": "RPG",
        r"\brole[- ]?playing\b": "RPG",
        r"\baction rpg\b": "Action RPG",
        r"\bjrpg\b": "JRPG",
        r"\bsouls[- ]?like\b": "Souls-like",
        r"\bmmo\b": "MMO",
        r"\bmmorpg\b": "MMORPG",
        r"\barpg\b": "ARPG",

        r"\bshooter\b": "Shooter",
        r"\bfps\b": "FPS",
        r"\bfirst[- ]?person shooter\b": "FPS",
        r"\btps\b": "TPS",
        r"\bthird[- ]?person shooter\b": "Third-Person Shooter",
        r"\btop[- ]?down shooter\b": "Top-Down Shooter",

        r"\bstrategy\b": "Strategy",
        r"\brts\b": "RTS",
        r"\breal[- ]?time strategy\b": "RTS",
        r"\bturn[- ]?based\b": "Turn-Based",
        r"\btactical\b": "Tactical",

        r"\broguelike\b": "Roguelike",
        r"\brogue[- ]?lite\b": "Roguelite",
        r"\bpermadeath\b": "Permadeath",

        r"\bplatformer\b": "Platformer",
        r"\bmetroidvania\b": "Metroidvania",

        r"\bsurvival\b": "Survival",
        r"\bcra(ft|fting)\b": "Crafting",
        r"\bbase building\b": "Base Building",

        r"\bpuzzle\b": "Puzzle",

        r"\bhorror\b": "Horror",
        r"\bsurvival horror\b": "Survival Horror",

        r"\bsimulation\b": "Simulation",
        r"\blife sim\b": "Life Simulation",
        r"\bfarming\b": "Farming",
        r"\bfarm\b": "Farming",
        r"\bmanagement\b": "Management",

        r"\bracing\b": "Racing",
        r"\bdriving\b": "Driving",
        r"\bvehicle combat\b": "Vehicular Combat",

        # === WORLD / SETTING ===
        r"\bfantasy\b": "Fantasy",
        r"\bhigh fantasy\b": "High Fantasy",
        r"\bdark fantasy\b": "Dark Fantasy",

        r"\bmedieval\b": "Medieval",
        r"\bknight\b": "Medieval",

        r"\bmagic(al)?\b": "Magic",
        r"\bspell\b": "Magic",

        r"\bsteampunk\b": "Steampunk",
        r"\bcyberpunk\b": "Cyberpunk",

        r"\bpost[- ]?apocalyptic\b": "Post-Apocalyptic",
        r"\bdystopian\b": "Dystopian",
        r"\bapocalypse\b": "Post-Apocalyptic",

        r"\bscience fiction\b": "Sci-Fi",
        r"\bsci[- ]?fi\b": "Sci-Fi",
        r"\bspace\b": "Space",
        r"\bgalaxy\b": "Space",
        r"\binterstellar\b": "Space",

        r"\bwestern\b": "Western",
        r"\bsamurai\b": "Samurai",
        r"\bninja\b": "Ninja",
        r"\bmytholog(y|ical)\b": "Mythology",

        # === WORLD TYPE ===
        r"\bopen world\b": "Open World",
        r"\bopen[- ]?world\b": "Open World",
        r"\bsandbox\b": "Sandbox",
        r"\bnon[- ]?linear\b": "Non-linear",
        r"\bhub[- ]?based\b": "Hub World",

        # === STORY / TONE ===
        r"\bstory[- ]?driven\b": "Story Rich",
        r"\bstory rich\b": "Story Rich",
        r"\bnarrative\b": "Narrative",
        r"\bchoices matter\b": "Choices Matter",
        r"\bbranching\b": "Choices Matter",
        r"\bmoral choices?\b": "Moral Choices",
        r"\bcharacter driven\b": "Character Driven",
        r"\bepic\b": "Epic",
        r"\blemotional\b": "Emotional",

        # === CHARACTERS ===
        r"\bcompanions?\b": "Companions",
        r"\bfollowers?\b": "Companions",
        r"\bfactions?\b": "Factions",

        # === COMBAT ===
        r"\bcombat\b": "Combat",
        r"\bmelee\b": "Melee Combat",
        r"\bsword\b": "Melee Combat",
        r"\barchery\b": "Archery",
        r"\branged\b": "Ranged Combat",
        r"\bgunfight\b": "Gun Combat",
        r"\bshootout\b": "Gun Combat",

        r"\bboss(es)?\b": "Boss Fights",
        r"\bstealth\b": "Stealth",
        r"\bcover system\b": "Cover Shooter",
        r"\bparkour\b": "Parkour",
        r"\bdodging\b": "Dodging",

        # === RPG SYSTEMS / PROGRESSION ===
        r"\blevel up\b": "Progression",
        r"\bleveling\b": "Progression",
        r"\bexperience\b": "Progression",
        r"\bxp\b": "Progression",

        r"\bskills?\b": "Skills",
        r"\bskill tree\b": "Skills",
        r"\babilities\b": "Abilities",
        r"\btraits?\b": "Traits",
        r"\bperks?\b": "Perks",

        r"\bloot\b": "Loot",
        r"\bloot system\b": "Loot",
        r"\binventory\b": "Inventory",
        r"\bcrafting\b": "Crafting",
        r"\bresource(s)?\b": "Resource Management",

        # === QUESTS / EXPLORATION ===
        r"\bquest(s)?\b": "Questing",
        r"\bside quest\b": "Side Quests",
        r"\bexplor(ation|e)\b": "Exploration",
        r"\bdiscover\b": "Exploration",
        r"\bdungeon(s)?\b": "Dungeons",
        r"\braids?\b": "Raids",
        r"\bcaves?\b": "Caves",
        r"\bruins?\b": "Ruins",

        # === WORLD ACTIVITIES ===
        r"\bhunting\b": "Hunting",
        r"\bfishing\b": "Fishing",
        r"\bharvesting\b": "Harvesting",
        r"\bmining\b": "Mining",
        r"\bhorse riding\b": "Horse Riding",
        r"\bmount\b": "Mounts",

        # === ENEMIES / CREATURES ===
        r"\bmonsters?\b": "Monsters",
        r"\bbeasts?\b": "Beasts",
        r"\bdemons?\b": "Demons",
        r"\bdragons?\b": "Dragons",
        r"\bundead\b": "Undead",
        r"\bzombies?\b": "Zombies",
        r"\baliens?\b": "Aliens",
        r"\brobots?\b": "Robots",
        r"\bmechs?\b": "Mechs",

        # === MULTIPLAYER / ONLINE ===
        r"\bcoop\b": "Co-op",
        r"\bco[- ]?op\b": "Co-op",
        r"\bmultiplayer\b": "Multiplayer",
        r"\bonline\b": "Online",
        r"\bpvp\b": "PvP",
        r"\bpve\b": "PvE",
        r"\bguild(s)?\b": "Guilds",
        r"\bclan(s)?\b": "Clans",

        # === VISUAL STYLE ===
        r"\bpixel art\b": "Pixel Art",
        r"\banime\b": "Anime",
        r"\bcartoon\b": "Cartoon",
        r"\bvoxel\b": "Voxel",
        r"\b2d\b": "2D",
        r"\b3d\b": "3D",
        r"\bisometric\b": "Isometric",
        r"\btop[- ]?down\b": "Top-Down",

        # === MISC ===
        r"\brealistic\b": "Realistic",
        r"\bphysics\b": "Physics",
        r"\bdestruction\b": "Destruction",
        r"\bcraft\b": "Crafting",
        r"\bbuilder\b": "Building",
        r"\bopen ended\b": "Open-Ended",
    }

    def extract_tags_from_description(self, description: str) -> List[str]:
        found_tags: set[str] = set()

        for pattern, tag in SteamDBManager.DESCRIPTION_TAGS.items():
            if re.search(pattern, description, flags=re.IGNORECASE):
                found_tags.add(tag)

        return list(found_tags)

    def _get_cleaned_description(self, game: Dict[str, Any]) -> str:
        name: str = (game.get("name") or "").strip()

        raw_desc: str = game.get("description", "") or ""
        clean: str = BeautifulSoup(raw_desc, "html.parser").get_text(separator=" ")
        clean = html.unescape(clean)
        clean = re.sub(r"\s+", " ", clean).strip()

        tags: str = game.get("tags", "") or ""
        if tags:
            tags = " ".join(tags.split(","))

        auto_tags: List[str] = self.extract_tags_from_description(clean)
        auto_tags_str: str = " ".join(auto_tags) if auto_tags else ""

        combined_tags: str = " ".join(dict.fromkeys((tags + " " + auto_tags_str).split()))

        genres: str = game.get("genres", "") or ""
        if genres:
            genres = " ".join(genres.split(","))

        result: List[str] = []

        if name:
            result.append(f"Game: {name}.")

        if combined_tags:
            result.append(f"Tags: {combined_tags}.")

        if genres:
            result.append(f"Genres: {genres}.")

        final_text: str = "\n".join(result).strip()
        final_text = (
            "Represent the meaning of the following video game description for semantic retrieval:\n"
            f"{final_text}"
        )

        return final_text

    def _load_data(self) -> List[Dict[str, Any]]:
        self.logger.info("Started loading steamdb data")
        with open(self.steamdb_path, 'r', encoding='utf-8') as f:
            data: List[Dict[str, Any]] = json.load(f)
        self.logger.info("Loaded steamdb data")
        return data

    def _filter_games(self) -> None:
        result: List[Dict[str, Any]] = []
        for game in tqdm(self.data, desc="Generating embeddings", unit="game"):
            description: Optional[str] = game.get("description", "")
            stsp_owners: Optional[int] = game.get("stsp_owners", "")
            if description is None or description == "" or stsp_owners is None or stsp_owners <= 35000:
                continue
            result.append(game)
        self.data = result

    def _generate_embeddings(self) -> np.ndarray:
        self.logger.info("Started generating embeddings")
        embeddings: List[np.ndarray] = []
        i = 0
        for game in tqdm(self.data, desc="Generating embeddings", unit="game"):
            try:
                description: str = self._get_cleaned_description(game)
            except Exception:
                print("Exception!!")
                description = str(game.get("description", ""))
            if i == 5:
                print(description)
            i += 1
            
            emb: np.ndarray = self._get_text_embedding(description)
            embeddings.append(emb)

        self.logger.info("Finished generating embeddings")
        return np.array(embeddings)

    def _get_text_embedding(self, text: str) -> np.ndarray:
        response = self.ollama_client.embeddings(
            model="mxbai-embed-large",
            prompt=text
        )
        emb = np.array(response["embedding"], dtype=np.float32)
        emb = emb / np.linalg.norm(emb)
        return emb

    def _create_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        self.logger.info("Started building index")
        embeddings = normalize(embeddings)

        dimension: int = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings.astype(np.float32))

        self.logger.info("Finished building index")
        return index

    def _save_embeddings(self, embeddings: np.ndarray) -> None:
        np.save(self.embeddings_path, embeddings)

    def _load_embeddings(self) -> np.ndarray:
        try:
            embeddings: np.ndarray = np.load(self.embeddings_path)
            return embeddings
        except FileNotFoundError:
            return np.array([])

    def find_similar_games(self, query: str, k: int = 50) -> List[Dict[str, str]]:
        query = f"Represent the user query for retrieving relevant video games. \n{query}"
        self.logger.info(f"Started finding similiar games by query: {query}")

        query_embedding: np.ndarray = self._get_text_embedding(query).reshape(1, -1)
        query_embedding = normalize(query_embedding)
        
        distances, indices = self.index.search(query_embedding.astype(np.float32), k)
        self.logger.info(f"Found {k} similiar games")
        similar_games = []
        for i, idx in enumerate(indices[0]):
            game = self.data[idx]
            similar_games.append({
                'name': game['name'],
                'description': game['description']
            })
        return similar_games
