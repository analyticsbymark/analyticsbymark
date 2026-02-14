import requests
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date, timedelta

import pandas as pd
from urllib.parse import urljoin
from pydantic_settings import BaseSettings
from pydantic import computed_field, HttpUrl
from sqlmodel import SQLModel, Field, Session, create_engine, select, delete

class LL2Settings(BaseSettings):
    """
    Launch Library 2 (DEV) config.
    """

    # --- Core ---
    BASE_URL: HttpUrl = Field(
        default="https://ll.thespacedevs.com/2.3.0",  # DEV: https://lldev.thespacedevs.com/2.3.0 no rate limits
        description="LL2 DEV base URL",
    )
    TIMEOUT_S: int = 30
    USER_AGENT: str = "LL2Client/1.0 (ABM)"
    DEFAULT_LIMIT: int = 100

    # --- Endpoints (relative paths) ---
    EP_LAUNCHES: str = "/launches/"
    EP_AGENCIES: str = "/agencies/"
    EP_ASTRONAUTS: str = "/astronauts/"
    EP_PADS: str = "/pads/"
    EP_PAYLOADS: str = "/payloads/"
    EP_LAUNCHER_CONFIGS: str = "/launcher_configurations/"
    EP_MISSIONS: str = "/mission/"
    EP_EVENTS: str = "/event/"
    EP_LOCATIONS: str = "/location/"
    EP_STATIONS: str = "/spacestation/"

    def abs(self, path_or_url: str) -> str:
        """Make an absolute URL from a relative endpoint or passthrough if absolute."""
        if path_or_url.startswith(("http://", "https://")):
            return path_or_url
        return urljoin(str(self.BASE_URL).rstrip("/") + "/", path_or_url.lstrip("/"))


class LL2Client:
    """
    Simple Launch Library 2 client.
    - Uses LL2Settings for base URL and defaults
    - Follows pagination via 'next'
    - Supports an optional 'n_items' to return only the first N items
    """

    def __init__(self, settings):
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.settings.USER_AGENT,
            "Accept": "application/json",
        })

    def get_results(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        results_key: str = "results",
        n_items: Optional[int] = None,  # 🆕 limit for total items, not per-page
    ) -> List[Dict[str, Any]]:
        """
        Fetch results from a paginated endpoint.

        Args:
            endpoint: Relative path like '/launches/' or absolute URL.
            params: Query params (e.g., {'ordering': '-net'}).
            results_key: Key that holds items in the response ('results').
            n_items: Optional max number of total results to return.

        Returns:
            List of items (up to 'n_items' if provided).
        """
        url = self.settings.abs(endpoint)
        params = dict(params or {})
        params.setdefault("limit", self.settings.DEFAULT_LIMIT)

        all_items: List[Dict[str, Any]] = []
        print(url)
        print(params)
        # 1️⃣ First page
        resp = self.session.get(url, params=params, timeout=self.settings.TIMEOUT_S)
        resp.raise_for_status()
        data = resp.json()
        all_items.extend(data.get(results_key, []))
        next_url = data.get("next")

        # 2️⃣ Follow pagination
        while next_url:
            resp = self.session.get(next_url, timeout=self.settings.TIMEOUT_S)
            resp.raise_for_status()
            data = resp.json()
            all_items.extend(data.get(results_key, []))
            next_url = data.get("next")

            # 3️⃣ Stop early if we already hit the limit
            if n_items and len(all_items) >= n_items:
                return all_items[:n_items]

        return all_items



class LaunchData(SQLModel):
    name: str
    status: str
    window_start: datetime
    window_end: datetime
    image_thumbnail: Optional[str]
    mission_type: Optional[str]
    mission_description: Optional[str]
    agency_name: Optional[str]
    agency_country: Optional[str]
    agency_logo: Optional[str]
    launchpad_location_name: Optional[str]
    launchpad_country: Optional[str]

    @computed_field
    @property
    def window_month(self) -> int:
        return self.window_start.month

    @computed_field
    @property
    def window_month_short(self) -> str:
        return self.window_start.strftime("%b")

    @computed_field
    @property
    def window_month_year_short(self) -> str:
        return self.window_start.strftime("%b-%Y")

    @computed_field
    @property
    def window_year(self) -> int:
        return self.window_start.year


