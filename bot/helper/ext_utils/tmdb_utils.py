import aiohttp
from logging import getLogger

LOGGER = getLogger(__name__)

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"


async def search_tmdb(query: str, api_key: str, media_type: str = "multi"):
    """Search TMDB for movie or TV show info."""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{TMDB_BASE_URL}/search/{media_type}"
            params = {
                "api_key": api_key,
                "query": query,
                "language": "ar",
                "include_adult": False,
            }
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = data.get("results", [])
                    if results:
                        return results[0]
    except Exception as e:
        LOGGER.error(f"TMDB search error: {e}")
    return None


async def get_tmdb_details(tmdb_id: int, api_key: str, media_type: str = "movie"):
    """Fetch detailed TMDB info for a movie or TV show."""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{TMDB_BASE_URL}/{media_type}/{tmdb_id}"
            params = {
                "api_key": api_key,
                "language": "ar",
                "append_to_response": "credits,release_dates,content_ratings",
            }
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    return await resp.json()
    except Exception as e:
        LOGGER.error(f"TMDB detail fetch error: {e}")
    return None


def clean_filename_for_search(filename: str) -> str:
    """Extract a clean movie/show name from a filename."""
    import re
    # Remove extension
    name = re.sub(r'\.[a-zA-Z0-9]{2,4}$', '', filename)
    # Remove common quality/codec tags
    patterns = [
        r'\b(1080p|720p|480p|4K|2160p|HDRip|BDRip|BluRay|WEBRip|WEB-DL|HDTV|DVDRip|DVDSCR|CAM|TS|HEVC|x264|x265|H\.264|H\.265|AAC|AC3|DTS|MP3|FLAC|Atmos)\b',
        r'\b(S\d{1,2}E\d{1,2}|Season\s*\d+|Episode\s*\d+)\b',
        r'\b(REPACK|PROPER|EXTENDED|UNRATED|THEATRICAL|DIRECTORS\.CUT|DC)\b',
        r'\b(10bit|8bit|HDR|SDR|Dolby)\b',
        r'\[.*?\]|\(.*?\)',
        r'\b\d{4}\b(?=.*\b(1080|720|480|2160)\b)',  # year before quality
        r'[-_.]+',
    ]
    for pattern in patterns:
        name = re.sub(pattern, ' ', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+', ' ', name).strip()
    # Extract year if present
    year_match = re.search(r'\b(19|20)\d{2}\b', filename)
    year = year_match.group(0) if year_match else None
    return name.strip(), year


async def get_media_info_from_filename(filename: str, api_key: str) -> dict:
    """Main function: get TMDB info from a filename."""
    if not api_key:
        return {}

    clean_name, year = clean_filename_for_search(filename)
    if not clean_name:
        return {}

    LOGGER.info(f"TMDB: Searching for '{clean_name}' (year: {year})")

    # Try multi search first
    result = await search_tmdb(clean_name, api_key, "multi")
    if not result:
        # fallback: English search
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{TMDB_BASE_URL}/search/multi"
                params = {"api_key": api_key, "query": clean_name, "language": "en-US"}
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        results = data.get("results", [])
                        if results:
                            result = results[0]
        except Exception as e:
            LOGGER.error(f"TMDB fallback error: {e}")

    if not result:
        return {}

    media_type = result.get("media_type", "movie")
    tmdb_id = result.get("id")

    if media_type not in ("movie", "tv"):
        return {}

    details = await get_tmdb_details(tmdb_id, api_key, media_type)
    if not details:
        return {}

    # Extract info
    title = details.get("title") or details.get("name", "")
    original_title = details.get("original_title") or details.get("original_name", "")
    overview = details.get("overview", "")
    vote_average = details.get("vote_average", 0)
    vote_count = details.get("vote_count", 0)
    genres = [g["name"] for g in details.get("genres", [])]
    poster_path = details.get("poster_path", "")
    poster_url = f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else ""
    backdrop_path = details.get("backdrop_path", "")
    backdrop_url = f"https://image.tmdb.org/t/p/original{backdrop_path}" if backdrop_path else ""

    release_date = details.get("release_date") or details.get("first_air_date", "")
    release_year = release_date[:4] if release_date else ""

    # Runtime
    runtime = details.get("runtime") or 0
    if not runtime and details.get("episode_run_time"):
        runtime = details["episode_run_time"][0] if details["episode_run_time"] else 0

    # Production countries
    countries = [c["name"] for c in details.get("production_countries", [])]

    # Cast
    cast = []
    if credits := details.get("credits"):
        for person in credits.get("cast", [])[:5]:
            cast.append(person["name"])

    # Director
    director = ""
    if credits := details.get("credits"):
        for person in credits.get("crew", []):
            if person.get("job") == "Director":
                director = person["name"]
                break

    # Language
    original_language = details.get("original_language", "").upper()

    return {
        "title": title,
        "original_title": original_title,
        "overview": overview,
        "vote_average": round(vote_average, 1),
        "vote_count": vote_count,
        "genres": genres,
        "poster_url": poster_url,
        "backdrop_url": backdrop_url,
        "release_year": release_year,
        "runtime": runtime,
        "countries": countries,
        "cast": cast,
        "director": director,
        "original_language": original_language,
        "media_type": media_type,
        "tmdb_id": tmdb_id,
    }


def format_tmdb_caption(tmdb_info: dict, filename: str) -> str:
    """Format a beautiful Telegram caption from TMDB info."""
    if not tmdb_info:
        return f"<code>{filename}</code>"

    title = tmdb_info.get("title", "")
    original_title = tmdb_info.get("original_title", "")
    overview = tmdb_info.get("overview", "")
    rating = tmdb_info.get("vote_average", 0)
    genres = tmdb_info.get("genres", [])
    release_year = tmdb_info.get("release_year", "")
    runtime = tmdb_info.get("runtime", 0)
    cast = tmdb_info.get("cast", [])
    director = tmdb_info.get("director", "")
    original_language = tmdb_info.get("original_language", "")
    media_type = tmdb_info.get("media_type", "movie")
    tmdb_id = tmdb_info.get("tmdb_id", "")

    # Star rating
    stars = "⭐" * int(rating / 2) + ("½" if rating % 2 >= 1 else "")

    type_emoji = "🎬" if media_type == "movie" else "📺"
    type_label = "فيلم" if media_type == "movie" else "مسلسل"

    lines = []
    lines.append(f"🍿 <b>{title}</b>")
    if original_title and original_title != title:
        lines.append(f"<i>{original_title}</i>")
    lines.append("")

    if overview:
        # Truncate overview to 300 chars
        if len(overview) > 300:
            overview = overview[:297] + "..."
        lines.append(f"📖 {overview}")
        lines.append("")

    info_lines = []
    if release_year:
        info_lines.append(f"📅 <b>السنة:</b> {release_year}")
    if runtime:
        h, m = divmod(runtime, 60)
        rt_str = f"{h}س {m}د" if h else f"{m}د"
        info_lines.append(f"⏱ <b>المدة:</b> {rt_str}")
    if rating:
        info_lines.append(f"⭐ <b>التقييم:</b> {rating}/10")
    if genres:
        info_lines.append(f"🎭 <b>النوع:</b> {' | '.join(genres[:3])}")
    if original_language:
        info_lines.append(f"🌐 <b>اللغة:</b> {original_language}")
    if director:
        info_lines.append(f"🎥 <b>المخرج:</b> {director}")
    if cast:
        info_lines.append(f"🎭 <b>أبطال العمل:</b> {', '.join(cast[:3])}")

    lines.extend(info_lines)

    if tmdb_id:
        tmdb_url = f"https://www.themoviedb.org/{media_type}/{tmdb_id}"
        lines.append("")
        lines.append(f"🔗 <a href='{tmdb_url}'>معلومات إضافية على TMDB</a>")

    lines.append("")
    lines.append(f"🍿 <b>PopCorn</b> | @PopCornMiniApp_bot")

    return "\n".join(lines)


async def fetch_tmdb_poster(poster_url: str) -> bytes | None:
    """Download poster image bytes from TMDB."""
    if not poster_url:
        return None
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(poster_url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    return await resp.read()
    except Exception as e:
        LOGGER.error(f"TMDB poster download error: {e}")
    return None
