import os
import glob
import re
import traceback
import unicodedata
from difflib import SequenceMatcher
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

_NEEDED_COLS = [
    "DriverId",
    "Abbreviation",
    "FullName",
    "TeamName",
    "Position",
    "GridPosition",
    "ClassifiedPosition",
    "Status",
    "Laps",
    "Points",
    "Year",
    "Date",
    "EventName",
    "Mode",
    "RoundNumber",
]


def _classified_status(status: object) -> bool:
    text = str(status or "").strip().lower()
    return (
        text == "finished"
        or text == "lapped"
        or bool(re.fullmatch(r"\+\d+\s+laps?", text))
    )


def _did_not_start_status(status: object) -> bool:
    text = str(status or "").strip().lower()
    return text in {"did not start", "did not qualify", "withdrew", "withdrawn"}


def _normalize_text(text: object) -> str:
    if pd.isna(text):
        return ""
    normalized = unicodedata.normalize("NFKD", str(text or "").lower())
    normalized = "".join(c for c in normalized if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", normalized).strip()


def _format_number(value: float | int) -> str:
    number = float(value)
    if number.is_integer():
        return str(int(number))
    return f"{number:.1f}".replace(".", ",")


def _plural(value: float | int, singular: str, plural: str) -> str:
    word = singular if abs(float(value)) == 1 else plural
    return f"{_format_number(value)} {word}"


_RACE_GENERIC_TOKENS = {
    "a",
    "as",
    "da",
    "das",
    "de",
    "do",
    "dos",
    "e",
    "em",
    "etapa",
    "gp",
    "grand",
    "o",
    "os",
    "prix",
    "race",
    "racing",
}

_QUERY_STOPWORDS = _RACE_GENERIC_TOKENS | {
    "ano",
    "chegou",
    "colocacao",
    "colocacoes",
    "corrida",
    "corridas",
    "ficou",
    "final",
    "ganhador",
    "ganhou",
    "lugar",
    "mais",
    "podio",
    "posicao",
    "posicoes",
    "primeiro",
    "primeiros",
    "qual",
    "quais",
    "quem",
    "recente",
    "resultado",
    "top",
    "ultima",
    "ultimas",
    "ultimo",
    "ultimos",
    "venceu",
    "vencedor",
    "vencedores",
}

_EVENT_ALIASES = {
    "abu dhabi": ["abu", "dhabi"],
    "alemanha": ["german"],
    "arabia": ["saudi", "arabian"],
    "arabia saudita": ["saudi", "arabian"],
    "australia": ["australian"],
    "austria": ["austrian"],
    "azerbaijao": ["azerbaijan"],
    "bahrein": ["bahrain"],
    "barein": ["bahrain"],
    "belgica": ["belgian"],
    "brasil": ["brazilian", "sao", "paulo"],
    "canada": ["canadian"],
    "catar": ["qatar"],
    "china": ["chinese"],
    "eifel": ["eifel"],
    "emilia romagna": ["emilia", "romagna", "imola"],
    "espanha": ["spanish", "barcelona"],
    "estados unidos": ["united", "states"],
    "eua": ["united", "states"],
    "europa": ["european"],
    "franca": ["french"],
    "gra bretanha": ["british", "silverstone"],
    "holanda": ["dutch", "netherlands"],
    "hungria": ["hungarian"],
    "imola": ["emilia", "romagna", "imola"],
    "inglaterra": ["british", "silverstone"],
    "italia": ["italian", "monza"],
    "japao": ["japanese", "suzuka"],
    "jeddah": ["saudi", "arabian"],
    "las vegas": ["las", "vegas"],
    "malasia": ["malaysian"],
    "mexico": ["mexican", "mexico", "city"],
    "monza": ["italian", "monza"],
    "monaco": ["monaco"],
    "spa": ["belgian"],
    "spa francorchamps": ["belgian"],
    "interlagos": ["brazilian", "sao", "paulo"],
    "silverstone": ["british", "silverstone"],
    "suzuka": ["japanese", "suzuka"],
    "zandvoort": ["dutch", "netherlands"],
    "barcelona": ["spanish", "barcelona"],
    "catalunya": ["spanish", "barcelona"],
    "circuito da catalunha": ["spanish", "barcelona"],
    "spielberg": ["austrian"],
    "red bull ring": ["austrian"],
    "baku": ["azerbaijan"],
    "yas marina": ["abu", "dhabi"],
    "miami": ["miami"],
    "cota": ["united", "states"],
    "hungaroring": ["hungarian"],
    "paulo": ["sao", "paulo"],
    "portugal": ["portuguese"],
    "qatar": ["qatar"],
    "russia": ["russian"],
    "sao paulo": ["sao", "paulo", "brazilian"],
    "singapura": ["singapore"],
    "turquia": ["turkish"],
}


def _significant_tokens(text: str, stopwords: set[str] | None = None) -> set[str]:
    stopwords = stopwords or _RACE_GENERIC_TOKENS
    return {
        token
        for token in re.findall(r"[a-z0-9]+", _normalize_text(text))
        if len(token) >= 3 and token not in stopwords and not token.isdigit()
    }


def _expanded_query_tokens(normalized_text: str) -> set[str]:
    tokens = _significant_tokens(normalized_text, _QUERY_STOPWORDS)
    for alias, replacements in _EVENT_ALIASES.items():
        if alias in normalized_text:
            tokens.update(replacements)
    return tokens
 
 
def _read_parquet(filepath: str) -> pd.DataFrame | None:

    try:
        df = pd.read_parquet(filepath, engine="fastparquet")
        cols = [c for c in _NEEDED_COLS if c in df.columns]
        return df[cols]
    except Exception:
        pass
 
    try:
        df = pd.read_parquet(filepath)
        cols = [c for c in _NEEDED_COLS if c in df.columns]
        return df[cols]
    except Exception as err:
        print(f"[DATA] Erro ao ler {os.path.basename(filepath)}: {err}")
        return None
 
 
def _load_session_files(pattern: str) -> pd.DataFrame:
    """Le arquivos da pasta data/ e retorna um DataFrame unico."""
    print(f"[DATA] Procurando arquivos em: {DATA_DIR}")
 
    if not os.path.isdir(DATA_DIR):
        print(f"[DATA] ERRO: pasta 'data/' não encontrada em {DATA_DIR}")
        print("[DATA] Verifique se os arquivos .parquet estão na pasta correta.")
        return pd.DataFrame()
 
    files = sorted(glob.glob(os.path.join(DATA_DIR, pattern)))
 
    if not files:
        print(f"[DATA] ERRO: nenhum arquivo {pattern} encontrado!")
        return pd.DataFrame()
 
    print(f"[DATA] {len(files)} arquivos encontrados. Carregando...")
 
    dfs = []
    failed = 0
    for i, f in enumerate(files):
        df = _read_parquet(f)
        if df is not None:
            dfs.append(df)
        else:
            failed += 1
 
        if (i + 1) % 100 == 0 or (i + 1) == len(files):
            print(f"[DATA]   {i + 1}/{len(files)} arquivos processados...")
 
    if failed > 0:
        print(f"[DATA] Aviso: {failed} arquivo(s) não puderam ser lidos.")
 
    if not dfs:
        print("[DATA] ERRO: nenhum arquivo foi carregado com sucesso.")
        return pd.DataFrame()
 
    result = pd.concat(dfs, ignore_index=True)
    print(f"[DATA] Carregamento concluído: {len(result)} registros.")
    return result


def _load_all_races() -> pd.DataFrame:
    """Le todos os arquivos *_R.parquet e retorna um DataFrame unico."""
    return _load_session_files("*_R.parquet")


def _load_all_point_sessions() -> pd.DataFrame:
    """Le corridas e sprints, que sao as sessoes que pontuam no campeonato."""
    return _load_session_files("*_[RS].parquet")


def _to_silver_sessions(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza tipos e remove linhas sem chaves para analise estatistica."""
    if df.empty:
        return df

    silver = df.copy()
    silver["Mode"] = silver.get("Mode", "Race").fillna("Race")
    silver["FullName"] = silver["FullName"].fillna("").astype(str).str.strip()
    silver["TeamName"] = silver["TeamName"].fillna("Equipe não informada").astype(str).str.strip()
    silver["DriverId"] = silver.get("DriverId", silver["FullName"]).fillna(silver["FullName"])
    silver["DriverId"] = silver["DriverId"].astype(str).str.strip()

    for col in ["Position", "GridPosition", "Points", "Year", "RoundNumber", "Laps"]:
        if col in silver.columns:
            silver[col] = pd.to_numeric(silver[col], errors="coerce")

    if "Status" not in silver.columns:
        silver["Status"] = ""
    if "ClassifiedPosition" not in silver.columns:
        silver["ClassifiedPosition"] = ""

    silver["Status"] = silver["Status"].fillna("").astype(str).str.strip()
    silver["ClassifiedPosition"] = silver["ClassifiedPosition"].fillna("").astype(str).str.strip()
    classified_position = pd.to_numeric(silver["ClassifiedPosition"], errors="coerce").notna()
    classified_status = silver["Status"].map(_classified_status)
    missing_status_with_position = silver["Status"].eq("") & silver["Position"].notna()
    silver["IsClassified"] = classified_status | classified_position | missing_status_with_position
    silver["DidNotStart"] = (
        silver["Status"].map(_did_not_start_status)
        | silver["ClassifiedPosition"].str.upper().eq("W")
    )
    silver["DidNotFinish"] = ~silver["IsClassified"] & ~silver["DidNotStart"]

    silver["Date"] = pd.to_datetime(silver["Date"], errors="coerce")
    silver = silver.dropna(subset=["FullName", "Year", "RoundNumber"])
    silver = silver[silver["FullName"] != ""]
    silver["Year"] = silver["Year"].astype(int)
    silver["RoundNumber"] = silver["RoundNumber"].astype(int)
    silver["Points"] = silver["Points"].fillna(0.0)
    silver = silver.sort_values(["Year", "RoundNumber", "Mode", "Position"], na_position="last")
    return silver.reset_index(drop=True)
 
 
def _points_leaders_per_year(df: pd.DataFrame) -> str:
    """Piloto com mais pontos acumulados em cada temporada."""
    leaders = (
        df.groupby(["Year", "FullName"])["Points"]
        .sum()
        .reset_index()
        .sort_values(["Year", "Points"], ascending=[True, False])
        .drop_duplicates("Year")
    )
    return "\n".join(
        f"  {int(r.Year)}: {r.FullName} ({r.Points:.0f} pts)"
        for r in leaders.itertuples()
    )
 
 
class F1DataKnowledgeBase:
    """Base estruturada local montada a partir dos parquets importados via FastF1."""

    def __init__(self):
        print("[DATA] Carregando dados históricos de F1...")
        self.bronze_sessions = self._safe_load_sessions()
        self.sessions = _to_silver_sessions(self.bronze_sessions)
        self.context = self._build_context()
        self._prediction_cache = None

    def _safe_load_sessions(self) -> pd.DataFrame:
        try:
            return _load_all_point_sessions()
        except Exception:
            print("[DATA] ERRO inesperado ao carregar dados:")
            traceback.print_exc()
            return pd.DataFrame()

    def answer(self, user_input: str) -> str | None:
        """Tenta responder usando apenas a base estruturada antes do LLM."""
        if self.sessions.empty:
            return None

        text = user_input.lower()

        comparison_answer = self.driver_comparison(user_input)
        if comparison_answer:
            return comparison_answer

        race_answer = self.race_result(user_input)
        if race_answer:
            return race_answer

        driver_fact_answer = self.driver_fact(user_input)
        if driver_fact_answer:
            return driver_fact_answer

        championship_answer = self.championship_result(user_input)
        if championship_answer:
            return championship_answer

        if self._is_prediction_question(text):
            return self.predict_driver_champion()

        if self._is_standings_question(text):
            year = self._championship_query_year(text) or int(self.sessions["Year"].max())
            return self.driver_standings(year)

        if self._is_recent_winners_question(text):
            return self.recent_winners()

        if self._is_driver_profile_question(text):
            driver_profile = self.driver_profile(user_input)
            if driver_profile:
                return driver_profile

        return None

    def _build_context(self) -> str:
        if self.sessions.empty:
            return "Dados históricos de corridas não disponíveis no momento."

        try:
            df = self.sessions.copy()
            races = df[df["Mode"].fillna("Race").eq("Race")].copy()
            winners = races[races["Position"] == 1.0].copy()
            all_years = sorted(df["Year"].dropna().unique())
            last_two = all_years[-2:]
            latest_year = int(all_years[-1])

            top_drivers = winners["FullName"].value_counts().head(15)
            driver_wins_str = "\n".join(
                f"  {name}: {count} vitórias" for name, count in top_drivers.items()
            )

            top_teams = winners["TeamName"].value_counts().head(10)
            team_wins_str = "\n".join(
                f"  {name}: {count} vitórias" for name, count in top_teams.items()
            )

            champ_str = _points_leaders_per_year(df)

            current_drivers = (
                df[df["Year"].eq(latest_year)]
                .groupby(["FullName", "TeamName"], as_index=False)["Points"]
                .sum()
                .sort_values("Points", ascending=False)
            )
            current_driver_str = "\n".join(
                f"  {r.FullName} ({r.TeamName}) — {r.Points:.0f} pts"
                for r in current_drivers.itertuples()
            )

            recent_races = winners.sort_values("Date").tail(10)[
                ["Year", "EventName", "FullName", "TeamName"]
            ]
            recent_str = "\n".join(
                f"  {int(r.Year)} — {r.EventName}: {r.FullName} ({r.TeamName})"
                for r in recent_races.itertuples()
            )

            recent_driver_form = (
                winners[winners["Year"].isin(last_two)]["FullName"].value_counts()
            )
            recent_driver_str = "\n".join(
                f"  {name}: {count} vitórias" for name, count in recent_driver_form.items()
            )

            recent_team_form = (
                winners[winners["Year"].isin(last_two)]["TeamName"].value_counts()
            )
            recent_team_str = "\n".join(
                f"  {name}: {count} vitórias" for name, count in recent_team_form.items()
            )

            context = f"""
=== DADOS HISTÓRICOS DE F1 ({int(all_years[0])}–{int(all_years[-1])}) ===

MAIORES VENCEDORES DE CORRIDAS (todos os tempos):
{driver_wins_str}

VITÓRIAS POR EQUIPE (todos os tempos):
{team_wins_str}

LÍDERES DE PONTOS POR TEMPORADA:
{champ_str}

PILOTOS DA TEMPORADA MAIS RECENTE ({latest_year}):
{current_driver_str}

ÚLTIMAS 10 CORRIDAS:
{recent_str}

FORMA RECENTE — PILOTOS ({int(last_two[0])}–{int(last_two[1])}):
{recent_driver_str}

FORMA RECENTE — EQUIPES ({int(last_two[0])}–{int(last_two[1])}):
{recent_team_str}
""".strip()

            print(
                f"[DATA] Contexto pronto: {int(all_years[0])}–{int(all_years[-1])}, "
                f"{len(winners)} vitórias indexadas."
            )
            return context

        except Exception:
            print("[DATA] ERRO ao montar o contexto estatístico:")
            traceback.print_exc()
            return "Dados históricos de corridas não disponíveis no momento."

    def predict_driver_champion(self) -> str:
        prediction = self.champion_prediction_table()

        leader = prediction.iloc[0]
        runner_up = prediction.iloc[1] if len(prediction) > 1 else leader
        latest_year = int(leader.Year)
        confidence = self._prediction_confidence(
            latest_round=int(leader.RoundNumber),
            leader_probability=float(leader.ChampionProbability),
            gap=float(leader.ChampionProbability - runner_up.ChampionProbability),
        )

        top_lines = []
        for idx, row in prediction.head(3).iterrows():
            top_lines.append(
                f"{idx + 1}. {row.FullName} ({row.TeamName}) — "
                f"{row.ChampionProbability * 100:.1f}%"
            )

        return (
            f"Meu palpite para campeão de pilotos de {latest_year} é {leader.FullName}.\n\n"
            "Top 3 da projeção:\n"
            + "\n".join(top_lines)
            + "\n\n"
            f"Eu trataria essa previsão com confiança {confidence}. "
            f"{leader.FullName} aparece à frente porque combina pontuação forte, ritmo recente "
            "e desempenho consistente em posições de chegada. Ainda assim, campeonato de F1 muda "
            "rápido: abandono, atualização de carro e sequência de pistas podem virar a tendência."
        )

    def champion_prediction_table(self) -> pd.DataFrame:
        latest_year = int(self.sessions["Year"].max())
        latest_round = int(self.sessions[self.sessions["Year"] == latest_year]["RoundNumber"].max())
        cache_key = (latest_year, latest_round)

        if self._prediction_cache and self._prediction_cache["key"] == cache_key:
            return self._prediction_cache["data"].copy()

        prediction = self._predict_with_local_model()
        if prediction is None:
            prediction = self._predict_with_points_trend()

        self._prediction_cache = {"key": cache_key, "data": prediction.copy()}
        return prediction

    def dashboard_payload(self) -> dict:
        latest_year = int(self.sessions["Year"].max())
        season = self.sessions[self.sessions["Year"] == latest_year].copy()
        prediction = self.champion_prediction_table()
        leader = prediction.iloc[0]
        runner_up = prediction.iloc[1] if len(prediction) > 1 else leader
        latest_round = int(leader.RoundNumber)
        confidence = self._prediction_confidence(
            latest_round=latest_round,
            leader_probability=float(leader.ChampionProbability),
            gap=float(leader.ChampionProbability - runner_up.ChampionProbability),
        )

        standings = (
            season.groupby(["FullName", "TeamName"], as_index=False)["Points"]
            .sum()
            .sort_values("Points", ascending=False)
            .head(8)
        )

        races = self.sessions[self.sessions["Mode"].eq("Race")].copy()
        season_races = season[season["Mode"].eq("Race")].copy()
        winners = races[races["Position"] == 1.0].sort_values("Date").tail(5)
        season_winners = season_races[season_races["Position"] == 1.0].drop_duplicates(
            ["Year", "RoundNumber"]
        )
        team_wins = (
            season_winners["TeamName"]
            .value_counts()
            .head(6)
            .reset_index()
        )
        team_wins.columns = ["team", "wins"]

        latest_event = season.sort_values("Date").dropna(subset=["Date"]).tail(1)
        latest_event_name = latest_event.iloc[0]["EventName"] if not latest_event.empty else ""

        return {
            "prediction": {
                "year": latest_year,
                "leader": str(leader.FullName),
                "team": str(leader.TeamName),
                "confidence": confidence,
                "top": [
                    {
                        "driver": str(row.FullName),
                        "team": str(row.TeamName),
                        "probability": round(float(row.ChampionProbability) * 100, 1),
                        "points": round(float(row.Points), 1),
                        "wins": int(row.Wins) if pd.notna(row.Wins) else 0,
                        "podiums": int(row.Podiums) if pd.notna(row.Podiums) else 0,
                    }
                    for row in prediction.head(5).itertuples()
                ],
            },
            "summary": {
                "season": latest_year,
                "latestRound": latest_round,
                "latestEvent": str(latest_event_name),
                "seasons": int(self.sessions["Year"].nunique()),
                "drivers": int(self.sessions["FullName"].nunique()),
                "teams": int(self.sessions["TeamName"].nunique()),
                "races": int(races[["Year", "RoundNumber"]].drop_duplicates().shape[0]),
            },
            "standings": [
                {
                    "position": idx + 1,
                    "driver": str(row.FullName),
                    "team": str(row.TeamName),
                    "points": round(float(row.Points), 1),
                }
                for idx, row in enumerate(standings.itertuples())
            ],
            "recentWinners": [
                {
                    "year": int(row.Year),
                    "event": str(row.EventName),
                    "driver": str(row.FullName),
                    "team": str(row.TeamName),
                }
                for row in winners.itertuples()
            ],
            "teamWins": [
                {"team": str(row.team), "wins": int(row.wins)}
                for row in team_wins.itertuples()
            ],
        }

    def driver_standings(self, year: int | None = None, limit: int = 10) -> str | None:
        year = year or int(self.sessions["Year"].max())
        season = self.sessions[self.sessions["Year"] == year].copy()
        if season.empty:
            return f"Não encontrei pontuação de campeonato para {year}."

        standings = (
            season.groupby(["FullName", "TeamName"], as_index=False)["Points"]
            .sum()
            .sort_values("Points", ascending=False)
            .head(limit)
        )
        rows = [
            f"{i + 1}. {r.FullName} ({r.TeamName}) — {r.Points:.0f} pts"
            for i, r in enumerate(standings.itertuples())
        ]
        return (
            f"Classificação de pilotos em {year}, considerando o campeonato até a etapa "
            f"mais recente:\n" + "\n".join(rows)
        )

    def championship_result(self, query: str, limit: int = 10) -> str | None:
        if not self._is_championship_result_question(query):
            return None

        year = self._championship_query_year(query)
        if year is None:
            return None

        season = self.sessions[self.sessions["Year"].eq(year)].copy()
        if season.empty:
            return f"Não encontrei dados do campeonato de {year}."

        if self._is_constructor_standings_question(query):
            standings = (
                season.groupby("TeamName", as_index=False)["Points"]
                .sum()
                .sort_values("Points", ascending=False)
                .head(limit)
            )
            champion = standings.iloc[0]
            rows = [
                f"{i + 1}. {row.TeamName} — {row.Points:.0f} pts"
                for i, row in enumerate(standings.itertuples())
            ]
            return (
                f"Resultado do campeonato de construtores de {year}: "
                f"a campeã foi a {champion.TeamName}, com {champion.Points:.0f} pontos.\n"
                + "\n".join(rows)
            )

        standings = (
            season.groupby(["FullName", "TeamName"], as_index=False)["Points"]
            .sum()
            .sort_values("Points", ascending=False)
            .head(limit)
        )
        champion = standings.iloc[0]
        rows = [
            f"{i + 1}. {row.FullName} ({row.TeamName}) — {row.Points:.0f} pts"
            for i, row in enumerate(standings.itertuples())
        ]
        return (
            f"Resultado do campeonato de pilotos de {year}: "
            f"o campeão foi {champion.FullName}, com {champion.Points:.0f} pontos.\n"
            + "\n".join(rows)
        )

    def recent_winners(self, limit: int = 5) -> str | None:
        races = self.sessions[self.sessions["Mode"].fillna("Race").eq("Race")].copy()
        winners = races[races["Position"] == 1.0].sort_values("Date").tail(limit)
        if winners.empty:
            return None

        rows = [
            f"{int(r.Year)} — {r.EventName}: {r.FullName} ({r.TeamName})"
            for r in winners.itertuples()
        ]
        return "Últimos vencedores:\n" + "\n".join(rows)

    def latest_race_winner(self) -> str | None:
        return self.race_result("quem venceu a última corrida")

    def race_result(self, query: str) -> str | None:
        driver_name = self._match_driver_name(query)
        result_type = self._race_result_type(query)
        if result_type is None and driver_name and self._has_race_reference(query):
            result_type = "driver"
        if result_type == "classification" and driver_name and self._asks_driver_race_result(query):
            result_type = "driver"
        if not result_type:
            return None

        race = self._resolve_race(query)
        if race is None:
            return None

        race_rows = (
            self.sessions[
                self.sessions["Mode"].fillna("Race").eq("Race")
                & self.sessions["Year"].eq(int(race.Year))
                & self.sessions["RoundNumber"].eq(int(race.RoundNumber))
            ]
            .copy()
            .dropna(subset=["Position"])
            .sort_values("Position")
        )
        if race_rows.empty:
            return None

        event_name = str(race.EventName)
        year = int(race.Year)

        if result_type == "driver":
            driver_row = race_rows[race_rows["FullName"].eq(driver_name)]
            if driver_row.empty:
                return f"Não encontrei {driver_name} no resultado do {event_name} de {year}."
            return self._format_driver_race_result(driver_row.iloc[0], event_name, year)

        if result_type == "position":
            position = self._extract_requested_position(query)
            if position is None:
                return None
            position_row = race_rows[race_rows["Position"].eq(float(position))]
            if position_row.empty:
                return f"Não encontrei {position}º colocado no {event_name} de {year}."
            row = position_row.iloc[0]
            return (
                f"No {event_name} de {year}, o {position}º colocado foi "
                f"{row.FullName}, pela {row.TeamName}. "
                f"Largou em {self._format_position(row.GridPosition)}, completou "
                f"{_format_number(row.Laps)} voltas, marcou {_format_number(row.Points)} ponto(s) "
                f"e teve status: {row.Status or 'não informado'}."
            )

        if result_type == "winner":
            winner = race_rows[race_rows["Position"].eq(1.0)]
            if winner.empty:
                return None
            winner = winner.iloc[0]
            if self._is_latest_race_reference(query):
                return (
                    f"A corrida mais recente foi o {event_name} de {year}. "
                    f"Quem venceu foi {winner.FullName}, pela equipe {winner.TeamName}."
                )
            return (
                f"No {event_name} de {year}, quem venceu foi {winner.FullName}, "
                f"pela equipe {winner.TeamName}."
            )

        if result_type == "classification":
            limit = self._classification_limit(query)
            rows = self._format_classification_rows(race_rows.head(limit))
            label = "classificação completa" if limit >= len(race_rows) else f"top {limit}"
            return f"{label.capitalize()} do {event_name} de {year}:\n" + "\n".join(rows)

        podium = race_rows[race_rows["Position"].isin([1.0, 2.0, 3.0])].head(3)
        if podium.empty:
            return None

        rows = self._format_classification_rows(podium)
        if self._is_latest_race_reference(query):
            return (
                f"O pódio da corrida mais recente, o {event_name} de {year}, foi:\n"
                + "\n".join(rows)
            )
        return f"O pódio do {event_name} de {year} foi:\n" + "\n".join(rows)

    @staticmethod
    def _format_position(value: object) -> str:
        if pd.isna(value):
            return "posição não informada"
        return f"{int(float(value))}º"

    def _format_driver_race_result(self, row: pd.Series, event_name: str, year: int) -> str:
        return (
            f"No {event_name} de {year}, {row.FullName} terminou em "
            f"{self._format_position(row.Position)} pela {row.TeamName}. "
            f"Largou em {self._format_position(row.GridPosition)}, completou "
            f"{_format_number(row.Laps)} voltas, marcou {_format_number(row.Points)} ponto(s) "
            f"e teve status: {row.Status or 'não informado'}."
        )

    @staticmethod
    def _format_classification_rows(rows: pd.DataFrame) -> list[str]:
        return [
            f"{int(row.Position)}. {row.FullName} ({row.TeamName}) — "
            f"{_format_number(row.Points)} pts, status: {row.Status or 'não informado'}"
            for row in rows.itertuples()
        ]

    @staticmethod
    def _classification_limit(query: str) -> int:
        normalized = _normalize_text(query)
        top_match = re.search(r"\btop\s*(\d{1,2})\b", normalized)
        if top_match:
            return max(1, min(int(top_match.group(1)), 30))
        if any(term in normalized for term in ["completo", "completa", "todos", "inteira", "inteiro"]):
            return 30
        return 10

    def driver_fact(self, query: str) -> str | None:
        if self._is_comparison_question(query):
            return None

        normalized = _normalize_text(query)
        driver_name = self._match_driver_name(query)
        if not driver_name:
            return None

        if self._has_race_reference(query):
            return None

        driver_rows = self.sessions[self.sessions["FullName"].eq(driver_name)].copy()
        if driver_rows.empty:
            return None

        race_rows = driver_rows[driver_rows["Mode"].fillna("Race").eq("Race")].copy()
        year = self._extract_year(normalized)
        scoped_races = race_rows[race_rows["Year"].eq(year)].copy() if year else race_rows
        if scoped_races.empty:
            return f"Não encontrei resultados de corrida para {driver_name}" + (f" em {year}." if year else ".")

        if any(term in normalized for term in ["vitoria", "venceu", "ganhou"]):
            wins = scoped_races[scoped_races["Position"].eq(1.0)].sort_values(["Date", "Year", "RoundNumber"])
            if any(term in normalized for term in ["quantas", "quantos", "total", "numero"]):
                scope = f" em {year}" if year else ""
                return f"{driver_name} tem {len(wins)} vitória(s){scope} na base local."
            if wins.empty:
                scope = f" em {year}" if year else ""
                return f"Não encontrei vitórias de {driver_name}{scope} na base local."

            row = wins.iloc[0] if "primeira" in normalized or "primeiro" in normalized else wins.iloc[-1]
            prefix = "A primeira vitória" if ("primeira" in normalized or "primeiro" in normalized) else "A última vitória"
            return (
                f"{prefix} de {driver_name} foi no {row.EventName} de {int(row.Year)}, "
                f"correndo pela {row.TeamName}."
            )

        if "podio" in normalized:
            podiums = scoped_races[scoped_races["Position"].le(3.0)].sort_values(["Date", "Year", "RoundNumber"])
            if any(term in normalized for term in ["quantas", "quantos", "total", "numero"]):
                scope = f" em {year}" if year else ""
                return f"{driver_name} tem {len(podiums)} pódio(s){scope} na base local."
            if podiums.empty:
                scope = f" em {year}" if year else ""
                return f"Não encontrei pódios de {driver_name}{scope} na base local."

            row = podiums.iloc[0] if "primeiro" in normalized or "primeira" in normalized else podiums.iloc[-1]
            prefix = "O primeiro pódio" if ("primeiro" in normalized or "primeira" in normalized) else "O último pódio"
            return (
                f"{prefix} de {driver_name} foi no {row.EventName} de {int(row.Year)}, "
                f"em {self._format_position(row.Position)}, pela {row.TeamName}."
            )

        if "pontos" in normalized or "pontuacao" in normalized or "pontuação" in normalized:
            points_rows = driver_rows[driver_rows["Year"].eq(year)].copy() if year else driver_rows
            points = float(points_rows["Points"].sum())
            scope = f" em {year}" if year else " na base local"
            return f"{driver_name} soma {_format_number(points)} ponto(s){scope}."

        if any(term in normalized for term in ["corridas", "gps", "largadas"]):
            entries = scoped_races[["Year", "RoundNumber"]].drop_duplicates().shape[0]
            scope = f" em {year}" if year else " na base local"
            return f"{driver_name} tem {entries} corrida(s){scope}."

        if any(term in normalized for term in ["melhor resultado", "melhor posicao", "melhor colocacao"]):
            best_position = scoped_races["Position"].min()
            best_rows = scoped_races[scoped_races["Position"].eq(best_position)].sort_values(["Date", "Year", "RoundNumber"])
            row = best_rows.iloc[0]
            return (
                f"O melhor resultado de {driver_name} foi {self._format_position(best_position)}. "
                f"Na base, a primeira ocorrência foi no {row.EventName} de {int(row.Year)}, "
                f"pela {row.TeamName}."
            )

        if self._is_latest_race_reference(normalized):
            row = scoped_races.sort_values(["Date", "Year", "RoundNumber"]).iloc[-1]
            return self._format_driver_race_result(row, str(row.EventName), int(row.Year))

        return None

    def driver_comparison(self, query: str) -> str | None:
        if not self._is_comparison_question(query):
            return None

        normalized = _normalize_text(query)
        drivers = self._match_driver_names(query)
        if len(drivers) < 2:
            return None

        stats = [self._driver_career_stats(driver) for driver in drivers[:3]]
        stats = [stat for stat in stats if stat]
        if len(stats) < 2:
            return None

        criterion_label = "indicadores objetivos"
        if "vitoria" in normalized:
            leader = max(stats, key=lambda item: item["wins"])
            criterion_label = "vitórias"
        elif "pontos" in normalized or "pontuacao" in normalized:
            leader = max(stats, key=lambda item: item["points"])
            criterion_label = "pontos"
        elif "podio" in normalized:
            leader = max(stats, key=lambda item: item["podiums"])
            criterion_label = "pódios"
        elif any(term in normalized for term in ["titulo", "titulos", "campeonato", "mundial"]):
            leader = max(stats, key=lambda item: item["championships"])
            criterion_label = "títulos"
        else:
            leader = max(
                stats,
                key=lambda item: (
                    item["championships"],
                    item["wins"],
                    item["podiums"],
                    item["points"],
                    item["races"],
                ),
            )
        rows = [
            (
                f"{item['driver']}: {item['championships']} título(s), "
                f"{item['wins']} vitória(s), {item['podiums']} pódio(s), "
                f"{_format_number(item['points'])} ponto(s), {item['races']} corrida(s)."
            )
            for item in stats
        ]
        if criterion_label == "indicadores objetivos":
            intro = (
                "Não existe um critério único para 'melhor'. Pelos indicadores objetivos da base local, "
                f"{leader['driver']} leva vantagem nesse recorte."
            )
        else:
            intro = f"Pelo critério de {criterion_label}, {leader['driver']} leva vantagem na base local."

        return intro + "\n" + "\n".join(rows)

    def _driver_career_stats(self, driver_name: str) -> dict | None:
        driver_rows = self.sessions[self.sessions["FullName"].eq(driver_name)].copy()
        if driver_rows.empty:
            return None

        races = driver_rows[driver_rows["Mode"].fillna("Race").eq("Race")].copy()
        championships = 0
        for year in sorted(self.sessions["Year"].dropna().unique()):
            if self._season_champion(int(year)) == driver_name:
                championships += 1

        return {
            "driver": driver_name,
            "championships": championships,
            "points": float(driver_rows["Points"].sum()),
            "races": int(races[["Year", "RoundNumber"]].drop_duplicates().shape[0]),
            "wins": int(races["Position"].eq(1.0).sum()),
            "podiums": int(races["Position"].le(3.0).sum()),
        }

    def driver_profile(self, query: str) -> str | None:
        driver_name = self._match_driver_name(query)
        if not driver_name:
            return None

        driver = self.sessions[self.sessions["FullName"].eq(driver_name)].copy()
        if driver.empty:
            return None

        driver = driver.sort_values(["Year", "RoundNumber", "Mode"])
        races = driver[driver["Mode"].eq("Race")].copy()
        classified_races = races[~races["DidNotStart"]].copy()
        latest_row = driver.sort_values("Date").dropna(subset=["Date"]).tail(1)
        if latest_row.empty:
            latest_row = driver.tail(1)
        latest = latest_row.iloc[0]

        first_year = int(driver["Year"].min())
        last_year = int(driver["Year"].max())
        latest_year = int(self.sessions["Year"].max())
        latest_team = str(latest.TeamName)
        total_points = float(driver["Points"].sum())
        race_count = int(classified_races[["Year", "RoundNumber"]].drop_duplicates().shape[0])
        wins = int((races["Position"] == 1).sum())
        podiums = int((races["Position"] <= 3).sum())
        best_finish = races["Position"].min()

        seasons = f"em {first_year}" if first_year == last_year else f"de {first_year} a {last_year}"
        best_finish_text = (
            f"{int(best_finish)}º lugar" if pd.notna(best_finish) else "sem resultado de corrida registrado"
        )

        current_points = 0.0
        standing_index = 0
        if last_year == latest_year:
            current_season = self.sessions[self.sessions["Year"].eq(latest_year)].copy()
            standings = (
                current_season.groupby(["FullName", "TeamName"], as_index=False)["Points"]
                .sum()
                .sort_values("Points", ascending=False)
                .reset_index(drop=True)
            )
            standing_row = standings[standings["FullName"].eq(driver_name)]
            if not standing_row.empty:
                standing_index = int(standing_row.index[0]) + 1
                current_points = float(standing_row.iloc[0]["Points"])

        achievements = []
        if wins:
            achievements.append(_plural(wins, "vitória", "vitórias"))
        if podiums:
            achievements.append(_plural(podiums, "pódio", "pódios"))
        if not achievements:
            achievements.append(f"melhor chegada em {best_finish_text}")

        achievement_text = ", ".join(achievements)
        total_points_text = _plural(total_points, "ponto", "pontos")
        race_count_text = _plural(race_count, "corrida", "corridas")
        current_points_text = _plural(current_points, "ponto", "pontos")
        if last_year == latest_year:
            if wins or podiums >= 10:
                return (
                    f"{driver_name} é um piloto de Fórmula 1 e atualmente corre pela {latest_team}. "
                    f"Na carreira, soma {total_points_text}, {race_count_text}, "
                    f"{achievement_text}. Em {latest_year}, tem {current_points_text} "
                    f"e está em {standing_index}º no campeonato de pilotos."
                )

            return (
                f"{driver_name} é um piloto de Fórmula 1 que atualmente corre pela {latest_team}. "
                f"Ele está no grid {seasons} e ainda está construindo sua trajetória "
                f"na categoria. Até aqui, tem {total_points_text}, {race_count_text} "
                f"e {achievement_text}. Em {latest_year}, soma {current_points_text} "
                f"e ocupa a {standing_index}ª posição no campeonato de pilotos."
            )

        if wins or podiums >= 10:
            return (
                f"{driver_name} foi um piloto de Fórmula 1 {seasons}. "
                f"Ele marcou época pela consistência e pelos resultados: {total_points_text}, "
                f"{race_count_text}, {achievement_text}. Sua equipe mais recente na categoria "
                f"foi {latest_team}."
            )

        return (
            f"{driver_name} foi um piloto de Fórmula 1 {seasons}. "
            f"Passou pela equipe {latest_team} no fim de sua passagem pela categoria e acumulou "
            f"{total_points_text} em {race_count_text}, com {achievement_text}."
        )

    def _predict_with_local_model(self) -> pd.DataFrame | None:
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.impute import SimpleImputer
            from sklearn.pipeline import Pipeline
        except Exception as err:
            print(f"[DATA] scikit-learn indisponível, usando tendência simples: {err}")
            return None

        latest_year = int(self.sessions["Year"].max())
        latest_round = int(self.sessions[self.sessions["Year"] == latest_year]["RoundNumber"].max())
        training, current, features = self._build_champion_abt(latest_year, latest_round)

        if training.empty or current.empty or training["Champion"].nunique() < 2:
            return None

        model = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="constant", fill_value=99)),
                (
                    "random_forest",
                    RandomForestClassifier(
                        n_estimators=300,
                        random_state=42,
                        min_samples_leaf=3,
                        class_weight="balanced",
                    ),
                ),
            ]
        )

        model.fit(training[features], training["Champion"])
        current = current.copy()
        current["ModelChampionProbability"] = model.predict_proba(current[features])[:, 1]
        current = self._apply_championship_reality_adjustment(
            current,
            current["ModelChampionProbability"],
        )
        return current.sort_values("ChampionProbability", ascending=False).reset_index(drop=True)

    def _predict_with_points_trend(self) -> pd.DataFrame:
        latest_year = int(self.sessions["Year"].max())
        latest_round = int(self.sessions[self.sessions["Year"] == latest_year]["RoundNumber"].max())
        current = self._driver_summary(latest_year, latest_round)
        current["RoundNumber"] = latest_round
        current["Year"] = latest_year
        current["Score"] = (
            current["Points"] * 1.0
            + current["Wins"] * 8.0
            + current["Podiums"] * 3.0
            + current["AvgPointsPerRound"] * 4.0
        )
        current["ModelChampionProbability"] = current["Score"]
        current = self._apply_championship_reality_adjustment(current, current["Score"])
        return current.sort_values("ChampionProbability", ascending=False).reset_index(drop=True)

    def _build_champion_abt(
        self,
        latest_year: int,
        latest_round: int,
    ) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
        years = sorted(y for y in self.sessions["Year"].unique() if y < latest_year)
        training_rows = []

        for year in years:
            if self.sessions[self.sessions["Year"] == year - 1].empty:
                continue

            year_rounds = sorted(self.sessions[self.sessions["Year"] == year]["RoundNumber"].unique())
            if not year_rounds:
                continue

            champion = self._season_champion(year)
            max_round = max(year_rounds)
            for round_number in year_rounds:
                summary = self._feature_table_for_round(year, int(round_number), max_round)
                if summary.empty:
                    continue
                summary["Champion"] = (summary["FullName"] == champion).astype(int)
                training_rows.append(summary)

        training = pd.concat(training_rows, ignore_index=True) if training_rows else pd.DataFrame()
        current = self._feature_table_for_round(latest_year, latest_round, latest_round)
        features = [
            "RoundNumber",
            "SeasonProgress",
            "Points",
            "AvgPointsPerRound",
            "Wins",
            "Podiums",
            "AvgFinish",
            "AvgGrid",
            "RaceEntries",
            "ClassifiedRaces",
            "FinishRate",
            "NonFinishRate",
            "DidNotFinish",
            "DidNotStart",
            "PointlessRaceRate",
            "PointsGapToLeader",
            "PointsShareOfLeader",
            "PrevPoints",
            "PrevWins",
            "PrevPodiums",
            "PrevAvgFinish",
            "PrevAvgGrid",
            "PrevFinishRate",
            "PrevNonFinishRate",
            "PrevPointlessRaceRate",
        ]
        return training, current, features

    def _feature_table_for_round(
        self,
        year: int,
        round_number: int,
        max_round: int,
    ) -> pd.DataFrame:
        current = self._driver_summary(year, round_number)
        previous = self._driver_summary(year - 1).rename(
            columns={
                "Points": "PrevPoints",
                "Wins": "PrevWins",
                "Podiums": "PrevPodiums",
                "AvgFinish": "PrevAvgFinish",
                "AvgGrid": "PrevAvgGrid",
                "FinishRate": "PrevFinishRate",
                "NonFinishRate": "PrevNonFinishRate",
                "PointlessRaceRate": "PrevPointlessRaceRate",
            }
        )
        previous = previous[
            [
                "FullName",
                "PrevPoints",
                "PrevWins",
                "PrevPodiums",
                "PrevAvgFinish",
                "PrevAvgGrid",
                "PrevFinishRate",
                "PrevNonFinishRate",
                "PrevPointlessRaceRate",
            ]
        ]

        features = current.merge(previous, on="FullName", how="left")
        features["RoundNumber"] = round_number
        features["Year"] = year
        features["SeasonProgress"] = round_number / max(max_round, 1)
        return features

    def _driver_summary(self, year: int, up_to_round: int | None = None) -> pd.DataFrame:
        season = self.sessions[self.sessions["Year"] == year].copy()
        if up_to_round is not None:
            season = season[season["RoundNumber"] <= up_to_round]

        if season.empty:
            return pd.DataFrame(
                columns=[
                    "FullName",
                    "TeamName",
                    "Points",
                    "AvgPointsPerRound",
                    "Wins",
                    "Podiums",
                    "AvgFinish",
                    "AvgGrid",
                    "RaceEntries",
                    "ClassifiedRaces",
                    "FinishRate",
                    "NonFinishRate",
                    "DidNotFinish",
                    "DidNotStart",
                    "PointlessRaceRate",
                    "PointsGapToLeader",
                    "PointsShareOfLeader",
                ]
            )

        races = season[season["Mode"].eq("Race")].copy()
        points = (
            season.groupby(["FullName", "TeamName"], as_index=False)
            .agg(Points=("Points", "sum"), Rounds=("RoundNumber", "nunique"))
        )

        race_stats = (
            races.groupby("FullName", as_index=False)
            .agg(
                RaceEntries=("RoundNumber", "nunique"),
                ClassifiedRaces=("IsClassified", "sum"),
                DidNotFinish=("DidNotFinish", "sum"),
                DidNotStart=("DidNotStart", "sum"),
                PointlessRaces=("Points", lambda s: (s <= 0).sum()),
                Wins=("Position", lambda s: (s == 1).sum()),
                Podiums=("Position", lambda s: (s <= 3).sum()),
                AvgFinish=("Position", "mean"),
                AvgGrid=("GridPosition", "mean"),
            )
        )

        summary = points.merge(race_stats, on="FullName", how="left")
        summary["AvgPointsPerRound"] = summary["Points"] / summary["Rounds"].clip(lower=1)
        for col in [
            "RaceEntries",
            "ClassifiedRaces",
            "DidNotFinish",
            "DidNotStart",
            "PointlessRaces",
            "Wins",
            "Podiums",
        ]:
            summary[col] = summary[col].fillna(0)
        race_entries = summary["RaceEntries"].clip(lower=1)
        summary["FinishRate"] = summary["ClassifiedRaces"] / race_entries
        summary["NonFinishRate"] = (summary["DidNotFinish"] + summary["DidNotStart"]) / race_entries
        summary["PointlessRaceRate"] = summary["PointlessRaces"] / race_entries
        leader_points = summary["Points"].max()
        if leader_points > 0:
            summary["PointsGapToLeader"] = leader_points - summary["Points"]
            summary["PointsShareOfLeader"] = summary["Points"] / leader_points
        else:
            summary["PointsGapToLeader"] = 0.0
            summary["PointsShareOfLeader"] = 0.0
        return summary.drop(columns=["Rounds", "PointlessRaces"])

    def _apply_championship_reality_adjustment(
        self,
        current: pd.DataFrame,
        raw_score: pd.Series,
    ) -> pd.DataFrame:
        current = current.copy()
        raw_strength = pd.to_numeric(raw_score, errors="coerce").fillna(0).clip(lower=0)
        raw_max = raw_strength.max()
        if raw_max > 0:
            raw_strength = raw_strength / raw_max

        points_strength = current["PointsShareOfLeader"].fillna(0).clip(lower=0, upper=1)
        max_avg_points = current["AvgPointsPerRound"].max()
        if max_avg_points > 0:
            pace_strength = (current["AvgPointsPerRound"] / max_avg_points).fillna(0).clip(0, 1)
        else:
            pace_strength = pd.Series(0.0, index=current.index)

        finish_strength = current["FinishRate"].fillna(0).clip(lower=0, upper=1)
        non_finish_rate = current["NonFinishRate"].fillna(0).clip(lower=0, upper=1)

        score = (
            raw_strength * 0.15
            + points_strength.pow(2) * 0.50
            + pace_strength * 0.20
            + finish_strength * 0.15
        )
        reliability_multiplier = (0.45 + finish_strength * 0.55) * (1 - non_finish_rate * 0.35)
        current["ChampionScore"] = score * reliability_multiplier

        score_sum = current["ChampionScore"].clip(lower=0).sum()
        if score_sum <= 0:
            current["ChampionProbability"] = 1 / len(current) if len(current) else 0.0
        else:
            current["ChampionProbability"] = current["ChampionScore"].clip(lower=0) / score_sum
        return current

    def _season_champion(self, year: int) -> str:
        standings = (
            self.sessions[self.sessions["Year"] == year]
            .groupby("FullName")["Points"]
            .sum()
            .sort_values(ascending=False)
        )
        return standings.index[0] if not standings.empty else ""

    def _match_driver_name(self, query: str) -> str | None:
        normalized_query = _normalize_text(query)
        query_tokens = set(re.findall(r"[a-z0-9]+", normalized_query))
        if not query_tokens:
            return None

        full_name_aliases = {
            "ayrton senna": "Ayrton Senna",
            "bruno senna": "Bruno Senna",
            "michael schumacher": "Michael Schumacher",
            "ralf schumacher": "Ralf Schumacher",
            "mick schumacher": "Mick Schumacher",
            "max verstappen": "Max Verstappen",
            "jos verstappen": "Jos Verstappen",
        }
        for alias, full_name in full_name_aliases.items():
            if alias in normalized_query:
                return full_name

        surname_aliases = {
            "senna": "Ayrton Senna",
            "schumacher": "Michael Schumacher",
        }
        for surname, full_name in surname_aliases.items():
            if surname in query_tokens:
                return full_name

        candidates = []
        driver_rows = (
            self.sessions[["FullName", "DriverId", "Abbreviation", "Year"]]
            .drop_duplicates()
            .dropna(subset=["FullName"])
        )

        for full_name, group in driver_rows.groupby("FullName"):
            full_name_norm = _normalize_text(full_name)
            name_parts = [part for part in full_name_norm.split() if len(part) >= 4]
            last_name = name_parts[-1] if name_parts else ""

            score = 0
            if full_name_norm and full_name_norm in normalized_query:
                score = max(score, 8)
            if last_name and last_name in query_tokens:
                score = max(score, 6)
            if last_name and any(SequenceMatcher(None, last_name, token).ratio() >= 0.88 for token in query_tokens):
                score = max(score, 5)
            if any(part in query_tokens for part in name_parts):
                score = max(score, 4)

            for row in group.itertuples():
                driver_id = _normalize_text(row.DriverId)
                abbreviation = _normalize_text(row.Abbreviation)
                if driver_id and (driver_id in normalized_query or driver_id in query_tokens):
                    driver_id_score = 7 if "_" in driver_id or " " in driver_id else 6
                    score = max(score, driver_id_score)
                if abbreviation and len(abbreviation) >= 3 and abbreviation in query_tokens:
                    score = max(score, 5)

            if score:
                candidates.append((score, int(group["Year"].max()), len(group), str(full_name)))

        if not candidates:
            return None

        candidates.sort(reverse=True)
        return candidates[0][3]

    def _match_driver_names(self, query: str) -> list[str]:
        normalized_query = _normalize_text(query)
        query_tokens = set(re.findall(r"[a-z0-9]+", normalized_query))
        if not query_tokens:
            return []

        matches = []
        canonical_surnames = {
            "verstappen": "Max Verstappen",
            "senna": "Ayrton Senna",
            "schumacher": "Michael Schumacher",
            "hamilton": "Lewis Hamilton",
            "leclerc": "Charles Leclerc",
            "alonso": "Fernando Alonso",
            "norris": "Lando Norris",
            "piastri": "Oscar Piastri",
            "russell": "George Russell",
            "perez": "Sergio Perez",
        }
        driver_rows = (
            self.sessions[["FullName", "DriverId", "Abbreviation", "Year"]]
            .drop_duplicates()
            .dropna(subset=["FullName"])
        )

        for full_name, group in driver_rows.groupby("FullName"):
            full_name = str(full_name)
            full_name_norm = _normalize_text(full_name)
            name_parts = [part for part in full_name_norm.split() if len(part) >= 4]
            last_name = name_parts[-1] if name_parts else ""
            canonical_name = canonical_surnames.get(last_name)
            if (
                canonical_name
                and last_name in query_tokens
                and full_name != canonical_name
                and full_name_norm not in normalized_query
            ):
                continue

            score = 0
            position = 10_000
            if full_name_norm and full_name_norm in normalized_query:
                score = max(score, 10)
                position = min(position, normalized_query.find(full_name_norm))

            if last_name and last_name in query_tokens:
                score = max(score, 8)
                position = min(position, normalized_query.find(last_name))

            if any(part in query_tokens for part in name_parts):
                score = max(score, 5)
                for part in name_parts:
                    if part in normalized_query:
                        position = min(position, normalized_query.find(part))

            if last_name:
                for token in query_tokens:
                    if SequenceMatcher(None, last_name, token).ratio() >= 0.88:
                        score = max(score, 6)
                        position = min(position, normalized_query.find(token))

            for row in group.itertuples():
                driver_id = _normalize_text(row.DriverId)
                abbreviation = _normalize_text(row.Abbreviation)
                if driver_id and (driver_id in normalized_query or driver_id in query_tokens):
                    score = max(score, 7)
                    position = min(position, normalized_query.find(driver_id))
                if abbreviation and len(abbreviation) >= 3 and abbreviation in query_tokens:
                    score = max(score, 6)
                    position = min(position, normalized_query.find(abbreviation))

            if score:
                matches.append((position, -score, -int(group["Year"].max()), full_name))

        matches.sort()
        ordered = []
        for _, _, _, full_name in matches:
            if full_name not in ordered:
                ordered.append(full_name)
        return ordered

    def _race_index(self) -> pd.DataFrame:
        races = self.sessions[self.sessions["Mode"].fillna("Race").eq("Race")].copy()
        if races.empty:
            return pd.DataFrame()

        columns = ["Year", "RoundNumber", "EventName", "Date"]
        return (
            races[columns]
            .sort_values(["Date", "Year", "RoundNumber"], na_position="last")
            .drop_duplicates(["Year", "RoundNumber"], keep="first")
            .reset_index(drop=True)
        )

    def _latest_race(self, races: pd.DataFrame) -> pd.Series | None:
        if races.empty:
            return None

        dated = races.dropna(subset=["Date"]).sort_values(["Date", "Year", "RoundNumber"])
        if not dated.empty:
            return dated.iloc[-1]

        return races.sort_values(["Year", "RoundNumber"]).iloc[-1]

    def _resolve_race(self, query: str) -> pd.Series | None:
        races = self._race_index()
        if races.empty:
            return None

        normalized = _normalize_text(query)
        year = self._extract_year(normalized)

        if self._is_latest_race_reference(normalized):
            scoped = races[races["Year"].eq(year)] if year else races
            return self._latest_race(scoped)

        round_match = re.search(r"\b(?:etapa|rodada|round)\s*(\d{1,2})\b", normalized)
        if round_match:
            round_number = int(round_match.group(1))
            scoped = races[races["RoundNumber"].eq(round_number)]
            if year:
                scoped = scoped[scoped["Year"].eq(year)]
            race = self._latest_race(scoped)
            if race is not None:
                return race

        query_tokens = _expanded_query_tokens(normalized)
        if not query_tokens:
            return None

        scoped = races[races["Year"].eq(year)].copy() if year else races.copy()
        if scoped.empty:
            return None

        scored = []
        for idx, row in scoped.iterrows():
            event_norm = _normalize_text(row.EventName)
            event_tokens = _significant_tokens(event_norm)
            if not event_tokens:
                continue

            score = 0.0
            if event_norm and event_norm in normalized:
                score += 100.0

            intersection = event_tokens & query_tokens
            score += len(intersection) * 25.0

            for event_token in event_tokens:
                for query_token in query_tokens:
                    ratio = SequenceMatcher(None, event_token, query_token).ratio()
                    shares_prefix = (
                        len(event_token) >= 5
                        and len(query_token) >= 5
                        and (event_token.startswith(query_token) or query_token.startswith(event_token))
                    )
                    if ratio >= 0.82 or shares_prefix:
                        score += 12.0
                        break

            if score >= 12.0:
                date_value = row.Date if pd.notna(row.Date) else pd.Timestamp.min
                scored.append((score, date_value, idx))

        if not scored:
            return None

        scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return scoped.loc[scored[0][2]]

    @staticmethod
    def _is_latest_race_reference(text: str) -> bool:
        normalized = _normalize_text(text)
        latest_terms = [
            "ultima corrida",
            "ultimo gp",
            "corrida mais recente",
            "gp mais recente",
            "corrida recente",
        ]
        return any(term in normalized for term in latest_terms)

    @staticmethod
    def _has_race_reference(text: str) -> bool:
        normalized = _normalize_text(text)
        if F1DataKnowledgeBase._is_latest_race_reference(normalized):
            return True
        if re.search(r"\b(?:gp|grand prix|corrida|etapa|rodada|round)\b", normalized):
            return True
        return any(alias in normalized for alias in _EVENT_ALIASES)

    @staticmethod
    def _asks_driver_race_result(text: str) -> bool:
        normalized = _normalize_text(text)
        return any(
            term in normalized
            for term in [
                "resultado",
                "posicao",
                "colocacao",
                "ficou",
                "terminou",
                "chegou",
                "pontos",
                "pontuacao",
                "grid",
                "largou",
                "status",
                "abandono",
                "voltas",
            ]
        )

    @staticmethod
    def _extract_requested_position(text: str) -> int | None:
        normalized = _normalize_text(text)
        ordinal_words = {
            "primeiro": 1,
            "primeira": 1,
            "segundo": 2,
            "segunda": 2,
            "terceiro": 3,
            "terceira": 3,
            "quarto": 4,
            "quarta": 4,
            "quinto": 5,
            "quinta": 5,
            "sexto": 6,
            "sexta": 6,
            "setimo": 7,
            "setima": 7,
            "oitavo": 8,
            "oitava": 8,
            "nono": 9,
            "nona": 9,
            "decimo": 10,
            "decima": 10,
        }
        for word, value in ordinal_words.items():
            if re.search(rf"\b{word}\b", normalized):
                return value

        patterns = [
            r"\bp\s*(\d{1,2})\b",
            r"\b(?:posicao|posição|colocacao|colocação|lugar)\s*(\d{1,2})\b",
            r"\b(\d{1,2})(?:o|a|º|ª)?\s*(?:colocado|colocada|lugar|posicao|posição)\b",
            r"\b(?:terminou|chegou|ficou)\s+em\s+(\d{1,2})(?:o|a|º|ª)?\b",
        ]
        for pattern in patterns:
            match = re.search(pattern, normalized)
            if match:
                value = int(match.group(1))
                if 1 <= value <= 30:
                    return value
        return None

    @staticmethod
    def _is_comparison_question(text: str) -> bool:
        normalized = _normalize_text(text)
        return any(
            term in f" {normalized} "
            for term in [
                " melhor ",
                " versus ",
                " vs ",
                " ou ",
                " compar",
                " maior ",
                " pior ",
                " mais vitoria",
                " mais pontos",
                " mais titulos",
                " mais podios",
            ]
        )

    @staticmethod
    def _race_result_type(query: str) -> str | None:
        normalized = _normalize_text(query)
        if F1DataKnowledgeBase._extract_requested_position(normalized) is not None:
            return "position"

        podium_terms = [
            "podio",
            "top 3",
            "top tres",
            "primeiros 3",
            "primeiros tres",
            "tres primeiros",
        ]
        if any(term in normalized for term in podium_terms):
            return "podium"

        winner_terms = ["quem ganhou", "quem venceu", "vencedor", "ganhador"]
        if any(term in normalized for term in winner_terms):
            return "winner"

        result_terms = [
            "resultado",
            "classificacao",
            "classificaçao",
            "classificação",
            "colocacao",
            "colocação",
            "posicao",
            "posição",
            "ordem",
            "ordem de chegada",
            "chegada",
            "top ",
        ]
        if any(term in normalized for term in result_terms):
            return "classification"

        return None

    @staticmethod
    def _is_latest_race_winner_question(text: str) -> bool:
        normalized = _normalize_text(text)
        winner_terms = ["quem ganhou", "quem venceu", "vencedor", "ganhador"]
        latest_terms = ["ultima corrida", "ultimo gp", "corrida mais recente", "gp mais recente"]
        return any(term in normalized for term in winner_terms) and any(
            term in normalized for term in latest_terms
        )

    @staticmethod
    def _is_driver_profile_question(text: str) -> bool:
        normalized = _normalize_text(text)
        comparison_terms = [
            "quem e melhor",
            "quem foi melhor",
            "melhor que",
            "versus",
            " vs ",
            " ou ",
            "compar",
            "maior que",
            "pior que",
        ]
        if any(term in f" {normalized} " for term in comparison_terms):
            return False

        profile_terms = [
            "quem e",
            "quem foi",
            "me fale sobre",
            "fale sobre",
            "conte sobre",
            "perfil de",
            "carreira de",
            "historia de",
        ]
        if any(term in normalized for term in profile_terms):
            return True

        tokens = re.findall(r"[a-z0-9]+", normalized)
        return 1 <= len(tokens) <= 3

    @staticmethod
    def _extract_year(text: str) -> int | None:
        match = re.search(r"\b(19\d{2}|20\d{2})\b", text)
        return int(match.group(1)) if match else None

    def _championship_query_year(self, text: str) -> int | None:
        normalized = _normalize_text(text)
        explicit_year = self._extract_year(normalized)
        if explicit_year is not None:
            return explicit_year

        latest_year = int(self.sessions["Year"].max())
        latest_completed_year = self._latest_completed_championship_year()
        latest_champion_terms = [
            "ultimo campeao",
            "ultima campea",
            "campeao atual",
            "campea atual",
            "atual campeao",
            "atual campea",
            "ultimo vencedor do campeonato",
            "ultimo campeao mundial",
        ]
        if any(term in normalized for term in latest_champion_terms):
            return latest_completed_year

        previous_terms = ["passado", "passada", "anterior"]
        season_terms = ["campeonato", "campeonanto", "temporada", "ano", "mundial"]
        if any(term in normalized for term in previous_terms) and any(
            term in normalized for term in season_terms
        ):
            return latest_completed_year

        current_terms = [
            "campeonato atual",
            "temporada atual",
            "este campeonato",
            "essa temporada",
            "temporada mais recente",
        ]
        if any(term in normalized for term in current_terms):
            return latest_year

        return None

    def _is_championship_result_question(self, text: str) -> bool:
        normalized = _normalize_text(text)
        if self._extract_year(normalized) is not None and any(
            term in normalized for term in ["campeao", "campea", "titulo", "título"]
        ):
            return True

        latest_champion_terms = [
            "ultimo campeao",
            "ultima campea",
            "campeao atual",
            "campea atual",
            "atual campeao",
            "atual campea",
        ]
        if any(term in normalized for term in latest_champion_terms):
            return True

        championship_terms = ["campeonato", "campeonanto", "temporada", "mundial"]
        result_terms = [
            "resultado",
            "classificacao",
            "pontuacao",
            "tabela",
            "standings",
            "quem ganhou",
            "quem venceu",
            "campeao",
            "vencedor",
        ]
        return (
            any(term in normalized for term in championship_terms)
            and any(term in normalized for term in result_terms)
            and self._championship_query_year(normalized) is not None
        )

    def _latest_completed_championship_year(self) -> int:
        races = self.sessions[self.sessions["Mode"].fillna("Race").eq("Race")]
        race_counts = races.groupby("Year")["RoundNumber"].nunique().sort_index()
        if race_counts.empty:
            return int(self.sessions["Year"].max())

        latest_year = int(race_counts.index[-1])
        if len(race_counts) == 1:
            return latest_year

        previous_year = int(race_counts.index[-2])
        latest_count = int(race_counts.iloc[-1])
        previous_count = int(race_counts.iloc[-2])
        minimum_complete_count = max(10, int(previous_count * 0.75))

        if latest_count < minimum_complete_count:
            return previous_year

        return latest_year

    @staticmethod
    def _is_constructor_standings_question(text: str) -> bool:
        normalized = _normalize_text(text)
        return any(
            term in normalized
            for term in ["construtores", "equipes", "times", "escuderias"]
        )

    @staticmethod
    def _is_prediction_question(text: str) -> bool:
        prediction_terms = ["prever", "previs", "projet", "palpite", "quem vai", "favorito"]
        title_terms = ["campe", "titulo", "título", "campeonato de pilotos"]
        return any(term in text for term in prediction_terms) and any(
            term in text for term in title_terms
        )

    @staticmethod
    def _is_standings_question(text: str) -> bool:
        terms = ["classificacao", "classificação", "pontuacao", "pontuação", "tabela"]
        championship_terms = ["pilotos", "campeonato", "temporada", "ranking"]
        return any(term in text for term in terms) and any(
            term in text for term in championship_terms
        )

    @staticmethod
    def _is_recent_winners_question(text: str) -> bool:
        return (
            any(term in text for term in ["ultimos vencedores", "últimos vencedores", "vencedores recentes"])
            or ("quem venceu" in text and "recent" in text)
        )

    @staticmethod
    def _prediction_confidence(
        latest_round: int,
        leader_probability: float,
        gap: float,
    ) -> str:
        if latest_round <= 5:
            return "cautelosa"
        if leader_probability >= 0.6 and gap >= 0.2:
            return "alta"
        if leader_probability >= 0.4 or gap >= 0.12:
            return "média"
        return "baixa"


def build_data_context() -> str:
    return F1DataKnowledgeBase().context


def build_knowledge_base() -> F1DataKnowledgeBase:
    return F1DataKnowledgeBase()