class AgencyLaunchData(SQLModel):
    # --- Identity (strongly recommended) ---
    launch_uuid: Optional[str] = Field(default=None, index=True)   # API "id" (UUID string)
    launch_url: Optional[str] = None

    # --- Timing ---
    net: Optional[datetime] = Field(default=None, index=True)      # best for time series
    window_start: Optional[datetime] = None
    window_end: Optional[datetime] = None
    last_updated: Optional[datetime] = None

    # --- Launch status ---
    launch_name: str
    launch_status: Optional[str] = None
    launch_status_id: Optional[int] = None
    launch_status_abbrev: Optional[str] = None
    launch_status_description: Optional[str] = None

    # --- Operator (who launched the rocket) ---
    operator_id: Optional[int] = Field(default=None, index=True)   # launch_service_provider.id
    operator_name: Optional[str] = Field(default=None, index=True) # launch_service_provider.name

    # --- Mission identity ---
    mission_id: Optional[int] = Field(default=None, index=True)

    # --- Mission ---
    mission_name: Optional[str] = None
    mission_type: Optional[str] = None
    mission_description: Optional[str] = None

    # --- Mission owner(s) (who owns/sponsors the mission) ---
    mission_owner_primary_id: Optional[int] = Field(default=None, index=True)
    mission_owner_primary_name: Optional[str] = Field(default=None, index=True)

    # Store all owners as a delimited string for easy filtering/grouping in BI
    mission_owner_all_ids: Optional[str] = None      # e.g. "44;161;121"
    mission_owner_all_names: Optional[str] = None    # e.g. "NASA;USAF;ESA"

    # --- Program(s) (useful for Starlink, Crew, etc.) ---
    program_names: Optional[str] = None              # e.g. "Starlink;Commercial Crew"

    # --- Media ---
    image_thumbnail: Optional[str] = None

    # --- Rocket ---
    rocket_full_name: Optional[str] = None
    rocket_variant: Optional[str] = None
    rocket_name: Optional[str] = None
    rocket_family: Optional[str] = None

    # --- Launchpad ---
    launchpad_id: Optional[int] = Field(default=None, index=True)
    launchpad_name: Optional[str] = None
    launchpad_description: Optional[str] = None
    launchpad_map_url: Optional[str] = None
    launchpad_latitude: Optional[float] = None
    launchpad_longitude: Optional[float] = None
    launchpad_location_name: Optional[str] = None
    launchpad_country: Optional[str] = None


class AgencyLaunchDataWrite(AgencyLaunchData, table=True):
    __tablename__ = 'agency_launch_data'

    id: Optional[int] = Field(default=None, primary_key=True)


class LaunchDataWrite(LaunchData, table=True):
    __tablename__ = 'launch_data'

    id: Optional[int] = Field(default=None, primary_key=True)

class LaunchesByMonthAndYear(SQLModel):
    window_month: int
    window_year: int
    window_month_short: str
    window_month_year_short : str
    launch_count: int

class LaunchesByMonthAndYearWrite(LaunchesByMonthAndYear, table=True):
    __tablename__ = 'launches_by_month_year'

    id: Optional[int] = Field(default=None, primary_key=True)


class AstronautData(SQLModel):
    astronaut_id: int
    name: str
    bio: Optional[str] = None
    age: Optional[int] = None
    date_of_birth: Optional[date] = None
    date_of_death: Optional[date] = None
    image_url: Optional[str] = None
    nationality: Optional[str] = None
    status: Optional[str] = None
    agency: Optional[str] = None
    type: Optional[str] = None
    first_flight: Optional[datetime] = None
    last_flight: Optional[datetime] = None
    in_space: Optional[bool] = None
    eva_time: Optional[timedelta] = None
    time_in_space: Optional[timedelta] = None
    flights_count: Optional[int] = None
    landings_count: Optional[int] = None
    spacewalks_count: Optional[int] = None

    # @computed_field
    # @property
    # def time_in_space_days(self) -> Optional[float]:
    #     if self.time_in_space_seconds is None:
    #         return None
    #     return self.time_in_space_seconds / 86400


class AstronautDataWrite(AstronautData, table=True):
    __tablename__ = "astronaut_data"
    id: Optional[int] = Field(default=None, primary_key=True)


class AgencyData(SQLModel):
    agency_id: int
    name: str
    type: Optional[str] = None
    abbrev: Optional[str] = None
    description: Optional[str] = None
    founding_year: Optional[int] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    logo_url: Optional[str] = None
    total_launch_count: Optional[int] = None
    consecutive_successful_launches: Optional[int] = None
    successful_launches: Optional[int] = None
    failed_launches: Optional[int] = None
    pending_launches: Optional[int] = None

class AgencyDataWrite(AgencyData, table=True):
    __tablename__ = "agency_data"
    id: Optional[int] = Field(default=None, primary_key=True)


sqlite_file_name = "database.db"

sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)


settings = LL2Settings()
client = LL2Client(settings)

# Request from API: 100 per page (DEFAULT_LIMIT)
# Stop after fetching 300 total launches across pages
launch_params = {"ordering": "-net", "net__lte": "2026-01-01T00:00:00Z"}

def safe_get(obj, *keys, default=None):
    """
    Safely get nested keys from a dict or list.
    Example:
        safe_get(launch, "mission", "agencies", 0, "name")
    """
    current = obj
    for key in keys:
        if current is None:
            return default

        if isinstance(key, int):  # list index
            if isinstance(current, list) and len(current) > key:
                current = current[key]
            else:
                return default
        else:  # dict key
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default

    return current

def extract_operator(launch_dict: dict) -> Tuple[Optional[int], Optional[str]]:
    return (
        safe_get(launch_dict, "launch_service_provider", "id"),
        safe_get(launch_dict, "launch_service_provider", "name"),
    )


def extract_mission_owners(launch_dict: dict) -> List[Dict]:
    """De-duped by agency id, preserving order."""
    agencies: List[Dict] = []

    # 1) mission.agencies
    mission_agencies = safe_get(launch_dict, "mission", "agencies", default=[]) or []
    if isinstance(mission_agencies, list):
        agencies.extend([a for a in mission_agencies if isinstance(a, dict)])

    # 2) program[].agencies
    programs = safe_get(launch_dict, "program", default=[]) or []
    if isinstance(programs, list):
        for p in programs:
            prog_agencies = safe_get(p, "agencies", default=[]) or []
            if isinstance(prog_agencies, list):
                agencies.extend([a for a in prog_agencies if isinstance(a, dict)])

    # de-dupe by id (fallback to name if id missing)
    seen = set()
    out: List[Dict] = []
    for a in agencies:
        key = safe_get(a, "id") or safe_get(a, "name")
        if key and key not in seen:
            seen.add(key)
            out.append(a)

    return out


def extract_program_names(launch_dict: dict) -> Optional[str]:
    programs = safe_get(launch_dict, "program", default=[]) or []
    if not isinstance(programs, list) or not programs:
        return None

    names = [safe_get(p, "name") for p in programs if safe_get(p, "name")]
    if not names:
        return None

    # de-dupe preserve order
    seen = set()
    deduped = []
    for n in names:
        if n not in seen:
            seen.add(n)
            deduped.append(n)

    return "; ".join(deduped)


def get_launch_data(client: LL2Client, params: Optional[dict] = None):

    if params is None:
        params = {"ordering": "net", "net__gte": "2026-01-01T00:00:00Z"}

    launch_data = client.get_results(settings.EP_LAUNCHES, params=params)

    data = []

    for launch_dict in launch_data:
        launch = LaunchData(
            name=safe_get(launch_dict, "name"),
            status=safe_get(launch_dict, "status", "name"),
            window_start=safe_get(launch_dict, "window_start"),
            window_end=safe_get(launch_dict, "window_end"),
            image_thumbnail=safe_get(launch_dict, "image", "thumbnail_url"),
            mission_type=safe_get(launch_dict, "mission", "type"),
            mission_description=safe_get(launch_dict, "mission", "description"),

            agency_name=safe_get(launch_dict, "mission", "agencies", 0, "name"),
            agency_country=safe_get(launch_dict, "mission", "agencies", 0, "country_code"),
            agency_logo=safe_get(launch_dict, "mission", "agencies", 0, "image", "logo_url"),

            launchpad_location_name=safe_get(launch_dict, "pad", "location", "name"),
            launchpad_country=safe_get(launch_dict, "pad", "country_code"),
        )

        data.append(launch)

    return data


def get_agency_launch_data(client: LL2Client, params: Optional[dict] = None):

    if params is None:
        params = {"ordering": "-net", "lsp__id": 121}

    launch_data = client.get_results(settings.EP_LAUNCHES, params=params)

    data = []

    for launch_dict in launch_data:
        operator_id, operator_name = extract_operator(launch_dict)

        owners = extract_mission_owners(launch_dict)
        primary_owner = owners[0] if owners else None

        # Build delimited strings (safe even if ids are missing)
        owner_ids = [str(safe_get(a, "id")) for a in owners if safe_get(a, "id") is not None]
        owner_names = [safe_get(a, "name") for a in owners if safe_get(a, "name")]

        launch = AgencyLaunchData(
            # --- identity ---
            launch_uuid=safe_get(launch_dict, "id"),
            launch_url=safe_get(launch_dict, "url"),

            # --- timing ---
            net=safe_get(launch_dict, "net"),
            window_start=safe_get(launch_dict, "window_start"),
            window_end=safe_get(launch_dict, "window_end"),
            last_updated=safe_get(launch_dict, "last_updated"),

            # --- status / label ---
            launch_name=safe_get(launch_dict, "name"),
            launch_status=safe_get(launch_dict, "status", "name"),
            launch_status_id=safe_get(launch_dict, "status", "id"),
            launch_status_abbrev=safe_get(launch_dict, "status", "abbrev"),
            launch_status_description=safe_get(launch_dict, "status", "description"),

            # --- operator ---
            operator_id=operator_id,
            operator_name=operator_name,

            # --- mission ---
            mission_id=safe_get(launch_dict, "mission", "id"),
            mission_name=safe_get(launch_dict, "mission", "name"),
            mission_type=safe_get(launch_dict, "mission", "type"),
            mission_description=safe_get(launch_dict, "mission", "description"),

            # --- mission owners ---
            mission_owner_primary_id=safe_get(primary_owner, "id") if primary_owner else None,
            mission_owner_primary_name=safe_get(primary_owner, "name") if primary_owner else  None,
            mission_owner_all_ids=";".join(owner_ids) if owner_ids else None,
            mission_owner_all_names=";".join(owner_names) if owner_names else None,

            # --- programs ---
            program_names=extract_program_names(launch_dict),

            # --- media ---
            image_thumbnail=safe_get(launch_dict, "image", "thumbnail_url"),

            # --- rocket ---
            rocket_full_name=safe_get(launch_dict, "rocket", "configuration", "full_name"),
            rocket_variant=safe_get(launch_dict, "rocket", "configuration", "variant"),
            rocket_name=safe_get(launch_dict, "rocket", "configuration", "name"),
            rocket_family=safe_get(launch_dict, "rocket", "configuration", "families", 0, "name"),

            # --- launchpad ---
            launchpad_name=safe_get(launch_dict, "pad", "name"),
            launchpad_id=safe_get(launch_dict, "pad", "id"),
            launchpad_description=safe_get(launch_dict, "pad", "description"),
            launchpad_map_url=safe_get(launch_dict, "pad", "map_url"),
            launchpad_latitude=safe_get(launch_dict, "pad", "latitude"),
            launchpad_longitude=safe_get(launch_dict, "pad", "longitude"),
            launchpad_location_name=safe_get(launch_dict, "pad", "location", "name"),
            launchpad_country=safe_get(launch_dict, "pad", "country", "alpha_3_code"),
        )

        data.append(launch)

    return data


def get_astronaut_data(client: LL2Client, params: Optional[dict] = None) -> list[AstronautData]:
    if params is None:
        # order by time in space descending, just as an interesting default
        params = {"ordering": "-time_in_space", "mode": "detailed"}

    raw_astronauts = client.get_results(settings.EP_ASTRONAUTS, params=params, n_items=300)

    data: list[AstronautData] = []

    for astro_dict in raw_astronauts:
        astronaut = AstronautData(
            astronaut_id=safe_get(astro_dict, "id"),
            name=safe_get(astro_dict, "name"),
            bio=safe_get(astro_dict, "bio"),
            age=safe_get(astro_dict, "age"),
            date_of_birth=safe_get(astro_dict, "date_of_birth"),
            date_of_death=safe_get(astro_dict, "date_of_death"),
            image_url=safe_get(astro_dict, "image", "image_url"),
            nationality=safe_get(astro_dict, "nationality", 0, "name"),
            status=safe_get(astro_dict, "status", "name"),
            agency=safe_get(astro_dict, "agency", "name"),
            type=safe_get(astro_dict, "type", "name"),
            first_flight=safe_get(astro_dict, "first_flight"),
            last_flight=safe_get(astro_dict, "last_flight"),
            in_space=safe_get(astro_dict, "in_space"),
            eva_time=safe_get(astro_dict, "eva_time"),
            time_in_space=safe_get(astro_dict, "time_in_space"),
            flights_count=safe_get(astro_dict, "flights_count"),
            landings_count=safe_get(astro_dict, "landings_count"),
            spacewalks_count=safe_get(astro_dict, "spacewalks_count")
        )
        data.append(astronaut)

    return data

def get_agency_data(client: LL2Client, params: Optional[dict] = None) -> list[AgencyData]:
    if params is None:
        params = {"ordering": "-total_launch_count", "mode": "detailed"}

    raw = client.get_results(settings.EP_AGENCIES, params=params, n_items=200)

    data: list[AgencyData] = []

    for a in raw:
        agency = AgencyData(
            agency_id=safe_get(a, "id"),
            name=safe_get(a, "name"),
            type=safe_get(a, "type", "name"),
            abbrev=safe_get(a, "abbrev"),
            description=safe_get(a, "description"),
            founding_year=safe_get(a, "founding_year"),
            country=safe_get(a , "country", 0, "name"),
            country_code=safe_get(a, "country", 0, "alpha_2_code"),
            logo_url=safe_get(a, "logo", "thumbnail_url"),
            total_launch_count=safe_get(a, "total_launch_count"),
            consecutive_successful_launches=safe_get(a, "consecutive_successful_launches"),
            successful_launches=safe_get(a, "successful_launches"),
            failed_launches=safe_get(a, "failed_launches"),
            pending_launches=safe_get(a, "pending_launches")
        )

        data.append(agency)

    return data

def create_tables():
    SQLModel.metadata.create_all(engine)

def truncate_tables():
    tables = [
        LaunchDataWrite,
        AgencyDataWrite,
        AstronautDataWrite,
        AgencyLaunchDataWrite
        # add more as needed
    ]

    with Session(engine) as session:
        for table in tables:
            session.exec(delete(table))
        session.commit()


def add_launches(launch_data: list[LaunchData]):
    with Session(engine) as session:
        for launch in launch_data:
            session.add(LaunchDataWrite(**launch.model_dump()))
        session.commit()

def add_agency_launches(launch_data: list[AgencyLaunchData]):
    with Session(engine) as session:
        for launch in launch_data:
            session.add(AgencyLaunchDataWrite(**launch.model_dump()))
        session.commit()

def select_launches():
    with Session(engine) as session:
        query = select(LaunchDataWrite)
        launches = session.exec(query).all()
        return launches

def select_launches_by_month_and_year():

    data = select_launches()

    launch_df = pd.DataFrame([x.model_dump() for x in data])

    launch_by_month = launch_df.groupby(['window_year', 'window_month', 'window_month_year_short', 'window_month_short'])['id'].count().reset_index().rename({'id': 'launch_count'}, axis=1)
    launch_by_month_objs = [LaunchesByMonthAndYear(**row) for row in launch_by_month.to_dict('records')]

    return launch_by_month_objs

def select_launches_by_month_and_year():

    data = select_launches()

    launch_df = pd.DataFrame([x.model_dump() for x in data])

    launch_by_month = launch_df.groupby(['window_year', 'window_month', 'window_month_year_short', 'window_month_short'])['id'].count().reset_index().rename({'id': 'launch_count'}, axis=1)
    launch_by_month_objs = [LaunchesByMonthAndYear(**row) for row in launch_by_month.to_dict('records')]

    return launch_by_month_objs



def add_launches_by_month_and_year():
    launches_by_month = select_launches_by_month_and_year()

    with Session(engine) as session:
        for month in launches_by_month:
            session.add(LaunchesByMonthAndYearWrite(**month.model_dump()))
        session.commit()

def add_astronauts(astronaut_data: list[AstronautData]):
    with Session(engine) as session:
        for astro in astronaut_data:
            session.add(AstronautDataWrite(**astro.model_dump()))
        session.commit()

def select_astronauts() -> list[AstronautDataWrite]:
    with Session(engine) as session:
        return session.exec(select(AstronautDataWrite)).all()

def add_agencies(agency_data: list[AgencyData]):
    with Session(engine) as session:
        for agency in agency_data:
            session.add(AgencyDataWrite(**agency.model_dump()))
        session.commit()

def select_agencies() -> list[AgencyDataWrite]:
    with Session(engine) as session:
        return session.exec(select(AgencyDataWrite)).all()



if __name__ == "__main__":

    create_tables()

    # truncate_tables()

    # launch_data = get_launch_data(client=client, params=launch_params)
    # add_launches(launch_data=launch_data)
    # add_launches_by_month_and_year()

    #Agency Launch Data
    # agency_launch_data = get_agency_launch_data(client=client)
    # add_agency_launches(launch_data=agency_launch_data)
    #
    # # Agencies
    # agencies = get_agency_data(client=client)
    # add_agencies(agency_data=agencies)
    #
    # #Astronauts
    # astronauts = get_astronaut_data(client=client)
    # add_astronauts(astronaut_data=astronauts)




